# NetCheck

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![codecov](https://codecov.io/gh/dannywade/netcheck/branch/master/graph/badge.svg?token=A4Y64P0Q2W)](https://codecov.io/gh/dannywade/netcheck)

## What is NetCheck?
A tool that allows network engineers to validate common changes and analyze their network using two popular network testing and analysis tools: pyATS and Batfish (TBD). NetCheck is built with a web UI and a RESTful API. The goal is to have full feature parity between the web UI and API, so that the user can interact with it however they wish.

## Demo
This demo shows how a user can select specific testcases based on their testing requirements. Once testcases are selected, the user fills out the details under each testcase. The details section allows the user to document their expectations for each testcase result. Once the details are completed for each testcase, run the test, and you will see the test results under the 'Results' link.

https://user-images.githubusercontent.com/13680237/185807330-7a9e8dc6-66bf-41df-b9ca-1d8beb889df3.mov

## Why should I use NetCheck?
Upon installation, NetCheck works out of the box to help validate common changes and allow you to learn things about your network that you may not known before using the analysis portion of the tool.

## What is NetCheck built on?
The tool is built using Python and multiple Python libraries. Below is a breakdown of the different components used in this project.

*The lists below may change in the future. I will try to keep it updated as the tool progresses.*

**Frontend:**
- HTML 5
- Bootstrap CSS
- JavaScript/jQuery/jQuery UI
- htmx

**Backend:**
- FastAPI
- SQLModel
- SQLite
- pyATS/Genie
- *Batfish (TBD)*
