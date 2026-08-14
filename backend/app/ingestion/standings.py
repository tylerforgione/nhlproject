from nhlpy import NHLClient
from app.db.base import SessionLocal
from app.models.standing import Standing


def ingest_standings():
    client = NHLClient()
    db = SessionLocal()

    try:
        standings = client.standings.league_standings()

        for s in standings:
            standing = Standing()
            db.merge()

        db.commit()
        print(f"Seeded {len(standings)} years of standings")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
