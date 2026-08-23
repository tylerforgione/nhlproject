from datetime import date
from enum import Enum

from pydantic import BaseModel

from app.schemas.common import Capability


class SeasonPhase(str, Enum):
    PRESEASON = "preseason"
    REGULAR_SEASON = "regular-season"
    PLAYOFFS = "playoffs"
    OFFSEASON = "offseason"


class CurrentContextResponse(BaseModel):
    official_date: date
    active_season_phase: SeasonPhase
    schedule_season_id: int
    latest_completed_season_id: int | None
    games_capability: Capability
