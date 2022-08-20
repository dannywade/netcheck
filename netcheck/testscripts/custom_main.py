from pyats import aetest
from genie.utils import Dq
import logging
import environment, routing_bgp, routing_ospf

logger = logging.getLogger(__name__)


class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def connect_to_devices(self, steps, testbed):
        device = testbed.devices["uut"]

        # Add device as testscript param
        self.parent.parameters.update(device=device)

        with steps.start(f"Connect to {device.name}"):
            device.connect()
            # To change Unicon logs: logfile='{new_path}'


### TESTCASE SECTION ###
# Call/run custom testcases
environment.CheckEnvironment
routing_bgp.BGPTest
routing_ospf.OSPFTest


class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect_from_devices(self, steps, device):
        with steps.start(f"Disconnecting from {device.name}"):
            device.disconnect()
