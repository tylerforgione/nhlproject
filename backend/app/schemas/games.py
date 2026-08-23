from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel

from app.schemas.common import Capability


class GameType(str, Enum):
    PRESEASON = "preseason"
    REGULAR_SEASON = "regular-season"
    PLAYOFFS = "playoffs"


class GameState(str, Enum):
    SCHEDULED = "scheduled"
    LIVE = "live"
    FINAL = "final"
    UNKNOWN = "unknown"


class TeamReference(BaseModel):
    id: int
    name: str
    abbreviation: str
    logo_url: str | None
    dark_logo_url: str | None


class GameSummary(BaseModel):
    id: int
    season_id: int
    game_type: GameType
    state: GameState
    official_date: date
    start_time_utc: datetime | None
    away_team: TeamReference
    home_team: TeamReference
    away_score: int | None
    home_score: int | None
    venue: str | None
    venue_timezone: str | None
    neutral_site: bool


class GamesByDateResponse(BaseModel):
    official_date: date
    capability: Capability
    games: list[GameSummary]
