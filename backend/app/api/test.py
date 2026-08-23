import json
from collections import defaultdict

from nhlpy import NHLClient

GAME_ID = 2025030173

client = NHLClient()

# path -> set of observed Python/JSON types
observed_types = defaultdict(set)


def type_name(value):
    if value is None:
        return "null"

    if isinstance(value, bool):
        return "boolean"

    if isinstance(value, int):
        return "integer"

    if isinstance(value, float):
        return "float"

    if isinstance(value, str):
        return "string"

    if isinstance(value, list):
        return "array"

    if isinstance(value, dict):
        return "object"

    return type(value).__name__


def inspect_json(value, path="root"):
    """
    Recursively inspect every value in the JSON response.

    Array indexes are represented with [] so:

        plays[0].details.shootingPlayerId
        plays[1].details.shootingPlayerId

    both become:

        root.plays[].details.shootingPlayerId
    """

    observed_types[path].add(type_name(value))

    if isinstance(value, dict):
        for key, child_value in value.items():
            child_path = f"{path}.{key}"

            inspect_json(
                child_value,
                child_path,
            )

    elif isinstance(value, list):
        for item in value:
            child_path = f"{path}[]"

            inspect_json(
                item,
                child_path,
            )


def main():
    pbp = client.game_center.play_by_play(GAME_ID)

    inspect_json(pbp)

    print(f"\nPLAY-BY-PLAY SCHEMA FOR GAME {GAME_ID}")

    print("=" * 100)

    for path in sorted(observed_types):
        types = ", ".join(sorted(observed_types[path]))

        print(f"{path:<80} {types}")


if __name__ == "__main__":
    main()
