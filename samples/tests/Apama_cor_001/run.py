# Sample PySys testcase
# Copyright (c) 2015-2016, 2018-2019 Software AG, Darmstadt, Germany and/or Software AG USA Inc., Reston, VA, USA, and/or its subsidiaries and/or its affiliates and/or their licensors. 
# Use, reproduction, transfer, publication or disclosure is prohibited except as specifically provided for in your License Agreement with Software AG 

from pysys.constants import *
from apama.basetest import ApamaBaseTest
from apama.correlator import CorrelatorHelper

class PySysTest(ApamaBaseTest):

	def execute(self):
		# create the correlator helper, start the correlator and attach an 
		# engine_receive process listening to a test channel. The helper will 
		# automatically get an available port that will be used for all 
		# operations against it
		correlator = CorrelatorHelper(self, name='testcorrelator')
		correlator.start(logfile='testcorrelator.log')
		receiveProcess = correlator.receive(filename='receive.evt', channels=['EchoChannel'], logChannels=True)
		correlator.applicationEventLogging(enable=True)
		
		# inject the simple.mon monitor (directory defaults to the testcase input)
		correlator.injectEPL(filenames=['simple.mon'])
		
		# not strictly necessary in this testcase, but a useful example of waiting 
		# for a log message
		self.waitForSignal('testcorrelator.log', expr="Loaded simple test monitor", 
			process=correlator.process, errorExpr=[' (ERROR|FATAL) .*'])
		
		# send in the events contained in the simple.evt file (directory defaults 
		# to the testcase input)
		correlator.send(filenames=['simple.evt'])
			
		# wait for all events to be processed
		correlator.flush()
		
		# wait until the receiver writes the expected events to disk
		self.waitForSignal('receive.evt', expr="SimpleEvent", condition=">=2")
		
	def validate(self):
		# look for log statements in the correlator log file
		self.assertGrep('testcorrelator.log', expr=' (ERROR|FATAL) .*', contains=False)
		
		exprList = []
		exprList.append('Received simple event with message - This is the first simple event')
		exprList.append('Received simple event with message - This is the second simple event')
		self.assertOrderedGrep('testcorrelator.log', exprList=exprList)
	
		# check the received events against the reference
		self.assertDiff('receive.evt', 'ref_receive.evt')
		