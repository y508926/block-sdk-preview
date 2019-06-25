from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/')

		# this model will fail to deploy: missing a required param:
		correlator.receive('all.evt')
		modelId_failed = self.createTestModel('apamax.analyticsbuilder.samples.TimeDelay')
		self.assertGrep('all.evt', expr="Created.*No value provided for required parameter 'Delay .secs.'")


		modelId = self.createTestModel('apamax.analyticsbuilder.samples.TimeDelay', {'delaySecs':1.9})
		self.sendEventStrings(correlator,
		                      self.timestamp(1),
		                      self.inputEvent('value', 12.25, id = modelId),
		                      self.timestamp(2))
		self.assertGrep('output.evt', expr=self.outputExpr('delayedValue', 12.25), contains=False)
		self.sendEventStrings(correlator,
		                      self.timestamp(3))
		self.assertGrep('output.evt', expr=self.outputExpr('delayedValue', 12.25), contains=True)
		self.sendEventStrings(correlator,
		                      self.inputEvent('value', 7.75, id = modelId),
		                      self.timestamp(5.1))

	def validate(self):
		self.assertGrep('output.evt', expr=self.outputExpr('delayedValue', 7.75))

