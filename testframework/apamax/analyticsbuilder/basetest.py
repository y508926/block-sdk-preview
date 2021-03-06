#!/usr/bin/env python
## License
# Copyright (c) 2017-2019 Software AG, Darmstadt, Germany and/or its licensors

# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the
# License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied.
# See the License for the specific language governing permissions and limitations under the License.


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

	Requires the following to be set on the project in pysysproject.xml file (typically from the environment):
	ANALYTICS_BUILDER_SDK
	APAMA_HOME
	"""

	def __init__(self, descriptor, outsubdir, runner, **kwargs):
		super(AnalyticsBuilderBaseTest, self).__init__(descriptor, outsubdir, runner, **kwargs)
		self.modelId=0
		self.IS_WINDOWS = OSFAMILY=='windows'

	def runAnalyticsBuilderScript(self, args=[], environs={}, **kwargs):
		"""
		Run the analytics_builder script.
		:param args: The arguments to pass to the script.
		:param environs: Any environment overrides.
		:param kwargs: Any arguments to pass through to startProcess.
		:return: The process handle of the process (L{ProcessWrapper}).
		"""
		env = dict(os.environ)
		env['PYTHONDONTWRITEBYTECODE'] = 'true'  # .pyc optimizations not needed and make it harder to delete things later
		if environs: env.update(environs)
		script = 'analytics_builder'
		stdouterr = self.allocateUniqueStdOutErr(script)

		try:
			return self.startProcess(f'{self.project.ANALYTICS_BUILDER_SDK}/{script}'+('.cmd' if self.IS_WINDOWS else ''), args,
				stdout=stdouterr[0], stderr=stdouterr[1],
				displayName=script, environs=env, **kwargs)
		except Exception:
			self.logFileContents(stdouterr[1]) or self.logFileContents(stdouterr[0])
			raise

	def injectCumulocityEvents(self, corr):
		"""
		Inject the Cumulocity event definitions.
		:param corrHelper: The CorrelatorHelper object.
		:return: None.
		"""
		corr.injectEPL(['Cumulocity_EventDefinitions.mon'], filedir=self.project.APAMA_HOME + "/monitors/cumulocity/9.8")
		corr.injectCDP(self.project.ANALYTICS_BUILDER_SDK + '/block-api/framework/cumulocity-forward-events.cdp')
		
	def startAnalyticsBuilderCorrelator(self, blockSourceDir=None, Xclock=True, numWorkers=4, **kwargs):
		"""
		Start a correlator with the EPL for Analytics Builder loaded.
		:param blockSourceDir: A location of blocks to include.
		:param Xclock: Externally clock correlator (on by default).
		:param numWorkers: Number of workers for Analytics Builder runtime (4 by default).
		"""

		# Build and extract the block extension:
		if blockSourceDir == None: blockSourceDir = self.input
		blockOutput = self.output+'/block-output.zip'
		self.runAnalyticsBuilderScript(['build', 'extension', '--input', blockSourceDir, '--output', blockOutput])
		with zipfile.ZipFile(blockOutput, 'r') as zf:
			blockOutput = Path(self.output + '/block-output/')
			os.mkdir(blockOutput)
			zf.extractall(blockOutput)

		# Start the correlator:
		corr = CorrelatorHelper(self)
		arguments=kwargs.get('arguments', [])
		arguments.append(f'-DanalyticsBuilder.numWorkerThreads={numWorkers}')
		kwargs['arguments']=arguments
		logfile=kwargs.get('logfile', 'correlator.log')
		kwargs['logfile']=logfile
		corr.start(Xclock=Xclock, **kwargs)
		corr.logfile = logfile
		corr.injectEPL([self.project.APAMA_HOME+'/monitors/'+i+'.mon' for i in ['ScenarioService', 'data_storage/MemoryStore', 'JSONPlugin', 'AnyExtractor', 'ManagementImpl', 'Management', 'ConnectivityPluginsControl', 'ConnectivityPlugins', 'HTTPClientEvents', 'AutomaticOnApplicationInitialized']])
		corr.injectCDP(self.project.ANALYTICS_BUILDER_SDK+'/block-api/framework/analyticsbuilder-framework.cdp')
		self.injectCumulocityEvents(corr)
		corr.injectCDP(self.project.ANALYTICS_BUILDER_SDK + '/block-api/framework/cumulocity-inventoryLookup-events.cdp')
		corr.injectEPL(self.project.ANALYTICS_BUILDER_SDK+'/testframework/resources/TestHelpers.mon')

		# inject block files:
		corr.injectEPL(sorted(list(blockOutput.rglob('*.mon'))))
		corr.send(sorted(list(blockOutput.rglob('*.evt'))))

		# now done
		corr.sendEventStrings('com.apama.connectivity.ApplicationInitialized()')
		corr.flush(10)
		self.analyticsBuilderCorrelator = corr
		corr.receive('output.evt', channels=['TestOutput'])
		return corr


	def createTestModel(self, blockUnderTest, parameters={}, id=None, corr=None, inputs={}, isDeviceOrGroup=None, wiring=[]):
		"""
		Create a test model.

		A test model tests a blockUnderTest and connects generic inputs and outputs to its block inputs/ outputs.
		:param blockUnderTest: Fully qualified name of the block to test (including package name).  Or a list of block fully qualified names, in which case wiring is required too.
		:param parameters: Map of identifier, value per parameter. (or if multiple models specified, block id to map of parameters)
		:param id: An identifier for the model. Uses the sequence model_0 model_1, etc. if not specified.
		:param corr: The correlator object to use - defaults to the last correlator started by startAnalyticsBuilderCorrelator.
		:param inputs: A map of input identifiers and corresponding type names. If the type name is empty, that input is not connected.
		:param isDeviceOrGroup: Cumulocity device or group identifier.
		:param if more than one block supplied, then this contains the wiring as a list of strings in the form source block index:output id:target block index:input id - e.g. ['0:timeWindow:1:window', '0:timeWindow:1:otherInput']
		:return: The identifier of the created model.
		"""
		if corr == None: corr = self.analyticsBuilderCorrelator
		if id == None:
			id = 'model_%s' % self.modelId
			self.modelId = self.modelId + 1
		waiter = Waiter(self, corr)
		if not isinstance(blockUnderTest, list):
			blockUnderTest=[blockUnderTest]
		testParams=', '.join([json.dumps(blockUnderTest), json.dumps(id), json.dumps(json.dumps(parameters)), json.dumps(json.dumps(inputs)), json.dumps(wiring), '{}'])
		corr.sendEventStrings(f'apamax.analyticsbuilder.test.Test({testParams})')
		if isDeviceOrGroup != None:		#As Analytics Builder model does async validaion of devices in the inventory, so mocking response for that.
			self.sendEventStrings(corr,self.inputManagedObject(parameters['deviceId'], 'com_test_device', 'Device1', [], [], [], [], [], [],{}, {isDeviceOrGroup: {}}))
		waiter.waitFor('com.apama.scenario.Created')
		return id


	def sendInput(self, value=0.0, name='value', id=None, corr=None):
		"""
		Send an input to a block under test.

		:param value: The value to send. Default to 0, but can be string or boolean.
		:param name: The identifier of the input to send to.
		:param id: The model to test, or model_0 by default
		:param corr: The correlator to use, or last started by startAnalyticsBuilderCorrelator by default.
		"""
		if corr == None: corr = self.analyticsBuilderCorrelator
		self.sendEventStrings(corr, self.inputEvent(name, value, id))

	def timestamp(self, t):
		"""
		Generate a string for a pseudo-timestamp event.
		"""
		return f'&TIME({t})'

	def inputEvent(self, name, value=0.0, id='model_0', partition='', eplType = 'string'):
		"""
		Generate the string form of an input event.
		:param name: The identifier of the input to send to.
		:param value: The value to send. Default to 0, but can be string or boolean.
		:param id: The model to test, or model_0 by default.
		"""
		if isinstance(value, float) or isinstance(value, int): eplType = 'float'
		if isinstance(value, bool): eplType = 'boolean'
		if eplType == 'string':
			value = json.dumps(value)
		return f'apamax.analyticsbuilder.test.Input("{name}", "{id}", "{partition}", any({eplType}, {value}))'
	
	def outputExpr(self, name='.*', value='.*', id='.*', partition='.*', time='.*', properties='.*'):
		"""
		Expression for assertGrep for an output event to look for.
		:param name: The identifier of the output
		:param value: The value to look for
		:param id: The model to test, or model_0 by default
		"""
		open=''
		end=''
		return f'apamax.analyticsbuilder.test.Output\("{name}","{id}","{partition}",{time},any\(.*,.?{value}.?\),{open}{properties}{end}\)'

	def sendEventStrings(self, corr, *events, **kwargs):
		"""
		Send events to the correlator.

		This method will include flushing the events.
		"""
		events = list(events)
		events.insert(0, '&FLUSHING(50)')
		corr.sendEventStrings(*events, **kwargs)

	def checkLogs(self, logfile=None):
		"""
		Check the correlator log files for errors/warnings.

		Verify the log files do not contain any errors. Don't use if you have tested with invalid parameters.
		:param logFile: Name of the log file, or uses last correlator started by startAnalyticsBuilderCorrelator by default.
		"""
		if logfile == None:
			logfile = self.analyticsBuilderCorrelator.logfile
		self.assertGrep(logfile, expr=' ERROR .*', contains=False)
		self.assertGrep(logfile, expr=' WARN .*', contains=False, ignores=['RLIMIT.* is not unlimited'])
