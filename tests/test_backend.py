from datetime import datetime
from fastapi.testclient import TestClient
from netcheck.main import app, create_test_results, create_inventory_devices
from netcheck.backend.db import create_db_and_tables

# Initialize the test client
client = TestClient(app)
# Create test DB and dummy entries
create_db_and_tables()
create_test_results()
create_inventory_devices()

# Testing the API
def test_api_root():
    response = client.get("/")
    assert response.status_code == 200


### TESTS FOR VALIDATION ENDPOINTS ###
def test_api_validation_test_results():
    response = client.get("/api/v1/validation/tests")
    assert response.status_code == 200


def test_api_validation_one_test_result():
    response = client.get("/api/v1/validation/tests/1")
    assert response.status_code == 200


def test_api_validation_delete_test_result():
    response = client.delete("/api/v1/validation/tests/1")
    assert response.status_code == 204


### TESTS FOR INVENTORY ENDPOINTS ###
def test_api_inventory_device_results():
    response = client.get("/api/v1/inventory/devices")
    assert response.status_code == 200


def test_api_inventory_one_device_result():
    response = client.get("/api/v1/inventory/devices/1")
    assert response.status_code == 200


def test_api_inventory_delete_device_result():
    response = client.delete("/api/v1/inventory/devices/1")
    assert response.status_code == 204
