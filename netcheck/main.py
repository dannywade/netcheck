from fastapi import FastAPI, Request, Form
from fastapi.params import Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.future import select
from sqlmodel import SQLModel, Session
import os
import shutil
from datetime import datetime
import yaml

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

# Run the app: uvicorn main:app --reload

app_dir = os.path.dirname(__file__)

api_description = "API used to validate and performs tests against your network"

app = FastAPI(description=api_description, version="V1", title="NetCheck API")

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


# Used to create dummy records in DB
create_db_and_tables()
create_test_results()
select_test_results()

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
