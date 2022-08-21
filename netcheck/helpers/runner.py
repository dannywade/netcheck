"""Module used for TestRunner class"""
from datetime import datetime
import logging
import subprocess
from time import sleep
from pyats.topology import Testbed
from genie.utils import Dq
import os
from os.path import exists
import json
from zipfile import ZipFile
import shutil

from backend.models import TestResults

logger = logging.getLogger(__name__)

# Maps frontend values to testscript names for custom validation testing
TASK_GROUP_MAPPER = {
    "Environment (CPU, Memory, etc.)": "environment",
    "BGP Routing": "routing_bgp",
    "OSPF Routing": "routing_ospf",
}


class TestRunner:
    """
    Instantiate a test runner object that will be used to run all pyATS test jobs and testcases.
    """

    def __init__(self, test_name: str, tests: dict, testbed: Testbed = None) -> None:
        self.test_name = test_name
        self.tests = tests
        self.testbed = testbed

    def run_tests(self, jobfile_name: str, results_path: str) -> str:
        """Runs pyATS jobfile and stores result in a user-defined results path."""
        # Get current time
        now = datetime.now()
        current_time = now.strftime("%Y%b%d-%H:%M")

        # Map to proper testscript names and format to fit pyATS logic string input as CLI arg
        test_names = []
        for t in self.tests:
            true_name = TASK_GROUP_MAPPER.get(t, None)
            test_names.append("'" + true_name + "'")

        if not test_names:
            raise IndexError("No group names passed to Easypy.")

        jobfile_dir = "./jobfiles"
        jobfile_path = f"{jobfile_dir}/{jobfile_name}"
        if not exists(jobfile_path):
            raise FileNotFoundError("Jobfile not found.")

        archive_dir_name = current_time
        temp_tb = "./temp/testbed.yaml"
        generated_df = "./datafiles/main_datafile.yaml"
        if not exists(temp_tb) or not exists(generated_df):
            raise FileNotFoundError("Generated testbed or datafile not found.")
        # Run the pyATS job via Easypy execution
        py_run = subprocess.run(
            args=[
                "pyats",
                "run",
                "job",
                jobfile_path,
                "--testbed-file",
                temp_tb,
                "--groups",
                f"Or({', '.join(str(x) for x in test_names)})",
                "--datafile",
                generated_df,
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
        self.results = results_path

        return results_path

    def get_results(self, results_path: str = None) -> dict:
        """
        Extracts the results.json and device CLI log from the archive folder and returns results.json as Python dict
        """
        if results_path is None:
            results_path = self.results
        # Extracts only the results.json file and store in a temp dir
        with ZipFile(results_path) as results_zip:
            results_zip.extract("results.json", "temp_results")

            # Extract device logs from the archive and store in the temp dir
            for fileName in results_zip.namelist():
                if "-cli-" in fileName:
                    results_zip.extract(fileName, "temp_results")
                    logger.info("Device logs file found and stored in temp dir!")

            # Open the results.json file and covert to a Python dict
            with open("temp_results/results.json", "r") as results:
                results_dict = json.load(results)
            self.job_results = results_dict

            return results_dict

    def parse_results(
        self,
        test_name: str = None,
        job_results: dict = None,
    ) -> TestResults:
        """
        Passes in pyATS job results as a Python dict and returns a dict of parsed values from results
        """

        if job_results is None:
            job_results = self.job_results

        # Find success_rate, total, passed, and failed values under the TestSuite results
        testsuite_results = Dq(job_results).contains_key_value("report", "summary")
        if test_name is None:
            test_name = job_results["report"]["name"]
        execution_time = job_results["report"]["starttime"]
        success_rate = testsuite_results.get_values("success_rate")  # float
        total = testsuite_results.get_values("total")
        passed = testsuite_results.get_values("passed")
        failed = testsuite_results.get_values("failed")

        parsed_results = TestResults(
            name=test_name,
            executed_at=execution_time,
            success_rate=success_rate[0],
            total_tests=total[0],
            tests_passed=passed[0],
            tests_failed=failed[0],
        )

        return parsed_results

    def read_device_logs(self) -> str:
        """
        Reads and returns the device logs
        """
        temp_results = os.listdir("./temp_results")
        for fileName in temp_results:
            if "-cli-" in fileName:
                device_log_file = fileName
                logger.info("Device logs file found and read from temp dir!")

        # Read device log and return it
        with open(f"./temp_results/{device_log_file}") as f:
            log = f.read()

        return log

    def _cleanup_pyats_results(self) -> None:
        """
        Remove the temp directory used to store the pyATS job results
        """
        if os.path.exists("temp_results"):
            logger.info("Temp results directory has been found!")
            # Delete the temp dir and all of its content
            shutil.rmtree("temp_results")
            logger.info("Temp results directory has been deleted!")
        else:
            logger.info("Temp results directory not found!")

    def _cleanup_pyats_testbed(self) -> None:
        """
        Remove the temp directory used to store the pyATS testbed
        """
        if os.path.exists("temp"):
            logger.info("Temp results directory has been found!")
            # Delete the temp dir and all of its content
            shutil.rmtree("temp")
            logger.info("Temp testbed directory has been deleted!")
        else:
            logger.info("Temp testbed directory not found!")

    def cleanup(self) -> None:
        """
        Remove the temp directory and pyATS job results
        """
        self._cleanup_pyats_results()
        self._cleanup_pyats_testbed()
