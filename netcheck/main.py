import ast
import uuid
from dotenv import load_dotenv
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

# Local imports
from api.api_v1.api import api_router
from backend.models import TestResults, DeviceInventory
from backend.db import create_db_and_tables, create_dummy_data, engine
from helpers.validation import (
    generate_testbed,
    generate_datafile,
    run_pyats_job,
    get_pyats_results,
    parse_pyats_results,
    cleanup_pyats_results,
    cleanup_pyats_testbed,
    read_device_logs,
)
from inventory import device_connection, discover_device
from tasks import run_network_tests
from worker import conn

# Load .env values
load_dotenv()

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
    # Add dummy records for testing
    create_dummy_data()


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


@app.get("/inventory", response_class=HTMLResponse)
async def inventory(request: Request):
    add_status = None
    return templates.TemplateResponse(
        "inventory.html", {"request": request, "add_status": add_status}
    )


@app.get("/validation", response_class=HTMLResponse)
async def post_checks(request: Request):
    return templates.TemplateResponse("validation.html", {"request": request})


@app.get("/custom-validation", response_class=HTMLResponse)
async def custom_checks(request: Request):
    return templates.TemplateResponse("custom_validation.html", {"request": request})


@app.get("/analysis", response_class=HTMLResponse)
async def analysis(request: Request):
    return templates.TemplateResponse("analysis.html", {"request": request})


@app.get("/custom-results", response_class=HTMLResponse)
async def custom_results(request: Request):
    return templates.TemplateResponse("custom_results.html", {"request": request})


@app.get("/partials/results-table", response_class=HTMLResponse)
async def results_table(request: Request):
    with Session(engine) as session:
        all_test_results = session.exec(select(TestResults)).all()
    return templates.TemplateResponse(
        "partial_results_table.html", {"request": request, "results": all_test_results}
    )


@app.post("/search-inventory", response_class=HTMLResponse)
async def inventory_table(request: Request, search: str = Form(None)):
    if search is None:
        with Session(engine) as session:
            results = session.exec(select(DeviceInventory)).all()
            return templates.TemplateResponse(
                "partial_inventory_table.html",
                {"request": request, "results": results},
            )
    else:
        with Session(engine) as session:
            search_match = select(DeviceInventory).where(
                DeviceInventory.hostname.like("%" + search + "%")
            )
            results = session.exec(search_match)
            return templates.TemplateResponse(
                "partial_inventory_table.html",
                {"request": request, "results": results},
            )


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
    """
    Receives user data from custom validation page, parses data, and runs testcases.

    Example payload from frontend:
    {
        "test_name": "test1",
        "tests": ["Environment (CPU, Memory, etc.)"],
        "test_details": [
            { "param_name": "cpu_util", "param_value": "50" },
            { "param_name": "mem_util", "param_value": "80" }
        ]
    }
    """
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

    # Convert testcase parameters into dict for datafile
    tc_params = {}
    for item in my_data["test_details"]:
        param = {item["param_name"]: item["param_value"]}
        tc_params.update(param)

    print(tc_params)
    # TODO: Replace static arg values with variables again
    generate_testbed(
        hostname="csr1000v-1", os_type="iosxe", device_ip="131.226.217.143"
    )
    generate_datafile(tc_params)

    # Pass in list of tests from frontend and execute testscript(s) via pyATS Easypy
    job = q.enqueue(
        run_network_tests,
        test_name=my_data["test_name"],
        tests=my_data["tests"],
        job_timeout="3m",
    )

    # TODO: Provide some additional feedback in logs on job status
    print("Job is being processed!")


@app.post("/addDevice", response_class=HTMLResponse)
async def add_inventory_device(
    request: Request,
    deviceHostname: str = Form(...),
    deviceIp: str = Form(...),
):
    creds = {"username": os.getenv("NC_USER"), "password": os.getenv("NC_PASSWORD")}
    # May make this an async task to allow for quicker response to user
    device = device_connection(deviceIp, creds)
    if device is not None:
        device_record = discover_device(device)
        # If hostname isn't discovered, use the user's form input
        if device_record.hostname is None:
            device_record.hostname = deviceHostname
    else:
        device_record = None

    if device_record is not None:
        # Save device to the device inventory table
        with Session(engine) as session:
            session.add(device_record)
            session.commit()
            session.refresh(device_record)
            add_status = True
    else:
        add_status = False

    return templates.TemplateResponse(
        "inventory.html", {"request": request, "add_status": add_status}
    )
