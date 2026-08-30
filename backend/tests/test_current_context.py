from datetime import date, timedelta

from app.domain.official_date import current_official_date
from app.main import app
from app.models.game import Game
from app.models.season import Season
from app.models.team import Team


def test_current_context_returns_the_active_regular_season(client, db_session):
    today = date(2026, 1, 15)
    app.dependency_overrides[current_official_date] = lambda: today
    completed_season = Season(
        id=20242025,
        standings_start=today - timedelta(days=400),
        standings_end=today - timedelta(days=200),
    )
    active_season = Season(
        id=20252026,
        standings_start=today - timedelta(days=30),
        standings_end=today + timedelta(days=120),
    )
    home_team = Team(id=1, name="Boston Bruins", abbrev="BOS", is_nhl=True)
    away_team = Team(id=2, name="New York Rangers", abbrev="NYR", is_nhl=True)
    game = Game(
        id=2025020001,
        season_id=active_season.id,
        game_type_id=2,
        game_date=today,
        home_team_id=home_team.id,
        away_team_id=away_team.id,
        neutral_site=False,
    )
    db_session.add_all(
        [completed_season, active_season, home_team, away_team, game]
    )
    db_session.commit()

    response = client.get("/api/v1/current-context")

    assert response.status_code == 200
    assert response.json() == {
        "official_date": today.isoformat(),
        "active_season_phase": "regular-season",
        "schedule_season_id": 20252026,
        "latest_completed_season_id": 20242025,
        "games_capability": {
            "state": "unknown",
            "explanation": "Schedule coverage has not been verified.",
        },
    }
