from datetime import timedelta

from app.models.season import Season


def test_current_context_uses_the_upcoming_schedule_season_in_the_offseason(
    client, db_session, official_today
):
    today = official_today
    completed_season = Season(
        id=20252026,
        standings_start=today - timedelta(days=240),
        standings_end=today - timedelta(days=30),
    )
    upcoming_season = Season(
        id=20262027,
        standings_start=today + timedelta(days=60),
        standings_end=today + timedelta(days=240),
    )
    db_session.add_all([completed_season, upcoming_season])
    db_session.commit()

    response = client.get("/api/v1/current-context")

    assert response.status_code == 200
    assert response.json() == {
        "official_date": today.isoformat(),
        "active_season_phase": "offseason",
        "schedule_season_id": 20262027,
        "latest_completed_season_id": 20252026,
        "games_capability": {
            "state": "unknown",
            "explanation": "Schedule coverage has not been verified.",
        },
    }
