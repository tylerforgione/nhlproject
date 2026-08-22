from nhlpy import NHLClient

import re
import unicodedata

from app.db.base import SessionLocal

from app.models.player import Player
from app.models.roster import Roster
from app.models.team import Team
from app.models.season import Season
from app.models.skater_stats import SkaterStats
from app.models.goalie_stats import GoalieStats

# ---------------------------------------------------------
# CACHE
# ---------------------------------------------------------

# Cache team roster responses by:
#
#     (team_abbrev, season_id)
#
# Example:
#
#     ("MTL", 20252026)
#
# becomes:
#
#     {
#         player_id: sweater_number,
#         ...
#     }
#
# This prevents us from making the same team-roster API call
# again for every single player.
ROSTER_CACHE = {}


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------


def toi_to_seconds(toi: str | None):
    if not toi:
        return None

    minutes, seconds = toi.split(":")
    return int(minutes) * 60 + int(seconds)


def normalize_team_name(name: str):
    """
    Normalize API/database team names for comparison.

    Examples:

        Montréal Canadiens -> montreal canadiens
        Ottawa Senators (1917) -> ottawa senators
    """

    if not name:
        return ""

    name = unicodedata.normalize("NFKD", name)

    name = "".join(c for c in name if not unicodedata.combining(c))

    # Remove parenthetical suffixes such as "(1917)"
    name = re.sub(
        r"\s*\([^)]*\)\s*",
        " ",
        name,
    )

    return " ".join(name.lower().split())


def find_team(
    db,
    api_team_name: str,
    season_id: int,
):
    """
    Match the team name returned by the NHL player endpoint
    to a Team in our database.
    """

    normalized_api_name = normalize_team_name(api_team_name)

    teams = db.query(Team).all()

    candidates = []

    for team in teams:
        if normalize_team_name(team.name) != normalized_api_name:
            continue

        first_season = int(team.first_season) if team.first_season else None

        last_season = int(team.last_season) if team.last_season else None

        if first_season is not None and season_id < first_season:
            continue

        if last_season is not None and season_id > last_season:
            continue

        candidates.append(team)

    if len(candidates) == 1:
        return candidates[0]

    if len(candidates) > 1:
        print(
            f"WARNING: Multiple team matches for "
            f"{api_team_name} in {season_id}: "
            f"{[team.name for team in candidates]}"
        )

        return None

    print(f"WARNING: Could not match team " f"'{api_team_name}' for season {season_id}")

    return None


def get_sweater_number(
    client,
    team: Team,
    season_id: int,
    player_id: int,
):
    """
    Fetch a player's sweater number from the NHL team roster
    endpoint.

    The roster response is cached per team-season so we only
    make one API call for each combination.
    """

    cache_key = (
        team.abbrev,
        season_id,
    )

    if cache_key not in ROSTER_CACHE:
        try:
            roster_data = client.teams.team_roster(
                team_abbr=team.abbrev,
                season=str(season_id),
            )

            all_players = (
                roster_data.get("forwards", [])
                + roster_data.get("defensemen", [])
                + roster_data.get("goalies", [])
            )

            ROSTER_CACHE[cache_key] = {
                p["id"]: p.get("sweaterNumber")
                for p in all_players
                if p.get("id") is not None
            }

        except Exception as e:
            print(
                f"WARNING: Could not get roster for " f"{team.abbrev} {season_id}: {e}"
            )

            # Cache the failure too so we don't repeatedly
            # hammer an endpoint that doesn't work.
            ROSTER_CACHE[cache_key] = {}

    return ROSTER_CACHE[cache_key].get(player_id)


def add_nullable(
    existing_value,
    new_value,
):
    """
    Add two nullable counting stats.

    If both values are None, preserve None rather than turning
    an unavailable historical statistic into 0.
    """

    if existing_value is None and new_value is None:
        return None

    return (existing_value or 0) + (new_value or 0)


# ---------------------------------------------------------
# STINT MERGING
# ---------------------------------------------------------


def merge_skater_stint(
    stats: SkaterStats,
    row: dict,
):
    """
    Merge a second stint with the same team during the same
    season into the already-pending SkaterStats row.

    Example:

        MTL -> BOS -> MTL

    Both Montreal stints become one Montreal season-stat row.
    """

    stats.games_played = add_nullable(
        stats.games_played,
        row.get("gamesPlayed"),
    )

    stats.goals = add_nullable(
        stats.goals,
        row.get("goals"),
    )

    stats.assists = add_nullable(
        stats.assists,
        row.get("assists"),
    )

    stats.points = add_nullable(
        stats.points,
        row.get("points"),
    )

    stats.plus_minus = add_nullable(
        stats.plus_minus,
        row.get("plusMinus"),
    )

    stats.pim = add_nullable(
        stats.pim,
        row.get("pim"),
    )

    stats.shots = add_nullable(
        stats.shots,
        row.get("shots"),
    )

    stats.power_play_goals = add_nullable(
        stats.power_play_goals,
        row.get("powerPlayGoals"),
    )

    stats.power_play_points = add_nullable(
        stats.power_play_points,
        row.get("powerPlayPoints"),
    )

    stats.shorthanded_goals = add_nullable(
        stats.shorthanded_goals,
        row.get("shorthandedGoals"),
    )

    stats.shorthanded_points = add_nullable(
        stats.shorthanded_points,
        row.get("shorthandedPoints"),
    )

    stats.game_winning_goals = add_nullable(
        stats.game_winning_goals,
        row.get("gameWinningGoals"),
    )

    stats.ot_goals = add_nullable(
        stats.ot_goals,
        row.get("otGoals"),
    )

    # Recalculate shooting percentage from combined totals.
    if stats.shots:
        stats.shooting_pctg = stats.goals / stats.shots
    else:
        stats.shooting_pctg = None

    # These cannot be perfectly recombined from the API
    # fields alone, so for the rare multiple-stint case
    # leave the first stint's values:
    #
    #     avg_toi_seconds
    #     faceoff_winning_pctg


