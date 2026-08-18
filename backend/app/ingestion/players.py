from nhlpy import NHLClient
from app.db.base import SessionLocal
from app.models.player import Player
from app.models.roster import Roster
from app.models.season import Season
from app.models.standing import Standing
from app.models.team import Team
from datetime import date


def ingest_players(season_id: int):
    client = NHLClient()
    db = SessionLocal()

    # Prevent duplicate objects within this season before commit()
    seen_player_ids = set()
    seen_roster_entries = set()

    try:
        teams = (
            db.query(Team)
            .join(Standing, Standing.team_id == Team.id)
            .filter(Standing.season_id == season_id)
            .all()
        )

        for team in teams:
            roster = client.teams.team_roster(
                team_abbr=team.abbrev, season=str(season_id)
            )

            all_players = (
                roster.get("forwards", [])
                + roster.get("defensemen", [])
                + roster.get("goalies", [])
            )

            for p in all_players:
                player_id = p["id"]

                # -------------------------
                # PLAYER
                # -------------------------
                if player_id not in seen_player_ids:
                    player = Player(
                        id=player_id,
                        first_name=p["firstName"]["default"],
                        last_name=p["lastName"]["default"],
                        position_code=p.get("positionCode"),
                        shoots_catches=p.get("shootsCatches"),
                        height_in_inches=p.get("heightInInches"),
                        weight_in_pounds=p.get("weightInPounds"),
                        height_in_centimeters=p.get("heightInCentimeters"),
                        weight_in_kilograms=p.get("weightInKilograms"),
                        birth_date=(
                            date.fromisoformat(p["birthDate"])
                            if p.get("birthDate")
                            else None
                        ),
                        birth_city=p.get("birthCity", {}).get("default"),
                        birth_country=p.get("birthCountry"),
                        birth_state_province=(
                            p.get("birthStateProvince", {}).get("default")
                        ),
                        headshot_url=p.get("headshot"),
                    )

                    db.merge(player)
                    seen_player_ids.add(player_id)

                # -------------------------
                # ROSTER ENTRY
                # -------------------------
                roster_key = (
                    player_id,
                    team.id,
                    season_id,
                )

                if roster_key not in seen_roster_entries:
                    roster_entry = Roster(
                        player_id=player_id,
                        team_id=team.id,
                        season_id=season_id,
                        sweater_number=p.get("sweaterNumber"),
                        position_code=p.get("positionCode"),
                    )

                    db.add(roster_entry)
                    seen_roster_entries.add(roster_key)

        db.commit()
        print(f"Ingested players and rosters for season {season_id}")

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()


if __name__ == "__main__":
    db = SessionLocal()

    season_ids = [row[0] for row in db.query(Standing.season_id).distinct().all()]

    db.close()

    for season_id in sorted(season_ids):
        print(f"Ingesting players for season {season_id}...")

        try:
            ingest_players(season_id)
        except Exception as e:
            print(f"Failed for season {season_id}: {e}")
            continue
