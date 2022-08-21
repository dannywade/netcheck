import os
from datetime import datetime
import subprocess
from zipfile import ZipFile
from time import sleep
import json
from genie.utils import Dq
import shutil
import yaml

from backend.models import TestResults

"""
Module used for pyATS functions
"""

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


def generate_testbed(hostname: str, device_ip: str, os_type: str) -> None:

    tb = {
        "devices": {
            hostname: {
                "connections": {
                    "cli": {"ip": device_ip, "protocol": "ssh", "port": "22"}
                },
                "credentials": {
                    "default": {
                        "username": "developer",  # Hardcoded for testing only. Need to change back to env var
                        "password": "C1sco12345",
                    },
                },
                "os": os_type,
                "type": "testing_device",
                "alias": "uut",
            }
        }
    }

    # Create temp dir for testbed file
    temp_path = "./temp"
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)
    os.makedirs(temp_path)

    # Create YAML testbed file
    with open(f"{temp_path}/testbed.yaml", "w") as f:
        yaml.dump(tb, f)


def generate_datafile(testcase_params: dict) -> None:
    """
    Generate a datafile using a dict of testcase names and params as input.

    Example:

    testcase_params = {
            bgp_routes: 25,
            ebgp_neighbors: 2,
            ibgp_neighbors: 1,
            local_asn: 65000,
            remote_asns: [65001, 65002]
    }

    """
    # Create temp dir for testbed file
    temp_path = "./temp"
    # Adding params as testscript params vs testcase params
    # df = {"testcases": {**testcase_params}}
    df = {"parameters": {**testcase_params}}
    # Create YAML testbed file
    with open(f"{temp_path}/datafile.yaml", "w") as f:
        yaml.dump(df, f)


def run_pyats_job(jobfile_name: str, current_dir: str) -> str:
    """
    Runs pyATS jobfile and stores result in custom archive folder
    """
    # current_dir = os.path.dirname(os.path.abspath(__file__))

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
            f"{current_dir}/pyats_logs",
            "--archive-name",
            archive_dir_name,
        ]
    )
    # Allow time for archive creation
    sleep(3)
    # Return the file path of the archived results
    results_path = f"{current_dir}/pyats_logs/{archive_dir_name}.zip"

    return results_path


def get_pyats_results(results_path: str) -> dict:
    """
    Extracts the results.json and device CLI log from the archive folder and returns results.json as Python dict
    """
    # Extracts only the results.json file and store in a temp dir
    with ZipFile(results_path) as results_zip:
        results_zip.extract("results.json", "temp_results")

        # Extract device logs from the archive and store in the temp dir
        for fileName in results_zip.namelist():
            if "-cli-" in fileName:
                results_zip.extract(fileName, "temp_results")
                print("Device logs file found and stored in temp dir!")

        # Open the results.json file and covert to a Python dict
        with open("temp_results/results.json", "r") as results:
            results_dict = json.load(results)

        return results_dict


def parse_pyats_results(job_results: dict, test_name: str = None) -> TestResults:
    """
    Passes in pyATS job results as a Python dict and returns a dict of parsed values from results
    """

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


def read_device_logs() -> str:
    """
    Reads and returns the device logs
    """
    temp_results = os.listdir("./temp_results")
    for fileName in temp_results:
        if "-cli-" in fileName:
            device_log_file = fileName
            print("Device logs file found and read from temp dir!")

    # Read device log and return it
    with open(f"./temp_results/{device_log_file}") as f:
        log = f.read()

    return log


def cleanup_pyats_results() -> None:
    """
    Remove the temp directory used to store the pyATS job results
    """
    if os.path.exists("temp_results"):
        print("Temp results directory has been found!")
        # Delete the temp dir and all of its content
        shutil.rmtree("temp_results")
        print("Temp results directory has been deleted!")
    else:
        print("Temp results directory not found!")


def cleanup_pyats_testbed() -> None:
    """
    Remove the temp directory used to store the pyATS job results
    """
    if os.path.exists("temp"):
        print("Temp results directory has been found!")
        # Delete the temp dir and all of its content
        shutil.rmtree("temp")
        print("Temp testbed directory has been deleted!")
    else:
        print("Temp testbed directory not found!")


if __name__ == "__main__":
    testscript = "bgp"

    tc_dict = {
        "bgp_routes_testcase": {
            "parameters": {
                "bgp_routes": 25,
            }
        },
        "bgp_neighbors_testcase": {
            "parameters": {
                "ebgp_neighbors": 2,
                "ibgp_neighbors": 1,
                "local_asn": 65000,
                "remote_asns": [65001, 65002],
            }
        },
    }

    generate_datafile(tc_dict)
    # update_datafile("environment", tc_dict)