def merge_goalie_stint(
    stats: GoalieStats,
    row: dict,
):
    """
    Same idea as merge_skater_stint(), but for goalies.
    """

    stats.games_played = add_nullable(
        stats.games_played,
        row.get("gamesPlayed"),
    )

    stats.games_started = add_nullable(
        stats.games_started,
        row.get("gamesStarted"),
    )

    stats.wins = add_nullable(
        stats.wins,
        row.get("wins"),
    )

    stats.losses = add_nullable(
        stats.losses,
        row.get("losses"),
    )

    stats.ties = add_nullable(
        stats.ties,
        row.get("ties"),
    )

    stats.ot_losses = add_nullable(
        stats.ot_losses,
        row.get("otLosses"),
    )

    stats.shots_against = add_nullable(
        stats.shots_against,
        row.get("shotsAgainst"),
    )

    stats.goals_against = add_nullable(
        stats.goals_against,
        row.get("goalsAgainst"),
    )

    stats.shutouts = add_nullable(
        stats.shutouts,
        row.get("shutouts"),
    )

    stats.goals = add_nullable(
        stats.goals,
        row.get("goals"),
    )

    stats.assists = add_nullable(
        stats.assists,
        row.get("assists"),
    )

    stats.pim = add_nullable(
        stats.pim,
        row.get("pim"),
    )

    new_toi = toi_to_seconds(row.get("timeOnIce"))

    stats.time_on_ice_seconds = add_nullable(
        stats.time_on_ice_seconds,
        new_toi,
    )

    # Recalculate save percentage from combined totals.
    if stats.shots_against:
        saves = stats.shots_against - (stats.goals_against or 0)

        stats.save_pctg = saves / stats.shots_against

    else:
        stats.save_pctg = None

    # GAA = goals against per 60 minutes.
    if stats.time_on_ice_seconds:
        stats.goals_against_avg = (
            (stats.goals_against or 0) * 3600 / stats.time_on_ice_seconds
        )

    else:
        stats.goals_against_avg = None


# ---------------------------------------------------------
# PLAYER INGESTION
# ---------------------------------------------------------


