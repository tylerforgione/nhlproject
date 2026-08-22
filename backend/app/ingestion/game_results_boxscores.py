from nhlpy import NHLClient

from app.db.base import SessionLocal

from app.models.game import Game
from app.models.game_result import GameResult
from app.models.skater_game_stats import SkaterGameStats
from app.models.goalie_game_stats import GoalieGameStats

from app.models.player import Player
from app.models.team import Team
from app.models.season import Season


def toi_to_seconds(toi: str | None):
    """
    Convert NHL time strings such as:

        "16:00" -> 960
        "59:04" -> 3544

    Returns None if no TOI was supplied.
    """
    if not toi:
        return None

    try:
        minutes, seconds = toi.split(":")
        return int(minutes) * 60 + int(seconds)

    except (ValueError, AttributeError):
        return None


def parse_shot_split(value: str | None):
    """
    NHL goalie boxscores return situation shots as strings such as:

        "34/37"

    Meaning:

        34 saves
        37 shots against

    Returns:

        (saves, shots_against)

    Missing historical data returns:

        (None, None)
    """
    if not value:
        return None, None

    try:
        saves, shots = value.split("/")
        return int(saves), int(shots)

    except (ValueError, AttributeError):
        return None, None


def upsert_game_result(db, game: Game, boxscore: dict):
    home = boxscore.get("homeTeam", {})
    away = boxscore.get("awayTeam", {})

    period = boxscore.get("periodDescriptor", {})
    clock = boxscore.get("clock", {})
    outcome = boxscore.get("gameOutcome", {})

    result = db.get(
        GameResult,
        game.id,
    )

    if result is None:
        result = GameResult(
            game_id=game.id,
        )

        db.add(result)

    result.home_team_score = home.get("score")
    result.away_team_score = away.get("score")

    result.home_team_sog = home.get("sog")
    result.away_team_sog = away.get("sog")

    result.period_number = period.get("number")
    result.period_type = period.get("periodType")

    result.time_remaining = clock.get("timeRemaining")
    result.seconds_remaining = clock.get("secondsRemaining")

    result.clock_running = clock.get("running")
    result.in_intermission = clock.get("inIntermission")

    result.last_period_type = outcome.get("lastPeriodType")


def upsert_skater_stats(
    db,
    game: Game,
    team_id: int,
    player_data: dict,
    unknown_player_ids: set,
):
    player_id = player_data.get("playerId")

    if player_id is None:
        return

    player = db.get(
        Player,
        player_id,
    )

    if player is None:
        unknown_player_ids.add(player_id)
        return

    existing = (
        db.query(SkaterGameStats)
        .filter(
            SkaterGameStats.game_id == game.id,
            SkaterGameStats.player_id == player_id,
        )
        .first()
    )

    if existing is None:
        existing = SkaterGameStats(
            game_id=game.id,
            player_id=player_id,
            team_id=team_id,
        )

        db.add(existing)

    existing.team_id = team_id

    existing.sweater_number = player_data.get("sweaterNumber")

    existing.position_code = player_data.get("position")

    existing.goals = player_data.get("goals")
    existing.assists = player_data.get("assists")
    existing.points = player_data.get("points")

    existing.plus_minus = player_data.get("plusMinus")

    existing.pim = player_data.get("pim")

    existing.hits = player_data.get("hits")

    existing.power_play_goals = player_data.get("powerPlayGoals")

    existing.shots_on_goal = player_data.get("sog")

    existing.faceoff_winning_pctg = player_data.get("faceoffWinningPctg")

    existing.toi_seconds = toi_to_seconds(player_data.get("toi"))

    existing.blocked_shots = player_data.get("blockedShots")

    existing.shifts = player_data.get("shifts")

    existing.giveaways = player_data.get("giveaways")

    existing.takeaways = player_data.get("takeaways")


def upsert_goalie_stats(
    db,
    game: Game,
    team_id: int,
    player_data: dict,
    unknown_player_ids: set,
):
    player_id = player_data.get("playerId")

    if player_id is None:
        return

    player = db.get(
        Player,
        player_id,
    )

    if player is None:
        unknown_player_ids.add(player_id)
        return

    (
        even_strength_saves,
        even_strength_shots,
    ) = parse_shot_split(player_data.get("evenStrengthShotsAgainst"))

    (
        power_play_saves,
        power_play_shots,
    ) = parse_shot_split(player_data.get("powerPlayShotsAgainst"))

    (
        shorthanded_saves,
        shorthanded_shots,
    ) = parse_shot_split(player_data.get("shorthandedShotsAgainst"))

    existing = (
        db.query(GoalieGameStats)
        .filter(
            GoalieGameStats.game_id == game.id,
            GoalieGameStats.player_id == player_id,
        )
        .first()
    )

    if existing is None:
        existing = GoalieGameStats(
            game_id=game.id,
            player_id=player_id,
            team_id=team_id,
        )

        db.add(existing)

    existing.team_id = team_id

    existing.sweater_number = player_data.get("sweaterNumber")

    existing.starter = player_data.get("starter")

    existing.decision = player_data.get("decision")

    existing.pim = player_data.get("pim")

    existing.goals_against = player_data.get("goalsAgainst")

    existing.even_strength_goals_against = player_data.get("evenStrengthGoalsAgainst")

    existing.power_play_goals_against = player_data.get("powerPlayGoalsAgainst")

    existing.shorthanded_goals_against = player_data.get("shorthandedGoalsAgainst")

    existing.saves = player_data.get("saves")

    existing.shots_against = player_data.get("shotsAgainst")

    existing.save_pctg = player_data.get("savePctg")

    existing.even_strength_saves = even_strength_saves

    existing.even_strength_shots_against = even_strength_shots

    existing.power_play_saves = power_play_saves

    existing.power_play_shots_against = power_play_shots

    existing.shorthanded_saves = shorthanded_saves

    existing.shorthanded_shots_against = shorthanded_shots

    existing.toi_seconds = toi_to_seconds(player_data.get("toi"))


