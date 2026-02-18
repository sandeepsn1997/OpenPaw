from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_agent_time_tool():
    response = client.post("/api/agent", json={"message": "what is the time?"})
    assert response.status_code == 200
    body = response.json()
    assert body["tool_used"] == "clock"
    assert "Current server time" in body["reply"]
