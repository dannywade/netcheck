"""Testscript to check on environmental values such as CPU, memory, and power."""

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


class CheckEnvironment(aetest.Testcase):
    @aetest.setup
    def setup(self, device):
        if device.connected:
            self.passed("Successfully connected to the device")
        else:
            self.failed("Could not connect to the device")

    @aetest.test
    def verify_cpu_memory(self, steps, device):
        with steps.start("Checking CPU utilization") as step:
            try:
                if device.os == "iosxe" or "ios":
                    cpu_util = device.api.get_platform_cpu_load()
                if cpu_util < 75:
                    step.passed("Device is running under 75% CPU utilization")
                else:
                    step.failed(
                        "Device is running running higher than 75% CPU utilization"
                    )
            except Exception as e:
                self.failed(
                    f"Could not parse data due to the following error: {str(e)}"
                )
        with steps.start("Checking memory utilization") as step:
            try:
                if device.os == "iosxe" or "ios":
                    mem_util = device.api.get_platform_memory_usage()
                if mem_util < 75:
                    step.passed("Device is running under 75% memory utilization")
                else:
                    step.failed(
                        "Device is running running higher than 75% memory utilization"
                    )
            except Exception as e:
                self.failed(
                    f"Could not parse data due to the following error: {str(e)}"
                )

        # TODO: Add test for checking power supplies
        @aetest.test
        def verify_power(self, steps, device):
            pass


class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect_from_devices(self, steps, device):
        with steps.start(f"Disconnecting from {device.name}"):
            device.disconnect()
