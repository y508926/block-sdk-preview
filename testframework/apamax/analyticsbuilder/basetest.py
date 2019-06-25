#!/usr/bin/env python
# Copyright (c) 2019 Software AG, Darmstadt, Germany and/or Software AG USA Inc., Reston, VA, USA, and/or its subsidiaries and/or its affiliates and/or their licensors.
# Use, reproduction, transfer, publication or disclosure is prohibited except as specifically provided for in your License Agreement with Software AG

from pysys.constants import *
from pysys.basetest import BaseTest
from apama.correlator import CorrelatorHelper
from apama.basetest import ApamaBaseTest
import os, zipfile, json
from pathlib import Path

class Waiter:
	def __init__(self, parent, corr, channels=[]):
		self.parent = parent
		self.corr = corr
		self.stdouterr = self.parent.allocateUniqueStdOutErr('waiter')

		corr.receive(self.stdouterr[0], channels=channels)
	def waitFor(self, expr, count=5):
		self.corr.flush(count=count)
		self.parent.waitForSignal(self.stdouterr[0], expr=expr)

class AnalyticsBuilderBaseTest(ApamaBaseTest):
	"""
	Base test for Analytics Builder tests.

	Requires the following to be set on the project in pysysproject (typically from the environment):
	PAB_SDK
	APAMA_HOME
	"""

	def __init__(self, descriptor, outsubdir, runner, **kwargs):
		super(AnalyticsBuilderBaseTest, self).__init__(descriptor, outsubdir, runner, **kwargs)
		self.modelId=0
		self.IS_WINDOWS = OSFAMILY=='windows'

	def runAnalyticsBuilderScript(self, args=[], environs={}, **kwargs):
		"""
		Run the analytics_builder script.
		:param args: the arguments to pass to the script
		:param environs: any environment overrides.
		:param kwargs: any arguments to pass through to startProcess
		:return: The process handle of the process (L{ProcessWrapper}).
		"""
		env = dict(os.environ)
		env['PYTHONDONTWRITEBYTECODE'] = 'true'  # .pyc optimizations not needed and make it harder to delete things later
		if environs: env.update(environs)
		script = 'analytics_builder'
		stdouterr = self.allocateUniqueStdOutErr(script)

		try:
			return self.startProcess(f'{self.project.PAB_SDK}/{script}'+('.cmd' if self.IS_WINDOWS else ''), args,
				stdout=stdouterr[0], stderr=stdouterr[1],
				displayName=script, environs=env, **kwargs)
		except Exception:
			self.logFileContents(stdouterr[1]) or self.logFileContents(stdouterr[0])
			raise


	def startAnalyticsBuilderCorrelator(self, blockSourceDir=None, Xclock=True, **kwargs):
		"""
		Start a Correlator with Analytics Builder EPL loaded.
		:param blockSourceDir: a location of blocks to include
		:param Xclock: externally clock correlator (on by default)
		"""

		# Build and extract the block extension:
		if blockSourceDir == None: blockSourceDir = self.input
		blockOutput = self.output+'/block-output.zip'
		self.runAnalyticsBuilderScript(['build', 'extension', '--input', blockSourceDir, '--output', blockOutput])
		with zipfile.ZipFile(blockOutput, 'r') as zf:
			blockOutput = Path(self.output + '/block-output/')
			os.mkdir(blockOutput)
			zf.extractall(blockOutput)

		# start the correlator:
		corr = CorrelatorHelper(self)
		arguments=kwargs.get('arguments', [])
		arguments.append('-DanalyticsBuilder.numWorkerThreads=3')
		kwargs['arguments']=arguments
		corr.start(Xclock=Xclock, **kwargs)
		corr.injectEPL([self.project.APAMA_HOME+'/monitors/'+i+'.mon' for i in ['ScenarioService', 'data_storage/MemoryStore', 'JSONPlugin', 'AnyExtractor', 'ManagementImpl', 'Management', 'ConnectivityPluginsControl', 'ConnectivityPlugins', 'HTTPClientEvents', 'AutomaticOnApplicationInitialized']])
		corr.injectCDP(self.project.PAB_SDK+'/block-api/framework/analyticsbuilder-framework.cdp')
		corr.injectEPL(self.project.PAB_SDK+'/testframework/resources/TestHelpers.mon')

		# inject block files:
		corr.injectEPL(sorted(list(blockOutput.rglob('*.mon'))))
		corr.send(sorted(list(blockOutput.rglob('*.evt'))))

		# now done
		corr.sendEventStrings('com.apama.connectivity.ApplicationInitialized()')
		corr.flush(10)
		self.analyticsBuilderCorrelator = corr
		corr.receive('output.evt', channels=['TestOutput'])
		return corr


	def createTestModel(self, blockUnderTest, parameters={}, id=None, corr=None, inputs={}):
		"""
		Create a test model.

		A test model tests a blockUnderTest and connects generic inputs and outputs to its block input/ outputs.
		:param blockUnderTest: Fully qualified name of the block to test (including package name)
		:param parameters: id: value map of parameters.
		:param id: an identifier for the model. Uses the sequence model_0 model_1, etc if not specified.
		:param corr: correlator object to use - defaults to the last correlator started by startAnalyticsBuilderCorrelator
		:param inputs: a map of input id to type name. If type name is empty, that input is not connected.
		:return: the id of the model created.
		"""
		if corr == None: corr = self.analyticsBuilderCorrelator
		if id == None:
			id = 'model_%s' % self.modelId
			self.modelId = self.modelId + 1
		waiter = Waiter(self, corr)
		testParams=', '.join([json.dumps(blockUnderTest), json.dumps(id), json.dumps(json.dumps(parameters)), json.dumps(json.dumps(inputs)), '{}'])
		corr.sendEventStrings(f'apamax.analyticsbuilder.test.Test({testParams})')
		waiter.waitFor('com.apama.scenario.Created')
		return id

	def sendInput(self, value=0.0, name='value', id=None, corr=None):
		"""
		Sends an input to a block under test.

		:param value: value to send - default to 0, but can be string or boolean.
		:param name: id of the input to send to.
		:param id: Which model to test, or model_0 by default
		:param corr: correlator to use, or last started by startAnalyticsBuilderCorrelator by default.
		"""
		if corr == None: corr = self.analyticsBuilderCorrelator
		self.sendEventStrings(corr, self.inputEvent(name, value, id))

	def timestamp(self, t):
		"""
		Generate string for a pseudo-timestamp event
		"""
		return f'&TIME({t})'

	def inputEvent(self, name, value=0.0, id='model_0'):
		"""
		Generate string form of an input event.
		:param name: id of the input to send to.
		:param value: value to send - default to 0, but can be string or boolean.
		:param id: Which model to test, or model_0 by default
		"""
		eplType = 'string'
		if isinstance(value, float) or isinstance(value, int): eplType = 'float'
		if isinstance(value, bool): eplType = 'boolean'
		if eplType == 'string':
			value = json.dumps(value)
		return f'apamax.analyticsbuilder.test.Input("{name}", "{id}", any({eplType}, {value}))'

	def outputExpr(self, name='.*', value='.*', id='.*'):
		"""
		Expression for assertGrep for an Output event to look for.
		:param name: id of the output
		:param value: what value to look for
		:param id: Which model to test, or model_0 by default
		"""
		return f'apamax.analyticsbuilder.test.Output\("{name}","{id}",any\(.*,.?{value}.?\)\)'

	def sendEventStrings(self, corr, *events, **kwargs):
		"""
		Send events to the correlator.

		This method will include flushing the events.
		"""
		events = list(events)
		events.insert(0, '&FLUSHING(5)')
		corr.sendEventStrings(*events, **kwargs)
