def test_games_by_official_date_returns_a_structured_validation_error(client):
    response = client.get(
        "/api/v1/games", params={"official_date": "not-a-date"}
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_request"
    assert response.json()["error"]["message"] == "Request validation failed"
    assert response.json()["error"]["details"][0]["field"] == "query.official_date"
