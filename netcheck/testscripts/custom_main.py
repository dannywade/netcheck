from pyats import aetest
from genie.utils import Dq
import logging

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
# TODO: Figure out way to import custom testcases vs housing them in one file
class CheckEnvironment(aetest.Testcase):
    @aetest.setup
    def setup(self, device):
        if device.connected:
            self.passed("Successfully connected to the device")
        else:
            self.failed("Could not connect to the device")

    @aetest.test
    def verify_cpu_usage(self, steps, device, cpu_util):
        with steps.start("Checking CPU utilization") as step:
            try:
                if device.os == "iosxe" or "ios":
                    device_cpu = device.api.get_platform_cpu_load()
                if device_cpu < int(cpu_util):
                    step.passed(
                        f"Device is running under desired ({cpu_util}%) CPU utilization"
                    )
                else:
                    step.failed(
                        f"Device is running running higher than desired ({cpu_util}%) CPU utilization"
                    )
            except Exception as e:
                step.failed(
                    f"Could not parse data due to the following error: {str(e)}"
                )

    @aetest.test
    def verify_memory_usage(self, steps, device, mem_util):
        with steps.start("Checking memory utilization") as step:
            try:
                if device.os == "iosxe" or "ios":
                    device_mem = device.api.get_platform_memory_usage()
                if device_mem < int(mem_util):
                    step.passed(
                        f"Device is running under desired ({mem_util}%) memory utilization"
                    )
                else:
                    step.failed(
                        f"Device is running running higher than desired ({mem_util}%) memory utilization"
                    )
            except Exception as e:
                step.failed(
                    f"Could not parse data due to the following error: {str(e)}"
                )

        # TODO: Add test for checking power supplies
        @aetest.test
        def verify_power(self, steps, device):
            pass


class BGPTest(aetest.Testcase):
    logging.info("BGP testcase imported.")

    @aetest.test
    def bgp_test1(self):
        logging.info("This is BGP Test 1")


class OSPFTest(aetest.Testcase):
    logging.info("OSPF testcase imported.")

    @aetest.test
    def ospf_test1(self):
        print("This is OSPF Test 1")


class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect_from_devices(self, steps, device):
        with steps.start(f"Disconnecting from {device.name}"):
            device.disconnect()
