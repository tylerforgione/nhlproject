def test_current_context_returns_a_structured_error_when_no_season_exists(client):
    response = client.get("/api/v1/current-context")

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "current_context_unavailable",
            "message": "Current NHL context is unavailable",
            "details": [],
        }
    }
