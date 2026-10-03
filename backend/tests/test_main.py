from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_returns_project_status() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"project": "SmartPark AI", "status": "running"}


def test_health_check_returns_healthy_status() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_health_check_accepts_the_vite_development_origin() -> None:
    response = client.get("/health", headers={"Origin": "http://localhost:5173"})

    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
