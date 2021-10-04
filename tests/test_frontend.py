from fastapi.testclient import TestClient
from netcheck.main import app

# Initialize the test client
client = TestClient(app)


def test_index_page():
    response = client.get("/")
    assert response.status_code == 200
    assert response.template.name == "index.html"
    assert "request" in response.context


def test_about_page():
    response = client.get("/about")
    assert response.status_code == 200
    assert response.template.name == "about.html"
    assert "request" in response.context


def test_validation_page():
    response = client.get("/validation")
    assert response.status_code == 200
    assert response.template.name == "validation.html"
    assert "request" in response.context


def test_analysis_page():
    response = client.get("/analysis")
    assert response.status_code == 200
    assert response.template.name == "analysis.html"
    assert "request" in response.context
