"""Module used for TestRunner class"""
from datetime import datetime
import subprocess
from time import sleep
from pyats.topology import Testbed

logger = logging.getLogger(__name__)

# Maps frontend values to testscript names for custom validation testing
TASK_ID_MAPPER = {
    "Environment (CPU, Memory, etc.)": "environment",
    "BGP Routing": "routing_bgp",
    "OSPF Routing": "routing_ospf",
}

# List of available groups
GROUPS = ["env", "bgp", "ospf"]

# Maps selected tests to group
TEST_GROUP_MAPPER = {
    "Environment (CPU, Memory, etc.)": "env",
    "BGP Routing": "bgp",
    "OSPF Routing": "ospf",
}


class TestRunner:
    """
    Instantiate a test runner object that will be used to run all pyATS test jobs and testcases.
    """

    def __init__(self, test_name: str, tests: dict, testbed: Testbed) -> None:
        self.test_name = test_name
        self.tests = tests
        self.testbed = testbed

    def _get_group_tags(self):
        """Maps tests with group tag names. Groups are used to filter which testcases to run."""
        for test in self.tests:
            try:
                self.group_tags = TEST_GROUP_MAPPER.get(test, None)
            except ValueError:
                logger.error("Test group tag not found.")
        if self.group_tags not in GROUPS:
            logger.error("Test group tag not available.")
        return self.group_tags

    def _custom_group_tagging(*groups):
        # Need to create function that tests list of group tags from mapper
        pass

    def run_tests(self, jobfile_name: str, results_path: str) -> str:
        """Runs pyATS jobfile and stores result in a user-defined results path."""
        # Get current time
        now = datetime.now()
        current_time = now.strftime("%Y%b%d-%H:%M")

        archive_dir_name = current_time

        # Run the pyATS job via Easypy execution
        py_run = subprocess.run(
            args=[
                "pyats",
                "run",
                "job",
                jobfile_name,
                "--no-archive-subdir",
                "--archive-dir",
                f"{results_path}/pyats_logs",
                "--archive-name",
                archive_dir_name,
            ]
        )
        # Allow time for archive creation
        sleep(3)
        # Return the file path of the archived results
        results_path = f"{results_path}/pyats_logs/{archive_dir_name}.zip"

        return results_path
