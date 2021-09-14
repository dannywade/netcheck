from fastapi import FastAPI, Request, Form
from fastapi.params import Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
import os
from datetime import datetime
# Local imports
from api.api_v1.api import api_router

app_dir = os.path.dirname(__file__)

api_description = "API used to validate and performs tests against your network"

app = FastAPI(description=api_description,
            version="V1",
            title="NetCheck API")

# API router
app.include_router(api_router, prefix="/api/v1")

# Link app to static files and templates
app.mount("/frontend/static", StaticFiles(directory=f"{app_dir}/frontend/static"), name="static")
templates = Jinja2Templates(directory=f"{app_dir}/frontend/templates")

# Frontend views
@app.get("/", response_class=HTMLResponse)
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
async def validation_results(request: Request, osType: str = Form(...), deviceIp: str = Form(...) ):
    date = datetime.date
    
    # TODO: Need to figure out how to run pyATS testscript most efficiently - easypy or standalone
    
    return templates.TemplateResponse("results.html", {"request": request, "date": date, "device_ip": deviceIp})