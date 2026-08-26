from fastapi.testclient import TestClient

from app.db.base import get_db
from app.main import app


def test_public_api_returns_a_structured_unexpected_error():
    def unavailable_database():
        raise RuntimeError("database credentials must not leak")

    app.dependency_overrides[get_db] = unavailable_database

    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get("/api/v1/games?official_date=2026-01-15")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "internal_server_error",
            "message": "The request could not be completed",
            "details": [],
        }
    }
