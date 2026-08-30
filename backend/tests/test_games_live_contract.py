from datetime import date

from app.models.game import Game
from app.models.game_result import GameResult
from app.models.season import Season
from app.models.team import Team


def test_games_by_official_date_identifies_a_live_playoff_game(client, db_session):
    official_date = date(2026, 5, 20)
    season = Season(
        id=20252026,
        standings_start=date(2025, 10, 7),
        standings_end=date(2026, 4, 16),
    )
    away_team = Team(id=1, name="Boston Bruins", abbrev="BOS", is_nhl=True)
    home_team = Team(id=2, name="New York Rangers", abbrev="NYR", is_nhl=True)
    game = Game(
        id=2025030311,
        season_id=season.id,
        game_type_id=3,
        game_date=official_date,
        home_team_id=home_team.id,
        away_team_id=away_team.id,
        neutral_site=False,
        game_state="LIVE",
    )
    result = GameResult(
        game_id=game.id,
        away_team_score=1,
        home_team_score=1,
        period_number=2,
    )
    db_session.add_all([season, away_team, home_team, game, result])
    db_session.commit()

    response = client.get(
        "/api/v1/games", params={"official_date": official_date.isoformat()}
    )

    assert response.status_code == 200
    assert response.json()["games"][0]["state"] == "live"
    assert response.json()["games"][0]["game_type"] == "playoffs"
