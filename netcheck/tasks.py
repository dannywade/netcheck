from sqlmodel import Session
from backend.db import engine
from helpers.validation import (
    run_pyats_job,
    get_pyats_results,
    parse_pyats_results,
    cleanup_pyats_results,
    cleanup_pyats_testbed,
)
from helpers.runner import TestRunner
from datetime import datetime
import os

app_dir = os.path.dirname(__file__)


def run_network_test(test_name: str = None):
    current_time = datetime.now()

    # TODO: Change jobfile name and pass in test name from user
    job_results = run_pyats_job(
        jobfile_name="./jobfiles/circuit_jobfile.py", current_dir=app_dir
    )

    results_dict = get_pyats_results(results_path=job_results)
    results_summary = parse_pyats_results(job_results=results_dict, test_name=test_name)
    # device_logs = read_device_logs()

    # Save test results summary to the database
    with Session(engine) as session:
        session.add(results_summary)
        session.commit()
        session.refresh(results_summary)

    # TODO: Figure out what should be returned since HTML display is not necessary
    # Convert test results to a dictionary to use in HTML J2 template
    html_results = dict(results_summary)

    # Remove temp files used in testing
    cleanup_pyats_results()
    cleanup_pyats_testbed()

    return html_results


def run_network_tests(test_name: str = None, tests: list = None):
    current_time = datetime.now()

    runner = TestRunner(test_name=test_name, tests=tests)

    runner.run_tests(jobfile_name="custom_jobfile.py", results_path=app_dir)
    runner.get_results()
    results_summary = runner.parse_results()
    # device_logs = read_device_logs()

    # Save test results summary to the database
    with Session(engine) as session:
        session.add(results_summary)
        session.commit()
        session.refresh(results_summary)

    # TODO: Figure out what should be returned since HTML display is not necessary
    # Convert test results to a dictionary to use in HTML J2 template
    html_results = dict(results_summary)

    # Remove temp files used in testing
    runner.cleanup()

    return html_results
