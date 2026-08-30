from datetime import date

from app.models.game import Game
from app.models.season import Season
from app.models.team import Team


def test_games_by_official_date_identifies_a_preseason_game(client, db_session):
    official_date = date(2026, 9, 20)
    season = Season(
        id=20262027,
        standings_start=date(2026, 10, 6),
        standings_end=date(2027, 4, 15),
    )
    away_team = Team(id=1, name="Boston Bruins", abbrev="BOS", is_nhl=True)
    home_team = Team(id=2, name="New York Rangers", abbrev="NYR", is_nhl=True)
    game = Game(
        id=2026010010,
        season_id=season.id,
        game_type_id=1,
        game_date=official_date,
        home_team_id=home_team.id,
        away_team_id=away_team.id,
        neutral_site=False,
        game_state="FUT",
    )
    db_session.add_all([season, away_team, home_team, game])
    db_session.commit()

    response = client.get(
        "/api/v1/games", params={"official_date": official_date.isoformat()}
    )

    assert response.status_code == 200
    assert response.json()["games"][0]["game_type"] == "preseason"