def ingest_player_stats(
    player_id: int,
):
    client = NHLClient()
    db = SessionLocal()

    try:
        player = db.get(
            Player,
            player_id,
        )

        if player is None:
            print(f"Player {player_id} does not exist " f"in players table")

            return

        data = client.stats.player_career_stats(player_id)

        season_totals = data.get(
            "seasonTotals",
            [],
        )

        # These dictionaries solve the same-team-twice
        # problem within one player's API response.
        pending_skater_stats = {}
        pending_goalie_stats = {}

        seen_roster_keys = set()

        for row in season_totals:

            # NHL only
            if row.get("leagueAbbrev") != "NHL":
                continue

            season_id = row.get("season")
            game_type_id = row.get("gameTypeId")

            if season_id is None or game_type_id is None:
                continue

            # 2 = regular season
            # 3 = playoffs
            if game_type_id not in (2, 3):
                continue

            # -------------------------------------------------
            # SEASON
            # -------------------------------------------------

            season = db.get(
                Season,
                season_id,
            )

            if season is None:
                print(
                    f"WARNING: Season {season_id} " f"not found for player {player_id}"
                )

                continue

            # -------------------------------------------------
            # TEAM
            # -------------------------------------------------

            api_team_name = row.get(
                "teamName",
                {},
            ).get("default")

            if not api_team_name:
                print(
                    f"WARNING: No team name for "
                    f"player {player_id}, "
                    f"season {season_id}"
                )

                continue

            team = find_team(
                db,
                api_team_name,
                season_id,
            )

            if team is None:
                continue

            # -------------------------------------------------
            # ROSTER
            # -------------------------------------------------

            roster_key = (
                player.id,
                team.id,
                season_id,
            )

            if roster_key not in seen_roster_keys:
                existing_roster = (
                    db.query(Roster)
                    .filter(
                        Roster.player_id == player.id,
                        Roster.team_id == team.id,
                        Roster.season_id == season_id,
                    )
                    .first()
                )

                sweater_number = get_sweater_number(
                    client=client,
                    team=team,
                    season_id=season_id,
                    player_id=player.id,
                )

                if existing_roster is None:
                    roster = Roster(
                        player_id=player.id,
                        team_id=team.id,
                        season_id=season_id,
                        sweater_number=(sweater_number),
                        position_code=(player.position_code),
                    )

                    db.add(roster)

                elif (
                    existing_roster.sweater_number is None
                    and sweater_number is not None
                ):
                    existing_roster.sweater_number = sweater_number

                seen_roster_keys.add(roster_key)

            # -------------------------------------------------
            # STAT KEY
            # -------------------------------------------------

            stat_key = (
                player.id,
                team.id,
                season_id,
                game_type_id,
            )

            # -------------------------------------------------
            # GOALIE
            # -------------------------------------------------

            if player.position_code == "G":

                # Duplicate within this player's API response.
                if stat_key in pending_goalie_stats:
                    merge_goalie_stint(
                        pending_goalie_stats[stat_key],
                        row,
                    )

                    continue

                # Existing row from an earlier completed run.
                existing = (
                    db.query(GoalieStats)
                    .filter(
                        GoalieStats.player_id == player.id,
                        GoalieStats.team_id == team.id,
                        GoalieStats.season_id == season_id,
                        GoalieStats.game_type_id == game_type_id,
                    )
                    .first()
                )

                if existing is not None:
                    pending_goalie_stats[stat_key] = existing

                    continue

                goalie_stats = GoalieStats(
                    player_id=player.id,
                    team_id=team.id,
                    season_id=season_id,
                    game_type_id=game_type_id,
                    games_played=row.get("gamesPlayed"),
                    games_started=row.get("gamesStarted"),
                    wins=row.get("wins"),
                    losses=row.get("losses"),
                    ties=row.get("ties"),
                    ot_losses=row.get("otLosses"),
                    shots_against=row.get("shotsAgainst"),
                    goals_against=row.get("goalsAgainst"),
                    goals_against_avg=row.get("goalsAgainstAvg"),
                    save_pctg=row.get("savePctg"),
                    shutouts=row.get("shutouts"),
                    time_on_ice_seconds=(toi_to_seconds(row.get("timeOnIce"))),
                    goals=row.get("goals"),
                    assists=row.get("assists"),
                    pim=row.get("pim"),
                )

                db.add(goalie_stats)

                pending_goalie_stats[stat_key] = goalie_stats

            # -------------------------------------------------
            # SKATER
            # -------------------------------------------------

            else:

                # Duplicate within this player's API response.
                #
                # Example:
                #
                #     MTL -> BOS -> MTL
                #
                if stat_key in pending_skater_stats:
                    merge_skater_stint(
                        pending_skater_stats[stat_key],
                        row,
                    )

                    continue

                # Existing row from an earlier completed run.
                existing = (
                    db.query(SkaterStats)
                    .filter(
                        SkaterStats.player_id == player.id,
                        SkaterStats.team_id == team.id,
                        SkaterStats.season_id == season_id,
                        SkaterStats.game_type_id == game_type_id,
                    )
                    .first()
                )

                if existing is not None:
                    pending_skater_stats[stat_key] = existing

                    continue

                skater_stats = SkaterStats(
                    player_id=player.id,
                    team_id=team.id,
                    season_id=season_id,
                    game_type_id=game_type_id,
                    games_played=row.get("gamesPlayed"),
                    goals=row.get("goals"),
                    assists=row.get("assists"),
                    points=row.get("points"),
                    plus_minus=row.get("plusMinus"),
                    pim=row.get("pim"),
                    shots=row.get("shots"),
                    shooting_pctg=row.get("shootingPctg"),
                    avg_toi_seconds=(toi_to_seconds(row.get("avgToi"))),
                    faceoff_winning_pctg=(row.get("faceoffWinningPctg")),
                    power_play_goals=row.get("powerPlayGoals"),
                    power_play_points=row.get("powerPlayPoints"),
                    shorthanded_goals=row.get("shorthandedGoals"),
                    shorthanded_points=row.get("shorthandedPoints"),
                    game_winning_goals=row.get("gameWinningGoals"),
                    ot_goals=row.get("otGoals"),
                )

                db.add(skater_stats)

                pending_skater_stats[stat_key] = skater_stats

        db.commit()

        print(
            f"Ingested stats for "
            f"{player.first_name} "
            f"{player.last_name} "
            f"({player.id})"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------


if __name__ == "__main__":
    db = SessionLocal()

    player_ids = [row[0] for row in (db.query(Player.id).order_by(Player.id).all())]

    db.close()

    print(f"Found {len(player_ids)} players")

    for i, player_id in enumerate(
        player_ids,
        start=1,
    ):
        print(
            f"[{i}/{len(player_ids)}] " f"Ingesting stats for player " f"{player_id}..."
        )

        try:
            ingest_player_stats(player_id)

        except Exception as e:
            print(f"Failed for player " f"{player_id}: {e}")

            continue
