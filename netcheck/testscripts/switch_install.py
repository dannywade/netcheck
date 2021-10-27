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
class SwitchInstall(aetest.Testcase):
    @aetest.setup
    def setup(self, device):
        if device.connected:
            self.passed("Successfully connected to the device")
        else:
            self.failed("Could not connect to the device")

    @aetest.test
    def verify_switch_basics(self, steps, device):
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

    @aetest.test
    def verify_ios_version(self, steps, device):
        with steps.start("Checking the IOS version") as step:
            try:
                self.version = device.parse("show version")
                iosxe_standard = "17.03.03"
                ios_standard = "15.2"
                if device.os == "iosxe":
                    ios_check = (
                        Dq(self.version)
                        .contains(iosxe_standard)
                        .get_values("xe_version")
                    )
                elif device.os == "ios":
                    ios_check = (
                        Dq(self.version).contains(ios_standard).get_values("version")
                    )

                if ios_check:
                    step.passed("Device is running the proper IOS version.")
                else:
                    step.failed(
                        "Device is running a different IOS version than the defined standard."
                    )
            except Exception as e:
                self.failed(
                    f"Could not parse data due to the following error: {str(e)}"
                )

    # Tests to include:
    # DONE:
    # - Input errors are less than 1000
    # TODO:
    # - Default gateway is set
    # - STP is configured and running rapid-pvst
    # - VTP is disabled

    @aetest.test
    def interface_errors(self, steps, device):
        with steps.start("Checking for input errors on all interfaces") as step:
            try:
                if device.os == "iosxe" or "ios":
                    self.interfaces = device.parse("show interfaces")
                    input_errors = Dq(self.interfaces).get_values(
                        "in_errors"
                    )  # Returns a list of input errors for all interfaces
                for error in input_errors:
                    if error < 1000:
                        pass
                    else:
                        step.failed(
                            "One of the interfaces has more than 1000 input errors"
                        )
                step.passed("All interfaces are clean of input errors!")
            except Exception as e:
                self.failed(
                    f"Could not parse data due to the following error: {str(e)}"
                )

    @aetest.test
    def gather_logs(self, steps, device):
        with steps.start("Gather only error logs") as step:
            try:
                if device.os == "iosxe":
                    log_results = device.api.get_logging_logs()
                elif device.os == "ios":
                    log_results = device.parse("show logging")
                error_logs = log_results.q.contains_key_value(
                    "level", "error"
                ).get_values("messages_logged")
                if not error_logs:
                    step.passed("There were no Error logs!")
                else:
                    step.failed("There were some Error logs.")
            except Exception as e:
                self.failed(
                    f"Could not parse data due to the following error: {str(e)}"
                )


class CommonCleanup(aetest.CommonCleanup):
    @aetest.subsection
    def disconnect_from_devices(self, steps, device):
        with steps.start(f"Disconnecting from {device.name}"):
            device.disconnect()
