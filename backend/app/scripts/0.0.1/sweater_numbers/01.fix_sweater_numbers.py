from nhlpy import NHLClient

from app.db.base import SessionLocal
from app.models.roster import Roster
from app.models.team import Team
from app.models.player import Player
from app.models.season import Season


def main():
    client = NHLClient()
    db = SessionLocal()

    updated = 0
    not_found = []

    try:
        # Only roster rows that still need a sweater number
        rows = (
            db.query(Roster, Team)
            .join(
                Team,
                Roster.team_id == Team.id,
            )
            .filter(Roster.sweater_number.is_(None))
            .order_by(
                Roster.season_id,
                Team.abbrev,
            )
            .all()
        )

        # Group DB roster rows by team + season
        grouped = {}

        for roster, team in rows:
            key = (
                team.id,
                team.abbrev,
                roster.season_id,
            )

            grouped.setdefault(
                key,
                [],
            ).append(roster)

        print(f"Found {len(rows)} roster rows with no sweater number")

        print(f"Across {len(grouped)} team-season combinations")

        for (
            team_id,
            team_abbrev,
            season_id,
        ), roster_rows in grouped.items():

            try:
                api_roster = client.teams.team_roster(
                    team_abbr=team_abbrev,
                    season=str(season_id),
                )

            except Exception as e:
                print(f"Failed roster fetch for " f"{team_abbrev} {season_id}: {e}")
                continue

            all_players = (
                api_roster.get("forwards", [])
                + api_roster.get("defensemen", [])
                + api_roster.get("goalies", [])
            )

            # player_id -> sweater_number
            sweater_numbers = {
                p["id"]: p.get("sweaterNumber")
                for p in all_players
                if p.get("id") is not None
            }

            for roster in roster_rows:
                sweater_number = sweater_numbers.get(roster.player_id)

                if sweater_number is None:
                    not_found.append(
                        (
                            roster.player_id,
                            team_abbrev,
                            season_id,
                        )
                    )
                    continue

                roster.sweater_number = sweater_number
                updated += 1

            # Commit per team-season.
            db.commit()

            print(
                f"{team_abbrev} {season_id}: "
                f"processed {len(roster_rows)} roster rows"
            )

        print()
        print(f"Updated {updated} roster sweater numbers")

        if not_found:
            print()
            print(
                f"Could not find sweater number for " f"{len(not_found)} roster rows:"
            )

            for (
                player_id,
                team_abbrev,
                season_id,
            ) in not_found:
                print(
                    f"  player={player_id} "
                    f"team={team_abbrev} "
                    f"season={season_id}"
                )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
