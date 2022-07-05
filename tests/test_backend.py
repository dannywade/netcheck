from datetime import datetime
from fastapi.testclient import TestClient
from netcheck.main import app, create_test_results
from netcheck.backend.db import create_db_and_tables

# Initialize the test client
client = TestClient(app)
# Create test DB and dummy entries
create_db_and_tables()
create_test_results()

# Testing the API
def test_api_root():
    response = client.get("/")
    assert response.status_code == 200


### TESTS FOR PYATS (VALIDATION) ENDPOINTS ###
def test_api_pyats_test_results():
    response = client.get("/api/v1/pyats/tests")
    assert response.status_code == 200


def test_api_pyats_one_test_result():
    response = client.get("/api/v1/pyats/tests/1")
    assert response.status_code == 200


def test_api_pyats_delete_test_result():
    response = client.delete("/api/v1/pyats/tests/1")
    assert response.status_code == 200
