from datetime import date, datetime

from nhlpy import NHLClient

from app.db.base import SessionLocal
from app.models.game import Game
from app.models.season import Season
from app.models.standing import Standing
from app.models.team import Team


def parse_utc_datetime(value: str | None):
    if not value:
        return None

    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def ingest_games_for_season(season_id: int):
    client = NHLClient()
    db = SessionLocal()

    seen_game_ids = set()
    ingested_game_count = 0

    # Keyed by the NHL API team ID so each unknown team
    # only gets reported once.
    unknown_teams = {}

    try:
        # Only use NHL teams to request schedules.
        #
        # Non-NHL teams such as historical PCHA teams or
        # exhibition opponents may exist in our teams table,
        # but we don't expect the NHL club-schedule endpoint
        # to provide their full schedules.
        teams = (
            db.query(Team)
            .join(
                Standing,
                Standing.team_id == Team.id,
            )
            .filter(
                Standing.season_id == season_id,
                Team.is_nhl.is_(True),
            )
            .all()
        )

        for team in teams:
            try:
                schedule = client.schedule.team_season_schedule(
                    team_abbr=team.abbrev,
                    season=str(season_id),
                )

            except Exception as e:
                print(f"Failed to get schedule for " f"{team.abbrev} {season_id}: {e}")
                continue

            games = schedule.get("games", [])

            for g in games:
                game_id = g.get("id")

                if game_id is None:
                    continue

                if game_id in seen_game_ids:
                    continue

                seen_game_ids.add(game_id)

                game_type_id = g.get("gameType")

                home_api = g.get("homeTeam", {})
                away_api = g.get("awayTeam", {})

                home_team_id = home_api.get("id")
                away_team_id = away_api.get("id")

                if home_team_id is None or away_team_id is None:
                    print(f"Skipping game {game_id}: " f"missing home/away team ID")
                    continue

                # -----------------------------------------
                # RESOLVE TEAMS
                # -----------------------------------------

                home_team = db.get(
                    Team,
                    home_team_id,
                )

                away_team = db.get(
                    Team,
                    away_team_id,
                )

                # A known non-NHL team is perfectly valid.
                #
                # The only thing that prevents us from
                # inserting the game is a team that doesn't
                # exist in our teams table at all.

                if home_team is None:
                    unknown_teams[home_team_id] = {
                        "id": home_team_id,
                        "abbrev": home_api.get("abbrev"),
                        "name": (home_api.get("commonName", {}).get("default")),
                        "season": season_id,
                        "game_id": game_id,
                        "game_type_id": game_type_id,
                    }

                if away_team is None:
                    unknown_teams[away_team_id] = {
                        "id": away_team_id,
                        "abbrev": away_api.get("abbrev"),
                        "name": (away_api.get("commonName", {}).get("default")),
                        "season": season_id,
                        "game_id": game_id,
                        "game_type_id": game_type_id,
                    }

                if home_team is None or away_team is None:
                    continue

                # -----------------------------------------
                # GAME DATE
                # -----------------------------------------

                game_date = (
                    date.fromisoformat(g["gameDate"]) if g.get("gameDate") else None
                )

                # -----------------------------------------
                # GAME
                # -----------------------------------------

                game = Game(
                    id=game_id,
                    season_id=g["season"],
                    game_type_id=game_type_id,
                    game_date=game_date,
                    start_time_utc=(parse_utc_datetime(g.get("startTimeUTC"))),
                    # Use our resolved Team IDs.
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    venue=(
                        g.get(
                            "venue",
                            {},
                        ).get("default")
                    ),
                    venue_timezone=g.get("venueTimezone"),
                    neutral_site=g.get(
                        "neutralSite",
                        False,
                    ),
                    game_state=g.get("gameState"),
                    game_schedule_state=g.get("gameScheduleState"),
                )

                db.merge(game)

                ingested_game_count += 1

        db.commit()

        print(f"Ingested {ingested_game_count} games " f"for season {season_id}")

        return unknown_teams

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    db = SessionLocal()

    season_ids = [row[0] for row in (db.query(Standing.season_id).distinct().all())]

    db.close()

    all_unknown_teams = {}

    for season_id in sorted(season_ids):
        print(f"Ingesting games for season " f"{season_id}...")

        try:
            unknown_teams = ingest_games_for_season(season_id)

            # Keep the first useful example we find
            # for each unknown team.
            for team_id, team_data in unknown_teams.items():
                if team_id not in all_unknown_teams:
                    all_unknown_teams[team_id] = team_data

        except Exception as e:
            print(f"Failed for season " f"{season_id}: {e}")
            continue

    print()
    print("=" * 80)
    print("GAME INGESTION COMPLETE")
    print("=" * 80)

    if all_unknown_teams:
        print()
        print("Unknown teams encountered:")

        for team_id in sorted(all_unknown_teams):
            team = all_unknown_teams[team_id]

            print(
                f"  id={team['id']} | "
                f"abbrev={team['abbrev']} | "
                f"name={team['name']} | "
                f"season={team['season']} | "
                f"game_type={team['game_type_id']} | "
                f"example_game={team['game_id']}"
            )

    else:
        print()
        print("No unknown teams encountered.")
