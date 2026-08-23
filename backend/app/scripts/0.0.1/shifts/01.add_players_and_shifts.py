from datetime import date

import httpx
from nhlpy import NHLClient

from app.db.base import SessionLocal

from app.models.game import Game
from app.models.player import Player

# Import FK-related models so SQLAlchemy metadata knows about them.
from app.models.team import Team
from app.models.season import Season

from app.ingestion.game_results_boxscores import ingest_boxscore
from app.ingestion.shifts import ingest_shifts

# -------------------------------------------------------------------
# KEEP YOUR EXISTING 550-PLAYER SET HERE
# -------------------------------------------------------------------

MISSING_PLAYER_IDS = {
    8476421,
    8477035,
    8477522,
    8478429,
    8478848,
    8478863,
    8478867,
    8478880,
    8478912,
    8478956,
    8478981,
    8479022,
    8479522,
    8479548,
    8479555,
    8479561,
    8479594,
    8479609,
    8479746,
    8479942,
    8480016,
    8480191,
    8480202,
    8480248,
    8480249,
    8480257,
    8480291,
    8480321,
    8480356,
    8480481,
    8480750,
    8480791,
    8480799,
    8480805,
    8480838,
    8480876,
    8480992,
    8480993,
    8480998,
    8480999,
    8481000,
    8481041,
    8481085,
    8481110,
    8481115,
    8481159,
    8481183,
    8481228,
    8481367,
    8481480,
    8481536,
    8481538,
    8481547,
    8481558,
    8481561,
    8481562,
    8481569,
    8481578,
    8481587,
    8481615,
    8481619,
    8481658,
    8481662,
    8481667,
    8481689,
    8481699,
    8481707,
    8481715,
    8481731,
    8481732,
    8481737,
    8481741,
    8481743,
    8481746,
    8481749,
    8481760,
    8481794,
    8481817,
    8481820,
    8481866,
    8482060,
    8482064,
    8482066,
    8482080,
    8482082,
    8482085,
    8482086,
    8482091,
    8482096,
    8482098,
    8482102,
    8482106,
    8482119,
    8482120,
    8482121,
    8482123,
    8482134,
    8482136,
    8482139,
    8482143,
    8482144,
    8482151,
    8482154,
    8482160,
    8482162,
    8482163,
    8482167,
    8482168,
    8482170,
    8482171,
    8482173,
    8482188,
    8482194,
    8482205,
    8482206,
    8482213,
    8482214,
    8482217,
    8482411,
    8482446,
    8482449,
    8482453,
    8482454,
    8482459,
    8482461,
    8482466,
    8482472,
    8482477,
    8482478,
    8482490,
    8482499,
    8482501,
    8482507,
    8482512,
    8482518,
    8482525,
    8482588,
    8482631,
    8482639,
    8482657,
    8482663,
    8482668,
    8482676,
    8482678,
    8482682,
    8482683,
    8482686,
    8482688,
    8482690,
    8482692,
    8482693,
    8482695,
    8482697,
    8482698,
    8482700,
    8482704,
    8482707,
    8482714,
    8482715,
    8482716,
    8482718,
    8482724,
    8482727,
    8482734,
    8482739,
    8482744,
    8482746,
    8482749,
    8482757,
    8482759,
    8482763,
    8482766,
    8482777,
    8482784,
    8482785,
    8482798,
    8482804,
    8482806,
    8482808,
    8482828,
    8482829,
    8482839,
    8482860,
    8482863,
    8482866,
    8482867,
    8482869,
    8482874,
    8482881,
    8482882,
    8482888,
    8482889,
    8482890,
    8482901,
    8482902,
    8482911,
    8482914,
    8482916,
    8482919,
    8482920,
    8482922,
    8482923,
    8482925,
    8482932,
    8482933,
    8482940,
    8482941,
    8482942,
    8482948,
    8482949,
    8482951,
    8482953,
    8482976,
    8482981,
    8482993,
    8483010,
    8483012,
    8483017,
    8483039,
    8483043,
    8483045,
    8483050,
    8483059,
    8483062,
    8483085,
    8483100,
    8483103,
    8483104,
    8483114,
    8483390,
    8483394,
    8483398,
    8483400,
    8483401,
    8483426,
    8483427,
    8483428,
    8483430,
    8483432,
    8483433,
    8483435,
    8483436,
    8483437,
    8483438,
    8483442,
    8483448,
    8483449,
    8483453,
    8483455,
    8483463,
    8483465,
    8483467,
    8483470,
    8483471,
    8483480,
    8483482,
    8483486,
    8483488,
    8483494,
    8483496,
    8483497,
    8483498,
    8483503,
    8483507,
    8483511,
    8483513,
    8483514,
    8483518,
    8483519,
    8483520,
    8483526,
    8483534,
    8483538,
    8483563,
    8483569,
    8483611,
    8483651,
    8483652,
    8483668,
    8483671,
    8483675,
    8483677,
    8483684,
    8483685,
    8483687,
    8483692,
    8483695,
    8483696,
    8483697,
    8483699,
    8483703,
    8483704,
    8483711,
    8483712,
    8483728,
    8483740,
    8483741,
    8483745,
    8483748,
    8483750,
    8483751,
    8483756,
    8483769,
    8483771,
    8483772,
    8483799,
    8483804,
    8483805,
    8483829,
    8483833,
    8483837,
    8483841,
    8483844,
    8483847,
    8483878,
    8483917,
    8483920,
    8483921,
    8483924,
    8483930,
    8484107,
    8484123,
    8484124,
    8484131,
    8484139,
    8484140,
    8484143,
    8484146,
    8484151,
    8484152,
    8484155,
    8484158,
    8484159,
    8484160,
    8484162,
    8484165,
    8484168,
    8484173,
    8484174,
    8484176,
    8484177,
    8484178,
    8484184,
    8484187,
    8484188,
    8484189,
    8484195,
    8484196,
    8484200,
    8484202,
    8484207,
    8484209,
    8484214,
    8484216,
    8484217,
    8484218,
    8484219,
    8484221,
    8484222,
    8484223,
    8484224,
    8484229,
    8484230,
    8484236,
    8484246,
    8484255,
    8484259,
    8484262,
    8484271,
    8484280,
    8484293,
    8484310,
    8484314,
    8484325,
    8484326,
    8484379,
    8484380,
    8484392,
    8484393,
    8484395,
    8484396,
    8484404,
    8484405,
    8484406,
    8484408,
    8484412,
    8484414,
    8484428,
    8484430,
    8484433,
    8484434,
    8484440,
    8484452,
    8484455,
    8484460,
    8484461,
    8484466,
    8484468,
    8484472,
    8484476,
    8484481,
    8484483,
    8484484,
    8484491,
    8484497,
    8484507,
    8484514,
    8484521,
    8484529,
    8484533,
    8484537,
    8484566,
    8484616,
    8484636,
    8484760,
    8484761,
    8484765,
    8484769,
    8484770,
    8484772,
    8484774,
    8484775,
    8484781,
    8484782,
    8484785,
    8484786,
    8484790,
    8484792,
    8484794,
    8484795,
    8484796,
    8484802,
    8484804,
    8484805,
    8484808,
    8484810,
    8484813,
    8484814,
    8484815,
    8484821,
    8484822,
    8484830,
    8484834,
    8484835,
    8484836,
    8484839,
    8484844,
    8484845,
    8484851,
    8484858,
    8484859,
    8484864,
    8484868,
    8484869,
    8484878,
    8484880,
    8484887,
    8484888,
    8484891,
    8484899,
    8484900,
    8484904,
    8484906,
    8484908,
    8484910,
    8484916,
    8484928,
    8484933,
    8484935,
    8484939,
    8484950,
    8484951,
    8484966,
    8484968,
    8484976,
    8484989,
    8484994,
    8484997,
    8485005,
    8485007,
    8485011,
    8485019,
    8485022,
    8485025,
    8485035,
    8485039,
    8485042,
    8485052,
    8485055,
    8485070,
    8485071,
    8485086,
    8485087,
    8485105,
    8485115,
    8485116,
    8485138,
    8485170,
    8485352,
    8485362,
    8485367,
    8485368,
    8485370,
    8485375,
    8485378,
    8485381,
    8485382,
    8485383,
    8485385,
    8485386,
    8485388,
    8485389,
    8485392,
    8485405,
    8485409,
    8485412,
    8485437,
    8485439,
    8485441,
    8485449,
    8485457,
    8485461,
    8485462,
    8485465,
    8485468,
    8485470,
    8485472,
    8485485,
    8485486,
    8485490,
    8485492,
    8485493,
    8485495,
    8485496,
    8485509,
    8485511,
    8485538,
    8485539,
    8485545,
    8485549,
    8485589,
    8485597,
    8485599,
    8485605,
    8485625,
    8485630,
    8485657,
    8485678,
    8485702,
    8485797,
    8478148,
    8481064,
    8481757,
    8481758,
    8482642,
    8482729,
    8483523,
    8483869,
    8483898,
    8484121,
    8484442,
    8485729,
}


