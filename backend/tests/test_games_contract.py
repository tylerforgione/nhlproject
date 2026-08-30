from datetime import date, datetime, timezone

import pytest

from app.models.game import Game
from app.models.season import Season
from app.models.team import Team


def test_games_by_official_date_returns_an_empty_collection(client):
    response = client.get(
        "/api/v1/games", params={"official_date": "2026-01-15"}
    )

    assert response.status_code == 200
    assert response.json()["official_date"] == "2026-01-15"
    assert response.json()["season_id"] is None
    assert response.json()["game_type"] is None
    assert response.json()["games"] == []


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
        "season_id": None,
        "game_type": None,
        "freshness": {
            "state": "unknown",
            "updated_at": None,
            "explanation": "Schedule freshness has not been verified.",
        },
        "capability": {
            "state": "unknown",
            "explanation": "Schedule coverage has not been verified.",
        },
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


def test_games_by_official_date_preserves_an_unknown_upstream_state(
    client, db_session
):
    official_date = date(2026, 1, 15)
    season = Season(
        id=20252026,
        standings_start=date(2025, 10, 7),
        standings_end=date(2026, 4, 16),
    )
    away_team = Team(id=1, name="Boston Bruins", abbrev="BOS", is_nhl=True)
    home_team = Team(id=2, name="New York Rangers", abbrev="NYR", is_nhl=True)
    game = Game(
        id=2025020710,
        season_id=season.id,
        game_type_id=2,
        game_date=official_date,
        home_team_id=home_team.id,
        away_team_id=away_team.id,
        neutral_site=False,
        game_state="UNRECOGNIZED",
    )
    db_session.add_all([season, away_team, home_team, game])
    db_session.commit()

    response = client.get(
        "/api/v1/games", params={"official_date": official_date.isoformat()}
    )

    assert response.status_code == 200
    assert response.json()["games"][0]["state"] == "unknown"


def test_games_by_official_date_applies_season_and_game_type_reference_state(
    client, db_session
):
    official_date = date(2026, 5, 15)
    seasons = [
        Season(
            id=20242025,
            standings_start=date(2024, 10, 4),
            standings_end=date(2025, 4, 17),
        ),
        Season(
            id=20252026,
            standings_start=date(2025, 10, 7),
            standings_end=date(2026, 4, 16),
        ),
    ]
    away_team = Team(id=1, name="Boston Bruins", abbrev="BOS", is_nhl=True)
    home_team = Team(id=2, name="New York Rangers", abbrev="NYR", is_nhl=True)
    games = [
        Game(
            id=2024030111,
            season_id=20242025,
            game_type_id=3,
            game_date=official_date,
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            neutral_site=False,
            game_state="FINAL",
        ),
        Game(
            id=2025030111,
            season_id=20252026,
            game_type_id=3,
            game_date=official_date,
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            neutral_site=False,
            game_state="LIVE",
        ),
    ]
    db_session.add_all([*seasons, away_team, home_team, *games])
    db_session.commit()

    response = client.get(
        "/api/v1/games",
        params={
            "official_date": official_date.isoformat(),
            "season_id": 20252026,
            "game_type": "playoffs",
        },
    )

    assert response.status_code == 200
    assert response.json()["season_id"] == 20252026
    assert response.json()["game_type"] == "playoffs"
    assert [game["id"] for game in response.json()["games"]] == [2025030111]


def test_games_by_official_date_applies_only_the_requested_schedule_season(
    client, db_session
):
    official_date = date(2026, 5, 15)
    seasons = [
        Season(
            id=20242025,
            standings_start=date(2024, 10, 4),
            standings_end=date(2025, 4, 17),
        ),
        Season(
            id=20252026,
            standings_start=date(2025, 10, 7),
            standings_end=date(2026, 4, 16),
        ),
    ]
    away_team = Team(id=1, name="Boston Bruins", abbrev="BOS", is_nhl=True)
    home_team = Team(id=2, name="New York Rangers", abbrev="NYR", is_nhl=True)
    games = [
        Game(
            id=2024030111,
            season_id=20242025,
            game_type_id=3,
            game_date=official_date,
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            neutral_site=False,
        ),
        Game(
            id=2025010111,
            season_id=20252026,
            game_type_id=1,
            game_date=official_date,
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            neutral_site=False,
        ),
        Game(
            id=2025020111,
            season_id=20252026,
            game_type_id=2,
            game_date=official_date,
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            neutral_site=False,
        ),
    ]
    db_session.add_all([*seasons, away_team, home_team, *games])
    db_session.commit()

    response = client.get(
        "/api/v1/games",
        params={
            "official_date": official_date.isoformat(),
            "season_id": 20252026,
        },
    )

    assert response.status_code == 200
    assert response.json()["season_id"] == 20252026
    assert response.json()["game_type"] is None
    assert [game["id"] for game in response.json()["games"]] == [
        2025010111,
        2025020111,
    ]


