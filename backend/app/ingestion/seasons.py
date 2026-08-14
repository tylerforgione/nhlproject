from nhlpy import NHLClient
from app.db.base import SessionLocal
from app.models.season import Season
from datetime import date


def ingest_seasons():
    client = NHLClient()
    db = SessionLocal()

    try:
        seasons = client.standings.season_standing_manifest()

        for s in seasons:
            season = Season(
                id=s["id"],
                conferences_in_use=s["conferencesInUse"],
                divisions_in_use=s["divisionsInUse"],
                point_for_ot_loss_in_use=s["pointForOTlossInUse"],
                regulation_wins_in_use=s["regulationWinsInUse"],
                row_in_use=s["rowInUse"],
                standings_start=date.fromisoformat(s["standingsStart"]),
                standings_end=date.fromisoformat(s["standingsEnd"]),
                ties_in_use=s["tiesInUse"],
                wildcard_in_use=s["wildcardInUse"],
            )
            db.merge(season)

        db.commit()
        print(f"Seeded {len(seasons)} seasons.")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    ingest_seasons()
