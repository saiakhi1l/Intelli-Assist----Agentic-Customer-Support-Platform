from fastapi.testclient import TestClient

from intelli_assist.api import app


def test_health_live():
    with TestClient(app) as client:
        response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json()["status"] == "alive"