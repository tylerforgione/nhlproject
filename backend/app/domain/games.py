from enum import Enum, IntEnum


class GameTypeId(IntEnum):
    PRESEASON = 1
    REGULAR_SEASON = 2
    PLAYOFFS = 3


class GameType(str, Enum):
    PRESEASON = "preseason"
    REGULAR_SEASON = "regular-season"
    PLAYOFFS = "playoffs"
    UNKNOWN = "unknown"


class GameState(str, Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINAL = "final"
    UNKNOWN = "unknown"


def game_type_from_id(game_type_id: int) -> GameType:
    return {
        GameTypeId.PRESEASON: GameType.PRESEASON,
        GameTypeId.REGULAR_SEASON: GameType.REGULAR_SEASON,
        GameTypeId.PLAYOFFS: GameType.PLAYOFFS,
    }.get(game_type_id, GameType.UNKNOWN)


def game_state_from_code(game_state: str | None) -> GameState:
    if game_state in {"OFF", "FINAL"}:
        return GameState.FINAL

    if game_state == "LIVE":
        return GameState.LIVE

    if game_state == "FUT":
        return GameState.SCHEDULED

    return GameState.UNKNOWN
