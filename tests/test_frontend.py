from fastapi.testclient import TestClient
from netcheck.main import app

# Initialize the test client
client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}