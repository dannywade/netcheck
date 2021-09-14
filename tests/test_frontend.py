from fastapi.testclient import TestClient
from netcheck.main import app

# Initialize the test client
client = TestClient(app)

def test_index_page():
    response = client.get("/")
    assert response.status_code == 200

def test_about_page():
    response = client.get("/about")
    assert response.status_code == 200

def test_validation_page():
    response = client.get("/validation")
    assert response.status_code == 200

def test_analysis_page():
    response = client.get("/analysis")
    assert response.status_code == 200