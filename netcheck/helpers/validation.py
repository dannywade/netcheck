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

"""
Module used for pyATS functions
"""
def generate_testbed(device_ip: str, os: str) -> dict:
    username = config("EVE_USER")
    password = config("EVE_PW")
    
    tb = {
        "devices": {
            "uut": {
                "connections": {
                    "cli": {"ip": device_ip, "protocol": "ssh", "port": "22"}
                },
                "credentials": {
                    "default": {"username": username, "password": password},
                },
                "os": os,
                "type": "testing_device",
            }
        }
    }
    
    # TODO: Need to store testbed for jobfile to read from and load - DB (using data model) or YAML file

    return tb

def run_pyats_job(testbed_file: dict, jobfile_name: str, current_dir: str) -> str:
    """
    Runs pyATS jobfile and stores result in custom archive folder
    """
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get current time
    now = datetime.now()
    current_time = now.strftime("%Y%b%d-%H:%M")
    
    archive_dir_name = current_time
    
    # Run the pyATS job via Easypy execution
    py_run = subprocess.run(args=['pyats', 'run', 'job', jobfile_name, '--testbed-file', testbed_file, '--no-archive-subdir', '--archive-dir', './pyats_logs', '--archive-name', archive_dir_name])
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
        results_zip.extract('results.json', 'temp_results')
        
        # Extract device logs from the archive and store in the temp dir
        for fileName in results_zip.namelist():
            if '-cli-' in fileName:
                results_zip.extract(fileName, 'temp_results')
                print("Device logs file found!")
        
        # Open the results.json file and covert to a Python dict
        with open("temp_results/results.json", "r") as results:
            results_dict = json.load(results)
        
        return results_dict

def parse_pyats_results(results_dict: dict) -> dict:
    """
    Passes in pyATS job results as a Python dict and returns a dict of parsed values from results
    """
    # Initialize parsed results dict
    parsed_results = {}
    
    # Find success_rate, total, passed, and failed values under the TestSuite results
    testsuite_results = Dq(results_dict).contains_key_value("report", "summary")
    success_rate = testsuite_results.get_values("success_rate") # float
    total = testsuite_results.get_values("total")
    passed = testsuite_results.get_values("passed")
    failed = testsuite_results.get_values("failed")
    
    parsed_results.update({"success_rate": success_rate[0], "total_tests": total[0], "tests_passed": passed[0], "tests_failed": failed[0]})

    return parsed_results

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