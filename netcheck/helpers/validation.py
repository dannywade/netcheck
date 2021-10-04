from genericpath import exists
import os
from decouple import config
from datetime import datetime
import subprocess
from zipfile import ZipFile
from time import sleep
import json
from genie.utils import Dq
import shutil
from genie import testbed
import os
import yaml

"""
Module used for pyATS functions
"""


def generate_testbed(hostname: str, device_ip: str, os_type: str) -> None:

    tb = {
        "devices": {
            hostname: {
                "connections": {
                    "cli": {"ip": device_ip, "protocol": "ssh", "port": "22"}
                },
                "credentials": {
                    "default": {
                        "username": "%ENV{EVE_USER}",
                        "password": "%ENV{EVE_PW}",
                    },
                },
                "os": os_type,
                "type": "testing_device",
                "alias": "uut",
            }
        }
    }

    # Create temp dir for testbed file
    temp_path = "./temp_testbed"
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)
    os.makedirs(temp_path)

    # Create YAML testbed file
    with open("./temp_testbed/testbed.yaml", "w") as f:
        yaml.dump(tb, f)


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
            "./pyats_logs",
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
                print("Device logs file found!")

        # Open the results.json file and covert to a Python dict
        with open("temp_results/results.json", "r") as results:
            results_dict = json.load(results)

        return results_dict


def parse_pyats_results(job_results: dict) -> dict:
    """
    Passes in pyATS job results as a Python dict and returns a dict of parsed values from results
    """
    # Initialize parsed results dict
    parsed_results = {}

    # Find success_rate, total, passed, and failed values under the TestSuite results
    testsuite_results = Dq(job_results).contains_key_value("report", "summary")
    success_rate = testsuite_results.get_values("success_rate")  # float
    total = testsuite_results.get_values("total")
    passed = testsuite_results.get_values("passed")
    failed = testsuite_results.get_values("failed")

    parsed_results.update(
        {
            "success_rate": success_rate[0],
            "total_tests": total[0],
            "tests_passed": passed[0],
            "tests_failed": failed[0],
        }
    )

    return parsed_results


def read_device_logs():
    """
    Reads and returns the device logs
    """
    temp_results = os.listdir("./temp_results")
    for fileName in temp_results:
        if "-cli-" in fileName:
            device_log_file = fileName
            print("Device logs file found!")

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
    if os.path.exists("temp_testbed"):
        print("Temp results directory has been found!")
        # Delete the temp dir and all of its content
        shutil.rmtree("temp_testbed")
        print("Temp testbed directory has been deleted!")
    else:
        print("Temp testbed directory not found!")
