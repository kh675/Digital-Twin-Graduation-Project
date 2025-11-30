# tests/test_create_digital_twin.py
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_create_twin_minimal():
    payload = {
        "name":"UT Student",
        "email":"u@test",
        "gpa":3.0,
        "technical_skills":["Python"], 
        "preferred_track": "Data Science"
    }
    r = client.post("/create_digital_twin", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "student_id" in data
    assert "digital_twin" in data
