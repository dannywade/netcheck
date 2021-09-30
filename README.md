# NetCheck

## What is NetCheck?
A tool that allows network engineers to validate common changes and analyze their network using two popular network testing and analysis tools: pyATS and Batfish. NetCheck is built with a web UI and a RESTful API. The goal is to have full feature parity between the web UI and API, so that the user can interact with it however they wish.

## Why should I use NetCheck?
Upon installation, NetCheck works out of the box to help validate common changes and allow you to learn things about your network that you may not known before using the analysis portion of the tool.

## What is NetCheck built on?
The tool is built using Python and multiple Python libraries. Below is a breakdown of the different components used in this project.

*The lists below may change in the future. I will try to keep it updated as the tool progresses.*

**Frontend:**
- HTML 5
- Bootstrap CSS
- JavaScript/jQuery

**Backend:**
- FastAPI
- SQLModel
- SQLite
- pyATS/Genie
- Batfish
