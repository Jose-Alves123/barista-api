from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_ping():
    response = client.get("/beverages")
    assert response.status_code == 200