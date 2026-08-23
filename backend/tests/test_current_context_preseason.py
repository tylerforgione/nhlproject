from datetime import date, timedelta

from app.models.game import Game
from app.models.season import Season
from app.models.team import Team


def test_current_context_uses_todays_preseason_game_as_the_active_phase(
    client, db_session
):
    today = date.today()
    completed_season = Season(
        id=20252026,
        standings_start=today - timedelta(days=300),
        standings_end=today - timedelta(days=120),
    )
    upcoming_season = Season(
        id=20262027,
        standings_start=today + timedelta(days=20),
        standings_end=today + timedelta(days=220),
    )
    home_team = Team(id=1, name="Boston Bruins", abbrev="BOS", is_nhl=True)
    away_team = Team(id=2, name="New York Rangers", abbrev="NYR", is_nhl=True)
    game = Game(
        id=2026010001,
        season_id=upcoming_season.id,
        game_type_id=1,
        game_date=today,
        home_team_id=home_team.id,
        away_team_id=away_team.id,
        neutral_site=False,
    )
    db_session.add_all(
        [completed_season, upcoming_season, home_team, away_team, game]
    )
    db_session.commit()

    response = client.get("/api/v1/current-context")

    assert response.status_code == 200
    assert response.json()["active_season_phase"] == "preseason"
    assert response.json()["schedule_season_id"] == 20262027
