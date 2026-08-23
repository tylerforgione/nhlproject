from nhlpy import NHLClient

from app.db.base import SessionLocal
from app.models.game import Game

# Import models needed for SQLAlchemy FK resolution.
from app.models.team import Team
from app.models.season import Season

from app.ingestion.game_events import ingest_play_by_play

GAME_IDS = [
    1975020438,
]


def main():
    client = NHLClient()
    db = SessionLocal()

    try:
        for game_id in GAME_IDS:
            print(f"Backfilling game events for {game_id}...")

            game = db.get(Game, game_id)

            if game is None:
                print(f"Game {game_id} not found in games table")
                continue

            try:
                events = ingest_play_by_play(
                    db=db,
                    client=client,
                    game=game,
                )

                # Force SQLAlchemy/database errors to happen here,
                # rather than waiting until the final commit.
                db.flush()

                print(f"Game {game_id}: " f"{events} events processed")

            except Exception as e:
                db.rollback()

                print(f"Failed game {game_id}: {e}")

                raise

        db.commit()

        print("Game event backfill complete.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
