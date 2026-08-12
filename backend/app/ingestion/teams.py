from nhlpy import NHLClient
from app.db.base import SessionLocal
from app.models.team import Team


def ingest_active_teams():
    client = NHLClient()
    db = SessionLocal()

    try:
        teams = client.teams.teams()

        for t in teams():
            team = db.get(Team, t["abbrev"])

            existing = (
                db.query(Team)
                .filter(Team.abbrev == t["abbrev"], Team.is_active)
                .first()
            )
    finally:
        pass
