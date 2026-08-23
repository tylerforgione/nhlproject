from collections import defaultdict
from pprint import pprint

from nhlpy import NHLClient

PROBLEM_CASES = [
    {
        "game_id": 2014020327,
        "player_id": 8471418,
        "period": 3,
        "start_time": "04:23",  # 263 seconds
    },
    {
        "game_id": 2014020414,
        "player_id": 8468498,
        "period": 1,
        "start_time": "00:00",
    },
]


def time_to_seconds(value: str | None):
    if not value:
        return None

    minutes, seconds = value.split(":")
    return int(minutes) * 60 + int(seconds)


def main():
    client = NHLClient()

    for case in PROBLEM_CASES:
        game_id = case["game_id"]
        player_id = case["player_id"]
        period = case["period"]
        start_time = case["start_time"]
        start_seconds = time_to_seconds(start_time)

        print()
        print("=" * 100)
        print(
            f"GAME {game_id} | "
            f"PLAYER {player_id} | "
            f"PERIOD {period} | "
            f"START {start_time}"
        )
        print("=" * 100)

        data = client.game_center.shift_chart_data(str(game_id))

        rows = data.get("data", [])

        matches = []

        for row in rows:
            if row.get("typeCode") != 517:
                continue

            if row.get("playerId") != player_id:
                continue

            if row.get("period") != period:
                continue

            if time_to_seconds(row.get("startTime")) != start_seconds:
                continue

            matches.append(row)

        print(f"Found {len(matches)} matching shift rows.\n")

        for i, row in enumerate(matches, start=1):
            print(f"SHIFT {i}")
            pprint(row, sort_dicts=False)
            print()

        if len(matches) < 2:
            print("No duplicate pair found.")
            continue

        print("-" * 100)
        print("FIELD-BY-FIELD COMPARISON")
        print("-" * 100)

        all_keys = sorted(set().union(*(row.keys() for row in matches)))

        for key in all_keys:
            values = [row.get(key) for row in matches]

            same = all(value == values[0] for value in values)

            marker = "SAME" if same else "DIFFERENT"

            print(f"{marker:10} " f"{key:25} " f"{values}")

        # Compare while intentionally ignoring NHL row ID.
        without_id = []

        for row in matches:
            normalized = {key: value for key, value in row.items() if key != "id"}

            without_id.append(normalized)

        identical_except_id = all(row == without_id[0] for row in without_id)

        print()
        print("IDENTICAL EXCEPT FOR ID: " f"{identical_except_id}")


if __name__ == "__main__":
    main()