@pytest.mark.parametrize(
    ("game_type", "expected_ids"),
    [
        ("preseason", [2024010001, 2025010001]),
        ("regular-season", [2024020001, 2025020001]),
        ("playoffs", [2024030001, 2025030001]),
    ],
)
def test_games_by_official_date_applies_only_the_requested_game_type(
    client, db_session, game_type, expected_ids
):
    official_date = date(2026, 5, 15)
    seasons = [
        Season(
            id=20242025,
            standings_start=date(2024, 10, 4),
            standings_end=date(2025, 4, 17),
        ),
        Season(
            id=20252026,
            standings_start=date(2025, 10, 7),
            standings_end=date(2026, 4, 16),
        ),
    ]
    away_team = Team(id=1, name="Boston Bruins", abbrev="BOS", is_nhl=True)
    home_team = Team(id=2, name="New York Rangers", abbrev="NYR", is_nhl=True)
    games = [
        Game(
            id=season_prefix + type_id * 10000 + 1,
            season_id=season_id,
            game_type_id=type_id,
            game_date=official_date,
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            neutral_site=False,
        )
        for season_prefix, season_id in [
            (2024000000, 20242025),
            (2025000000, 20252026),
        ]
        for type_id in [1, 2, 3]
    ]
    db_session.add_all([*seasons, away_team, home_team, *games])
    db_session.commit()

    response = client.get(
        "/api/v1/games",
        params={
            "official_date": official_date.isoformat(),
            "game_type": game_type,
        },
    )

    assert response.status_code == 200
    assert response.json()["season_id"] is None
    assert response.json()["game_type"] == game_type
    assert [game["id"] for game in response.json()["games"]] == expected_ids
    assert {game["game_type"] for game in response.json()["games"]} == {
        game_type
    }


def test_games_by_official_date_orders_known_starts_before_missing_starts(
    client, db_session
):
    official_date = date(2026, 1, 15)
    season = Season(
        id=20252026,
        standings_start=date(2025, 10, 7),
        standings_end=date(2026, 4, 16),
    )
    away_team = Team(id=1, name="Boston Bruins", abbrev="BOS", is_nhl=True)
    home_team = Team(id=2, name="New York Rangers", abbrev="NYR", is_nhl=True)
    games = [
        Game(
            id=2025020004,
            season_id=season.id,
            game_type_id=2,
            game_date=official_date,
            start_time_utc=None,
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            neutral_site=False,
        ),
        Game(
            id=2025020005,
            season_id=season.id,
            game_type_id=2,
            game_date=official_date,
            start_time_utc=datetime(2026, 1, 16, 2, tzinfo=timezone.utc),
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            neutral_site=False,
        ),
        Game(
            id=2025020003,
            season_id=season.id,
            game_type_id=2,
            game_date=official_date,
            start_time_utc=datetime(2026, 1, 16, 1, tzinfo=timezone.utc),
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            neutral_site=False,
        ),
        Game(
            id=2025020002,
            season_id=season.id,
            game_type_id=2,
            game_date=official_date,
            start_time_utc=None,
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            neutral_site=False,
        ),
        Game(
            id=2025020001,
            season_id=season.id,
            game_type_id=2,
            game_date=official_date,
            start_time_utc=datetime(2026, 1, 16, 1, tzinfo=timezone.utc),
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            neutral_site=False,
        ),
    ]
    db_session.add_all([season, away_team, home_team, *games])
    db_session.commit()

    response = client.get(
        "/api/v1/games", params={"official_date": official_date.isoformat()}
    )

    assert response.status_code == 200
    assert [game["id"] for game in response.json()["games"]] == [
        2025020001,
        2025020003,
        2025020005,
        2025020002,
        2025020004,
    ]
