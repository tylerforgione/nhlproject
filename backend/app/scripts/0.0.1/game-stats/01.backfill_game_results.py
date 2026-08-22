from nhlpy import NHLClient

from app.db.base import SessionLocal
from app.models.game import Game
from app.ingestion.game_results_boxscores import ingest_boxscore

GAME_IDS = [
    1977020349,
    1988020087,
    1992020925,
    2002020464,
    2019020471,
]


def main():
    client = NHLClient()
    db = SessionLocal()

    unknown_player_ids = set()

    try:
        for game_id in GAME_IDS:
            game = db.get(Game, game_id)

            if game is None:
                print(f"Game {game_id} does not exist in games table")
                continue

            try:
                with db.begin_nested():
                    ingest_boxscore(
                        db=db,
                        client=client,
                        game=game,
                        unknown_player_ids=unknown_player_ids,
                    )

                    db.flush()

                print(f"Fixed game {game_id}")

            except Exception as e:
                print(f"Still failed for game {game_id}: {e}")

        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

    if unknown_player_ids:
        print("\nUnknown player IDs:")

        for player_id in sorted(unknown_player_ids):
            print(f"  {player_id}")


if __name__ == "__main__":
    main()
