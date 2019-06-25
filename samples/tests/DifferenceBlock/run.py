from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest

class PySysTest(AnalyticsBuilderBaseTest):
	def execute(self):
		correlator = self.startAnalyticsBuilderCorrelator(blockSourceDir=f'{self.project.SOURCE}/blocks/')
		modelId = self.createTestModel('apamax.analyticsbuilder.samples.Difference')
		self.sendEventStrings(correlator,
		                      self.timestamp(1),
		                      self.inputEvent('value1', 12.25, id = modelId),
		                      self.timestamp(2),
		                      self.inputEvent('value2', 7.75, id = modelId),
		                      self.timestamp(2.1))

	def validate(self):
		self.assertGrep('output.evt', expr=self.outputExpr('absoluteDifference', 4.5))

