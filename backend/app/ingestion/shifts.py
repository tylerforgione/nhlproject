from nhlpy import NHLClient

from app.db.base import SessionLocal

from app.models.game import Game
from app.models.player import Player
from app.models.shift import Shift
from app.models.team import Team
from app.models.season import Season


def time_to_seconds(value: str | None):
    """
    Convert NHL MM:SS strings to integer seconds.

    Examples:
        "00:00" -> 0
        "01:18" -> 78
        "20:00" -> 1200
    """

    if not value:
        return None

    try:
        minutes, seconds = value.split(":")

        return int(minutes) * 60 + int(seconds)

    except (
        ValueError,
        AttributeError,
    ):
        return None


def ingest_shifts(
    db,
    client: NHLClient,
    game: Game,
    unknown_player_ids: set,
    unknown_team_ids: set,
):
    """
    Ingest every player shift for one game.

    NHL shift-chart data occasionally contains duplicate rows
    representing the exact same real-world player shift.

    A shift is considered identical when these fields match:

        game_id
        player_id
        period
        start_time_seconds
        end_time_seconds

    Returns:
        number of unique shifts processed
    """

    if game.game_state == "FUT":
        return 0

    data = client.game_center.shift_chart_data(str(game.id))

    if not data:
        return 0

    shifts = data.get(
        "data",
        [],
    )

    if not shifts:
        return 0

    processed = 0

    # -----------------------------------------------------
    # EXISTING SHIFTS
    # -----------------------------------------------------
    #
    # Load all previously stored shifts for this game once.
    #
    # This is much cheaper than doing one SELECT for every
    # shift and also makes reruns safe.

    existing_shifts = db.query(Shift).filter(Shift.game_id == game.id).all()

    existing_by_key = {
        (
            shift.player_id,
            shift.period,
            shift.start_time_seconds,
            shift.end_time_seconds,
        ): shift
        for shift in existing_shifts
    }

    # Tracks unique intervals encountered in this API response.
    #
    # This specifically protects us against records like the
    # Khudobin case where NHL returned five different shift
    # IDs for the exact same interval.
    seen_shift_keys = set()

    for shift in shifts:

        # -------------------------------------------------
        # SHIFT RECORD ONLY
        # -------------------------------------------------

        type_code = shift.get("typeCode")

        # 517 = player shift.
        #
        # The shift-chart endpoint also contains other
        # event-like rows that don't belong in this table.
        if type_code != 517:
            continue

        shift_id = shift.get("id")
        player_id = shift.get("playerId")
        team_id = shift.get("teamId")
        period = shift.get("period")

        if shift_id is None or player_id is None or team_id is None or period is None:
            continue

        # -------------------------------------------------
        # TIME VALUES
        # -------------------------------------------------

        start_time_seconds = time_to_seconds(shift.get("startTime"))

        end_time_seconds = time_to_seconds(shift.get("endTime"))

        duration_seconds = time_to_seconds(shift.get("duration"))

        if start_time_seconds is None or end_time_seconds is None:
            continue

        # -------------------------------------------------
        # NATURAL SHIFT KEY
        # -------------------------------------------------

        shift_key = (
            player_id,
            period,
            start_time_seconds,
            end_time_seconds,
        )

        # Exact duplicate interval in the NHL API response.
        #
        # Example:
        #
        # Khudobin:
        #
        #   shift ID A -> 04:23 - 04:30
        #   shift ID B -> 04:23 - 04:30
        #   shift ID C -> 04:23 - 04:30
        #
        # Store only the first.
        if shift_key in seen_shift_keys:
            continue

        seen_shift_keys.add(shift_key)

        # -------------------------------------------------
        # FOREIGN KEY GUARDS
        # -------------------------------------------------

        player = db.get(
            Player,
            player_id,
        )

        if player is None:
            unknown_player_ids.add(player_id)

            continue

        team = db.get(
            Team,
            team_id,
        )

        if team is None:
            unknown_team_ids.add(team_id)

            continue

        # -------------------------------------------------
        # UPSERT
        # -------------------------------------------------

        existing = existing_by_key.get(shift_key)

        if existing is None:
            existing = Shift(
                id=shift_id,
                game_id=game.id,
                player_id=player_id,
                team_id=team_id,
                period=period,
                shift_number=shift.get("shiftNumber"),
                start_time_seconds=(start_time_seconds),
                end_time_seconds=(end_time_seconds),
                duration_seconds=(duration_seconds),
            )

            db.add(existing)

            existing_by_key[shift_key] = existing

        else:
            # Update mutable values if this shift was
            # previously ingested.
            #
            # We intentionally DO NOT change existing.id.
            #
            # If the NHL later returns the same real-world
            # shift using a different duplicate row ID,
            # our already-stored canonical row keeps its ID.

            existing.team_id = team_id

            existing.shift_number = shift.get("shiftNumber")

            existing.duration_seconds = duration_seconds

        processed += 1

    return processed


