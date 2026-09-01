from datetime import timedelta

from app.models.game import Game
from app.models.season import Season
from app.models.team import Team


def test_current_context_uses_todays_playoff_game_as_the_active_phase(
    client, db_session, official_today
):
    today = official_today
    season = Season(
        id=20252026,
        standings_start=today - timedelta(days=220),
        standings_end=today - timedelta(days=10),
    )
    home_team = Team(id=1, name="Boston Bruins", abbrev="BOS", is_nhl=True)
    away_team = Team(id=2, name="New York Rangers", abbrev="NYR", is_nhl=True)
    game = Game(
        id=2025030417,
        season_id=season.id,
        game_type_id=3,
        game_date=today,
        home_team_id=home_team.id,
        away_team_id=away_team.id,
        neutral_site=False,
    )
    db_session.add_all([season, home_team, away_team, game])
    db_session.commit()

    response = client.get("/api/v1/current-context")

    assert response.status_code == 200
    assert response.json()["active_season_phase"] == "playoffs"
    assert response.json()["schedule_season_id"] == 20252026


def test_current_context_keeps_the_playoff_phase_on_an_off_day(
    client, db_session, official_today
):
    today = official_today
    season = Season(
        id=20252026,
        standings_start=today - timedelta(days=220),
        standings_end=today - timedelta(days=30),
    )
    home_team = Team(id=1, name="Boston Bruins", abbrev="BOS", is_nhl=True)
    away_team = Team(id=2, name="New York Rangers", abbrev="NYR", is_nhl=True)
    games = [
        Game(
            id=2025030416,
            season_id=season.id,
            game_type_id=3,
            game_date=today - timedelta(days=1),
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            neutral_site=False,
        ),
        Game(
            id=2025030417,
            season_id=season.id,
            game_type_id=3,
            game_date=today + timedelta(days=1),
            home_team_id=away_team.id,
            away_team_id=home_team.id,
            neutral_site=False,
        ),
    ]
    db_session.add_all([season, home_team, away_team, *games])
    db_session.commit()

    response = client.get("/api/v1/current-context")

    assert response.status_code == 200
    assert response.json()["active_season_phase"] == "playoffs"
    assert response.json()["schedule_season_id"] == 20252026
