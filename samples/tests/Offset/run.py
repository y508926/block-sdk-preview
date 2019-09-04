#
#  $Copyright (c) 2019 Software AG, Darmstadt, Germany and/or Software AG USA Inc., Reston, VA, USA, and/or its subsidiaries and/or its affiliates and/or their licensors.$
#   This file is licensed under the Apache 2.0 license - see https://www.apache.org/licenses/LICENSE-2.0
#

from pysys.constants import *
from apamax.analyticsbuilder.basetest import AnalyticsBuilderBaseTest


class PySysTest(AnalyticsBuilderBaseTest):
    def execute(self):
        self.correlator = self.startAnalyticsBuilderCorrelator(
            blockSourceDir=f'{self.project.SOURCE}/blocks/')
        self.modelId = self.createTestModel('apamax.analyticsbuilder.samples.Offset')
        self.sendEventStrings(self.correlator,
                              self.timestamp(1),
                              self.inputEvent('value', 100.75, id=self.modelId),
                              self.timestamp(2),
                              self.inputEvent('value', 10.50, id=self.modelId),
                              self.timestamp(5),
                              )

    def validate(self):
        # Verifying that there are no errors in log file.
        self.checkLogs()

        # Verifying that the model is deployed successfully.
        self.assertGrep(self.analyticsBuilderCorrelator.logfile,
                        expr='Model \"' + self.modelId + '\" with PRODUCTION mode has started')

        # Verifying the result - output from the block.
        self.assertGrep('output.evt', expr=self.outputExpr('output', 200.75))
        self.assertGrep('output.evt', expr=self.outputExpr('output', 110.50))
