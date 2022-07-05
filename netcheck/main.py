import ast
import uuid
from fastapi import FastAPI, Request, Form
from fastapi.params import Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.future import select
from sqlmodel import Session
import os
from datetime import datetime
from rq import Queue
from rq.job import Job

# Local imports
from api.api_v1.api import api_router
from backend.models import TestResults
from backend.db import create_db_and_tables, engine
from helpers.validation import (
    generate_testbed,
    run_pyats_job,
    get_pyats_results,
    parse_pyats_results,
    cleanup_pyats_results,
    cleanup_pyats_testbed,
    read_device_logs,
)
from tasks import run_network_test
from worker import conn

# Run the app: uvicorn main:app --reload

app_dir = os.path.dirname(__file__)

api_description = "API used to validate and performs tests against your network"

app = FastAPI(description=api_description, version="V1", title="NetCheck API")

# Initializes RQ queue and connects to Redis
q = Queue(connection=conn)  # no args implies the default queue

# Initialize the SQLite DB
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Adds data in as rows
def create_test_results():
    current_date = datetime.now()
    # current_date = get_time.strftime("%m/%d/%Y %H:%M:%S")
    result1 = TestResults(
        name="circuit_upgrade",
        executed_at=current_date,
        success_rate=100.0,
        total_tests=3,
        tests_passed=3,
        tests_failed=0,
    )
    result2 = TestResults(
        name="wan_check",
        executed_at=current_date,
        success_rate=50.0,
        total_tests=4,
        tests_passed=2,
        tests_failed=2,
    )
    result3 = TestResults(
        name="l2_stp_check",
        executed_at=current_date,
        success_rate=0,
        total_tests=3,
        tests_passed=0,
        tests_failed=3,
    )

    with Session(engine) as session:
        session.add(result1)
        session.add(result2)
        session.add(result3)

        session.commit()

        session.refresh(result1)


def select_test_results():
    with Session(engine) as session:
        # Filter to test results with 100% success rate
        statement = select(TestResults).where(TestResults.success_rate == 100.0)
        result_1 = session.get(TestResults, 1)
        results = session.exec(statement)
        one_result = results.first()

        # Updating values for first row with 100% success rate
        # result_1.success_rate = 55.0
        # session.add(result_1)
        # session.commit()
        # session.refresh(result_1)
        # print(result_1)

        # Print all rows
        print(results.all())
        # Print first result of many
        # print(results.first())


# For Testing - Used to create dummy records in DB
# create_db_and_tables()
# create_test_results()
# select_test_results()

# API router
app.include_router(api_router, prefix="/api/v1")

# Link app to static files and templates
app.mount(
    "/frontend/static",
    StaticFiles(directory=f"{app_dir}/frontend/static"),
    name="static",
)
templates = Jinja2Templates(directory=f"{app_dir}/frontend/templates")

# Frontend views
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/validation", response_class=HTMLResponse)
async def post_checks(request: Request):
    return templates.TemplateResponse("validation.html", {"request": request})

@app.get("/custom-validation", response_class=HTMLResponse)
async def custom_checks(request: Request):
    return templates.TemplateResponse("custom_validation.html", {"request": request})


@app.get("/analysis", response_class=HTMLResponse)
async def analysis(request: Request):
    return templates.TemplateResponse("analysis.html", {"request": request})

@app.post("/validateForm", response_class=HTMLResponse)
async def validation_results(
    request: Request,
    deviceHostname: str = Form(...),
    osType: str = Form(...),
    deviceIp: str = Form(...),
):
    current_time = datetime.now()

    generate_testbed(hostname=deviceHostname, os_type=osType, device_ip=deviceIp)
    job_results = run_pyats_job(
        jobfile_name="./jobfiles/circuit_jobfile.py", current_dir=app_dir
    )
    results_dict = get_pyats_results(results_path=job_results)
    results_summary = parse_pyats_results(job_results=results_dict)
    device_logs = read_device_logs()

    # Save test results summary to the database
    with Session(engine) as session:
        session.add(results_summary)
        session.commit()
        session.refresh(results_summary)

    # Convert test results to a dictionary to use in HTML J2 template
    html_results = dict(results_summary)

    # Remove temp files used in testing
    cleanup_pyats_results()
    cleanup_pyats_testbed()

    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "date": current_time,
            "device_ip": deviceIp,
            "output": device_logs,
            **html_results,
        },
    )


@app.post("/validateSwitchInstall", response_class=HTMLResponse)
async def validation_results(
    request: Request,
    switchHostname: str = Form(...),
    switchOsType: str = Form(...),
    switchIp: str = Form(...),
):
    current_time = datetime.now()

    generate_testbed(hostname=switchHostname, os_type=switchOsType, device_ip=switchIp)
    job_results = run_pyats_job(
        jobfile_name="./jobfiles/switch_install_jobfile.py", current_dir=app_dir
    )
    results_dict = get_pyats_results(results_path=job_results)
    results_summary = parse_pyats_results(job_results=results_dict)
    device_logs = read_device_logs()

    # Save test results summary to the database
    with Session(engine) as session:
        session.add(results_summary)
        session.commit()
        session.refresh(results_summary)

    # Convert test results to a dictionary to use in HTML J2 template
    html_results = dict(results_summary)

    # Remove temp files used in testing
    # cleanup_pyats_results()
    # cleanup_pyats_testbed()

    return templates.TemplateResponse(
        "results.html",
        {
            "request": request,
            "date": current_time,
            "device_ip": switchIp,
            "output": device_logs,
            **html_results,
        },
    )

@app.post("/custom-post")
async def custom_validation(request: Request):
    # Receive data via XMLHttpRequest
    test_names = await request.body()
    # Convert bytes to Python dict for further parsing
    dict_convert = test_names.decode("UTF-8")
    my_data = ast.literal_eval(dict_convert)

    # TODO: Figure out better way to validate data (maybe in JS?)
    if not my_data["test_name"] and not my_data["tests"]:
        print("Form data was empty!")
        raise ValueError("Form was empty")

    # Create random ID for tests without user-provided test name
    if not my_data["test_name"]:
        my_data["test_name"] = str(uuid.uuid4())
    print(my_data)

    # TODO: Store test details (name + test names) into redis/db for further processing and run tests
    # TODO: Replace static arg values with variables again
    generate_testbed(hostname="csr1000v-1", os_type="iosxe", device_ip="131.226.217.143")
    job = q.enqueue(run_network_test, job_timeout="3m")

    # TODO: Provide some additional feedback in logs on job status
    print("Job is being processed!")