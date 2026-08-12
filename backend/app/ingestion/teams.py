from nhlpy import NHLClient
from app.db.base import SessionLocal
from app.models.team import Team


def ingest_teams():
    client = NHLClient()
    db = SessionLocal()

    try:
        teams = client.teams.teams()

        for t in teams:
            existing = (
                db.query(Team)
                .filter(Team.abbrev == t["abbrev"], Team.last_season == "20252026")
                .first()
            )

            if existing:
                existing.conference = t["conference"]["name"]
                existing.division = t["division"]["name"]

        db.commit()
        print("Updated team conferences and divisions")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    ingest_teams()
