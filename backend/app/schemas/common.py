from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class CapabilityState(str, Enum):
    AVAILABLE = "available"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


class Capability(BaseModel):
    state: CapabilityState
    explanation: str | None


class FreshnessState(str, Enum):
    FRESH = "fresh"
    STALE = "stale"
    UNKNOWN = "unknown"


class Freshness(BaseModel):
    state: FreshnessState
    updated_at: datetime | None
    explanation: str | None