PLAYER_URL = "https://api-web.nhle.com/v1/player/{player_id}/landing"


# -------------------------------------------------------------------
# PLAYER HELPERS
# -------------------------------------------------------------------


def fetch_player(player_id: int):
    response = httpx.get(
        PLAYER_URL.format(player_id=player_id),
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def add_missing_players(db):
    """
    Add the preseason-only players to the players table.

    Existing players are left alone, so this is safe to rerun.

    Returns:
        set of player IDs that could not be added
    """

    added = 0
    already_present = 0
    failed_player_ids = set()

    print(f"Checking {len(MISSING_PLAYER_IDS)} " f"preseason-only players...")

    for player_id in sorted(MISSING_PLAYER_IDS):
        existing = db.get(
            Player,
            player_id,
        )

        if existing is not None:
            already_present += 1
            continue

        try:
            data = fetch_player(player_id)

            player = Player(
                id=data["playerId"],
                first_name=(
                    data.get(
                        "firstName",
                        {},
                    ).get("default")
                ),
                last_name=(
                    data.get(
                        "lastName",
                        {},
                    ).get("default")
                ),
                position_code=data.get("position"),
                shoots_catches=data.get("shootsCatches"),
                height_in_inches=data.get("heightInInches"),
                weight_in_pounds=data.get("weightInPounds"),
                height_in_centimeters=data.get("heightInCentimeters"),
                weight_in_kilograms=data.get("weightInKilograms"),
                birth_date=(
                    date.fromisoformat(data["birthDate"])
                    if data.get("birthDate")
                    else None
                ),
                birth_city=(
                    data.get(
                        "birthCity",
                        {},
                    ).get("default")
                ),
                birth_country=data.get("birthCountry"),
                birth_state_province=(
                    data.get(
                        "birthStateProvince",
                        {},
                    ).get("default")
                ),
                headshot_url=data.get("headshot"),
            )

            db.add(player)

            # Flush immediately so FK checks later in this
            # transaction can see the new player.
            db.flush()

            added += 1

        except Exception as e:
            failed_player_ids.add(player_id)

            print(f"Failed player " f"{player_id}: {e}")

    db.commit()

    print()
    print(f"Players added: {added}")

    print(f"Players already present: " f"{already_present}")

    return failed_player_ids


# -------------------------------------------------------------------
# DISCOVER AFFECTED PRESEASON GAMES
# -------------------------------------------------------------------


def find_affected_game_ids(
    db,
    client: NHLClient,
):
    """
    Find preseason games containing at least one of the
    previously-missing players.

    Shift data begins in 20102011, so only scan from then on.

    We only scan preseason games because all IDs in this repair
    set are preseason-only players.

    Returns:
        affected_game_ids
        failed_discovery_game_ids
    """

    affected_game_ids = set()
    failed_game_ids = set()

    games = (
        db.query(Game)
        .filter(
            Game.season_id >= 20102011,
            Game.game_type_id == 1,
        )
        .order_by(
            Game.season_id,
            Game.game_date,
            Game.id,
        )
        .all()
    )

    print()
    print(f"Scanning {len(games)} preseason games " f"for affected players...")

    for game in games:
        if game.game_state == "FUT":
            continue

        try:
            data = client.game_center.shift_chart_data(str(game.id))

            if not data:
                continue

            rows = data.get(
                "data",
                [],
            )

            for row in rows:
                if row.get("typeCode") != 517:
                    continue

                if row.get("playerId") in MISSING_PLAYER_IDS:
                    affected_game_ids.add(game.id)
                    break

        except Exception as e:
            failed_game_ids.add(game.id)

            print(f"Failed discovery for game " f"{game.id}: {e}")

    print()
    print(f"Found {len(affected_game_ids)} " f"affected preseason games.")

    return (
        affected_game_ids,
        failed_game_ids,
    )


# -------------------------------------------------------------------
# REPAIR AFFECTED GAMES
# -------------------------------------------------------------------


def repair_games(
    db,
    client: NHLClient,
    affected_game_ids: set,
):
    """
    Re-run the existing boxscore and shift ingestion helpers
    for only the affected preseason games.

    Existing game stats/shifts are upserted by the normal
    ingestion code, while rows that were previously skipped
    because the Player FK was missing can now be inserted.
    """

    failed_game_ids = set()

    unknown_player_ids = set()
    unknown_team_ids = set()

    repaired_games = 0
    shifts_processed = 0

    game_ids = sorted(affected_game_ids)

    for i, game_id in enumerate(
        game_ids,
        start=1,
    ):
        game = db.get(
            Game,
            game_id,
        )

        if game is None:
            failed_game_ids.add(game_id)

            print(f"Game {game_id} no longer " f"exists in games table.")

            continue

        print(f"[{i}/{len(game_ids)}] " f"Repairing game {game_id}...")

        try:
            with db.begin_nested():

                # Re-ingests:
                #
                #   game_results
                #   skater_game_stats
                #   goalie_game_stats
                #
                # Existing player rows are updated;
                # previously-skipped preseason players
                # are now inserted.
                ingest_boxscore(
                    db=db,
                    client=client,
                    game=game,
                    unknown_player_ids=(unknown_player_ids),
                )

                # Re-ingests shifts for the game.
                #
                # Your current shift ingestion already:
                #
                #   - deduplicates identical NHL intervals
                #   - upserts existing shifts
                #   - inserts previously skipped players
                processed = ingest_shifts(
                    db=db,
                    client=client,
                    game=game,
                    unknown_player_ids=(unknown_player_ids),
                    unknown_team_ids=(unknown_team_ids),
                )

                db.flush()

            repaired_games += 1
            shifts_processed += processed

        except Exception as e:
            failed_game_ids.add(game_id)

            print(f"Failed game " f"{game_id}: {e}")

            continue

    # This is a repair script, so one final commit is enough.
    db.commit()

    return {
        "repaired_games": repaired_games,
        "shifts_processed": shifts_processed,
        "failed_game_ids": failed_game_ids,
        "unknown_player_ids": unknown_player_ids,
        "unknown_team_ids": unknown_team_ids,
    }


# -------------------------------------------------------------------
# MAIN
# -------------------------------------------------------------------


def main():
    client = NHLClient()
    db = SessionLocal()

    failed_player_ids = set()
    discovery_failures = set()

    repair_result = None

    try:
        # -------------------------------------------------
        # 1. ADD THE PRESEASON-ONLY PLAYERS
        # -------------------------------------------------

        failed_player_ids = add_missing_players(db)

        # -------------------------------------------------
        # 2. FIND THE PRESEASON GAMES THEY PLAYED IN
        # -------------------------------------------------

        (
            affected_game_ids,
            discovery_failures,
        ) = find_affected_game_ids(
            db=db,
            client=client,
        )

        # -------------------------------------------------
        # 3. REPAIR BOXSCORE STATS + SHIFTS
        # -------------------------------------------------

        repair_result = repair_games(
            db=db,
            client=client,
            affected_game_ids=(affected_game_ids),
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    print()
    print("=" * 80)
    print("PRESEASON PLAYER BACKFILL COMPLETE")
    print("=" * 80)

    print(f"Requested player IDs: " f"{len(MISSING_PLAYER_IDS)}")

    print(f"Failed player additions: " f"{len(failed_player_ids)}")

    print(f"Discovery failures: " f"{len(discovery_failures)}")

    if repair_result is not None:
        print(f"Games repaired: " f"{repair_result['repaired_games']}")

        print(f"Shift rows processed: " f"{repair_result['shifts_processed']}")

        print(f"Repair game failures: " f"{len(repair_result['failed_game_ids'])}")

        print(f"Still-unknown players: " f"{len(repair_result['unknown_player_ids'])}")

        print(f"Unknown teams: " f"{len(repair_result['unknown_team_ids'])}")

    # -----------------------------------------------------
    # FAILURE DETAILS
    # -----------------------------------------------------

    if failed_player_ids:
        print()
        print("Failed player IDs:")

        for player_id in sorted(failed_player_ids):
            print(f"  {player_id}")

    if discovery_failures:
        print()
        print("Games whose shift data could " "not be checked:")

        for game_id in sorted(discovery_failures):
            print(f"  {game_id}")

    if repair_result and repair_result["failed_game_ids"]:
        print()
        print("Games that failed during repair:")

        for game_id in sorted(repair_result["failed_game_ids"]):
            print(f"  {game_id}")

    if repair_result and repair_result["unknown_player_ids"]:
        print()
        print("Player IDs still missing " "after backfill:")

        for player_id in sorted(repair_result["unknown_player_ids"]):
            print(f"  {player_id}")

    if repair_result and repair_result["unknown_team_ids"]:
        print()
        print("Unknown team IDs:")

        for team_id in sorted(repair_result["unknown_team_ids"]):
            print(f"  {team_id}")


if __name__ == "__main__":
    main()