def ingest_shifts_for_season(
    db,
    client: NHLClient,
    season_id: int,
    unknown_player_ids: set,
    unknown_team_ids: set,
    failed_game_ids: set,
):
    """
    Ingest all shifts for a season.

    Individual games use savepoints, while the actual commit
    happens once at the end of the season.
    """

    games = (
        db.query(Game)
        .filter(Game.season_id == season_id)
        .order_by(
            Game.game_date,
            Game.id,
        )
        .all()
    )

    game_count = 0
    shift_count = 0
    future_count = 0
    failed_count = 0

    print(f"Ingesting shifts for season " f"{season_id} ({len(games)} games)...")

    for game in games:

        if game.game_state == "FUT":
            future_count += 1
            continue

        try:
            # -------------------------------------------------
            # GAME SAVEPOINT
            # -------------------------------------------------
            #
            # If one game's shift data is malformed, only that
            # game's work gets rolled back.

            with db.begin_nested():

                processed = ingest_shifts(
                    db=db,
                    client=client,
                    game=game,
                    unknown_player_ids=(unknown_player_ids),
                    unknown_team_ids=(unknown_team_ids),
                )

                # Force database constraint errors to occur
                # while the game's savepoint is active.
                db.flush()

            game_count += 1
            shift_count += processed

        except Exception as e:

            failed_game_ids.add(game.id)

            failed_count += 1

            print(f"  Failed game " f"{game.id}: {e}")

            continue

    # -----------------------------------------------------
    # SEASON COMMIT
    # -----------------------------------------------------

    db.commit()

    print(
        f"Season {season_id}: "
        f"{game_count} games, "
        f"{shift_count} shifts, "
        f"{future_count} future, "
        f"{failed_count} failed"
    )


def ingest_all_shifts():

    client = NHLClient()
    db = SessionLocal()

    unknown_player_ids = set()
    unknown_team_ids = set()
    failed_game_ids = set()

    try:
        season_ids = [
            row[0]
            for row in (
                db.query(Game.season_id)
                .filter(Game.season_id >= 20102011)
                .distinct()
                .order_by(Game.season_id)
                .all()
            )
        ]

        print(f"Found {len(season_ids)} seasons")

        for season_id in season_ids:

            try:

                ingest_shifts_for_season(
                    db=db,
                    client=client,
                    season_id=season_id,
                    unknown_player_ids=(unknown_player_ids),
                    unknown_team_ids=(unknown_team_ids),
                    failed_game_ids=(failed_game_ids),
                )

            except Exception as e:

                db.rollback()

                print(f"Failed season " f"{season_id}: {e}")

                continue

    finally:
        db.close()

    # -----------------------------------------------------
    # FINAL SUMMARY
    # -----------------------------------------------------

    print()
    print("=" * 80)
    print("SHIFT INGESTION COMPLETE")
    print("=" * 80)

    if unknown_player_ids:

        print()
        print(f"Unknown player IDs " f"({len(unknown_player_ids)}):")

        for player_id in sorted(unknown_player_ids):
            print(f"  {player_id}")

    else:

        print()
        print("No unknown player IDs encountered.")

    if unknown_team_ids:

        print()
        print(f"Unknown team IDs " f"({len(unknown_team_ids)}):")

        for team_id in sorted(unknown_team_ids):
            print(f"  {team_id}")

    else:

        print()
        print("No unknown team IDs encountered.")

    if failed_game_ids:

        print()
        print(f"Failed game IDs " f"({len(failed_game_ids)}):")

        for game_id in sorted(failed_game_ids):
            print(f"  {game_id}")

    else:

        print()
        print("No games failed.")


if __name__ == "__main__":
    ingest_all_shifts()
