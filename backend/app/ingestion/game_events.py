from nhlpy import NHLClient

from app.db.base import SessionLocal

from app.models.game import Game
from app.models.game_event import GameEvent

# These imports ensure SQLAlchemy knows about tables
# referenced by GameEvent foreign keys.
from app.models.team import Team
from app.models.season import Season


def time_to_seconds(value: str | None):
    """
    Convert NHL MM:SS strings to seconds.

    Examples:
        "00:00" -> 0
        "12:34" -> 754
        "20:00" -> 1200
    """
    if not value:
        return None

    try:
        minutes, seconds = value.split(":")
        return int(minutes) * 60 + int(seconds)

    except (ValueError, AttributeError):
        return None


def ingest_play_by_play(
    db,
    client,
    game: Game,
):
    """
    Ingest every play-by-play event for one game.

    Returns:
        number of events processed
    """

    # Future games do not have PBP yet.
    if game.game_state == "FUT":
        return 0

    data = client.game_center.play_by_play(str(game.id))

    if not data:
        return 0

    plays = data.get("plays", [])

    processed = 0

    for play in plays:
        event_id = play.get("eventId")

        if event_id is None:
            continue

        period = play.get(
            "periodDescriptor",
            {},
        )

        details = play.get(
            "details",
            {},
        )

        # -------------------------------------------------
        # EVENT OWNER TEAM
        # -------------------------------------------------

        event_owner_team_id = details.get("eventOwnerTeamId")

        # Some events such as:
        #
        #   period-start
        #   stoppage
        #   period-end
        #
        # don't belong to either team.
        #
        # Also protect against unexpected API team IDs so
        # an event cannot break the foreign key constraint.
        if event_owner_team_id is not None:
            team = db.get(
                Team,
                event_owner_team_id,
            )

            if team is None:
                event_owner_team_id = None

        # -------------------------------------------------
        # FIND EXISTING EVENT
        # -------------------------------------------------

        existing = (
            db.query(GameEvent)
            .filter(
                GameEvent.game_id == game.id,
                GameEvent.event_id == event_id,
            )
            .first()
        )

        if existing is None:
            existing = GameEvent(
                game_id=game.id,
                event_id=event_id,
            )

            db.add(existing)

        # -------------------------------------------------
        # COMMON EVENT DATA
        # -------------------------------------------------

        existing.period_number = period.get("number")

        existing.period_type = period.get("periodType")

        existing.time_in_period = play.get("timeInPeriod")

        existing.time_remaining = play.get("timeRemaining")

        existing.situation_code = play.get("situationCode")

        existing.home_team_defending_side = play.get("homeTeamDefendingSide")

        existing.type_code = play.get("typeCode")

        existing.event_type = play.get("typeDescKey")

        existing.sort_order = play.get("sortOrder")

        # -------------------------------------------------
        # COMMON DETAILS
        # -------------------------------------------------

        existing.event_owner_team_id = event_owner_team_id

        existing.x_coord = details.get("xCoord")

        existing.y_coord = details.get("yCoord")

        existing.zone_code = details.get("zoneCode")

        # -------------------------------------------------
        # EVENT-SPECIFIC DETAILS
        # -------------------------------------------------

        # Store the entire details object so no information
        # is lost for event-specific fields such as:
        #
        #   shootingPlayerId
        #   goalieInNetId
        #   blockingPlayerId
        #   scoringPlayerId
        #   assist1PlayerId
        #   committedByPlayerId
        #   winningPlayerId
        #   shotType
        #   reason
        #   duration
        #   etc.
        #
        # The common fields above are intentionally still
        # present inside JSONB. Keeping the original API
        # payload makes this lossless and easier to debug.
        existing.details = details or None

        processed += 1

    return processed


def ingest_events_for_season(
    db,
    client,
    season_id: int,
    failed_game_ids: set,
):
    """
    Ingest all available play-by-play events for one season.

    The season is committed as one transaction.

    Individual games use savepoints so a bad game does not
    invalidate every other game in the season.
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
    event_count = 0
    future_count = 0
    failed_count = 0

    print(f"Ingesting play-by-play for season " f"{season_id} ({len(games)} games)...")

    for game in games:
        if game.game_state == "FUT":
            future_count += 1
            continue

        try:
            # One savepoint per game.
            #
            # If one game's PBP contains something unexpected,
            # only that game is rolled back.
            with db.begin_nested():
                events = ingest_play_by_play(
                    db=db,
                    client=client,
                    game=game,
                )

                # Make SQLAlchemy send this game's pending
                # changes now so database/constraint errors
                # occur inside this savepoint.
                db.flush()

            game_count += 1
            event_count += events

        except Exception as e:
            failed_game_ids.add(game.id)

            failed_count += 1

            print(f"  Failed game {game.id}: {e}")

            continue

    # -------------------------------------------------
    # SEASON COMMIT
    # -------------------------------------------------

    db.commit()

    print(
        f"Season {season_id}: "
        f"{game_count} games, "
        f"{event_count} events, "
        f"{future_count} future, "
        f"{failed_count} failed"
    )


def ingest_all_game_events():
    client = NHLClient()
    db = SessionLocal()

    failed_game_ids = set()

    try:
        season_ids = [
            row[0]
            for row in (
                db.query(Game.season_id).distinct().order_by(Game.season_id).all()
            )
        ]

        print(f"Found {len(season_ids)} seasons")

        for season_id in season_ids:
            try:
                ingest_events_for_season(
                    db=db,
                    client=client,
                    season_id=season_id,
                    failed_game_ids=(failed_game_ids),
                )

            except Exception as e:
                # Something outside an individual game's
                # savepoint failed, so discard this season.
                db.rollback()

                print(f"Failed season " f"{season_id}: {e}")

                continue

    finally:
        db.close()

    # -------------------------------------------------
    # SUMMARY
    # -------------------------------------------------

    print()
    print("=" * 80)
    print("PLAY-BY-PLAY INGESTION COMPLETE")
    print("=" * 80)

    if failed_game_ids:
        print()
        print(f"Failed game IDs " f"({len(failed_game_ids)}):")

        for game_id in sorted(failed_game_ids):
            print(f"  {game_id}")

    else:
        print()
        print("No games failed.")


if __name__ == "__main__":
    ingest_all_game_events()
