from fastapi.testclient import TestClient
from netcheck.main import app

# Initialize the test client
client = TestClient(app)

# Testing the API
def test_api_root():
    response = client.get("/")
    assert response.status_code == 200


def test_api_pyats_test_results():
    response = client.get("/api/v1/pyats/tests")
    assert response.status_code == 200


def test_api_pyats_one_test_result():
    response = client.get("/api/v1/pyats/tests/1")
    assert response.status_code == 200
