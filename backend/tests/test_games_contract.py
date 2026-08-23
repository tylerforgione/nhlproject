from datetime import date, datetime, timezone

from app.models.game import Game
from app.models.season import Season
from app.models.team import Team


def test_games_by_official_date_returns_a_scheduled_game(client, db_session):
    official_date = date(2026, 1, 15)
    season = Season(
        id=20252026,
        standings_start=date(2025, 10, 7),
        standings_end=date(2026, 4, 16),
    )
    away_team = Team(
        id=1,
        name="Boston Bruins",
        abbrev="BOS",
        logo="https://example.com/bos-light.svg",
        dark_logo="https://example.com/bos-dark.svg",
        is_nhl=True,
    )
    home_team = Team(
        id=2,
        name="New York Rangers",
        abbrev="NYR",
        logo="https://example.com/nyr-light.svg",
        dark_logo=None,
        is_nhl=True,
    )
    game = Game(
        id=2025020710,
        season_id=season.id,
        game_type_id=2,
        game_date=official_date,
        start_time_utc=datetime(2026, 1, 16, 0, 30, tzinfo=timezone.utc),
        home_team_id=home_team.id,
        away_team_id=away_team.id,
        venue=None,
        venue_timezone="America/New_York",
        neutral_site=False,
        game_state="FUT",
        game_schedule_state="OK",
    )
    db_session.add_all([season, away_team, home_team, game])
    db_session.commit()

    response = client.get(
        "/api/v1/games", params={"official_date": official_date.isoformat()}
    )

    assert response.status_code == 200
    assert response.json() == {
        "official_date": "2026-01-15",
        "capability": {"state": "available", "explanation": None},
        "games": [
            {
                "id": 2025020710,
                "season_id": 20252026,
                "game_type": "regular-season",
                "state": "scheduled",
                "official_date": "2026-01-15",
                "start_time_utc": "2026-01-16T00:30:00Z",
                "away_team": {
                    "id": 1,
                    "name": "Boston Bruins",
                    "abbreviation": "BOS",
                    "logo_url": "https://example.com/bos-light.svg",
                    "dark_logo_url": "https://example.com/bos-dark.svg",
                },
                "home_team": {
                    "id": 2,
                    "name": "New York Rangers",
                    "abbreviation": "NYR",
                    "logo_url": "https://example.com/nyr-light.svg",
                    "dark_logo_url": None,
                },
                "away_score": None,
                "home_score": None,
                "venue": None,
                "venue_timezone": "America/New_York",
                "neutral_site": False,
            }
        ],
    }