def ingest_team_player_stats(
    db,
    game: Game,
    team_id: int,
    team_stats: dict,
    unknown_player_ids: set,
):
    forwards = team_stats.get(
        "forwards",
        [],
    )

    defense = team_stats.get(
        "defense",
        [],
    )

    goalies = team_stats.get(
        "goalies",
        [],
    )

    for player_data in forwards + defense:
        upsert_skater_stats(
            db=db,
            game=game,
            team_id=team_id,
            player_data=player_data,
            unknown_player_ids=unknown_player_ids,
        )

    for player_data in goalies:
        upsert_goalie_stats(
            db=db,
            game=game,
            team_id=team_id,
            player_data=player_data,
            unknown_player_ids=unknown_player_ids,
        )


def ingest_boxscore(
    db,
    client,
    game: Game,
    unknown_player_ids: set,
):
    """
    Ingest:

        GameResult
        SkaterGameStats
        GoalieGameStats

    from one NHL GameCentre boxscore.
    """

    if game.game_state == "FUT":
        return False

    boxscore = client.game_center.boxscore(str(game.id))

    if not boxscore:
        return False

    upsert_game_result(
        db,
        game,
        boxscore,
    )

    player_stats = boxscore.get(
        "playerByGameStats",
        {},
    )

    away_stats = player_stats.get(
        "awayTeam",
        {},
    )

    home_stats = player_stats.get(
        "homeTeam",
        {},
    )

    ingest_team_player_stats(
        db=db,
        game=game,
        team_id=game.away_team_id,
        team_stats=away_stats,
        unknown_player_ids=unknown_player_ids,
    )

    ingest_team_player_stats(
        db=db,
        game=game,
        team_id=game.home_team_id,
        team_stats=home_stats,
        unknown_player_ids=unknown_player_ids,
    )

    return True


def ingest_boxscores_for_season(
    db,
    client,
    season_id: int,
    unknown_player_ids: set,
    failed_game_ids: set,
):
    games = (
        db.query(Game)
        .filter(Game.season_id == season_id)
        .order_by(
            Game.game_date,
            Game.id,
        )
        .all()
    )

    ingested_count = 0
    future_count = 0
    failed_count = 0

    print(f"Ingesting boxscores for season " f"{season_id} ({len(games)} games)...")

    for game in games:
        if game.game_state == "FUT":
            future_count += 1
            continue

        try:
            # Savepoint for this individual game.
            #
            # If one strange historical game fails, only
            # that game's pending changes are rolled back.
            # The rest of the season remains intact.
            with db.begin_nested():
                ingested = ingest_boxscore(
                    db=db,
                    client=client,
                    game=game,
                    unknown_player_ids=(unknown_player_ids),
                )

                # Force SQL errors to occur inside this
                # game's savepoint rather than waiting
                # until the end-of-season commit.
                db.flush()

            if ingested:
                ingested_count += 1

        except Exception as e:
            failed_game_ids.add(game.id)
            failed_count += 1

            print(f"  Failed game {game.id}: {e}")

            continue

    # One real commit for the entire season.
    db.commit()

    print(
        f"Season {season_id}: "
        f"{ingested_count} ingested, "
        f"{future_count} future, "
        f"{failed_count} failed"
    )


def ingest_all_boxscores():
    client = NHLClient()
    db = SessionLocal()

    unknown_player_ids = set()
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
                ingest_boxscores_for_season(
                    db=db,
                    client=client,
                    season_id=season_id,
                    unknown_player_ids=(unknown_player_ids),
                    failed_game_ids=(failed_game_ids),
                )

            except Exception as e:
                # Something went wrong outside an individual
                # game's savepoint. Roll back this season.
                db.rollback()

                print(f"Failed season " f"{season_id}: {e}")

                continue

    finally:
        db.close()

    print()
    print("=" * 80)
    print("BOXSCORE INGESTION COMPLETE")
    print("=" * 80)

    if unknown_player_ids:
        print()
        print(f"Unknown player IDs " f"({len(unknown_player_ids)}):")

        for player_id in sorted(unknown_player_ids):
            print(f"  {player_id}")

    else:
        print()
        print("No unknown player IDs encountered.")

    if failed_game_ids:
        print()
        print(f"Failed game IDs " f"({len(failed_game_ids)}):")

        for game_id in sorted(failed_game_ids):
            print(f"  {game_id}")

    else:
        print()
        print("No games failed.")


if __name__ == "__main__":
    ingest_all_boxscores()
