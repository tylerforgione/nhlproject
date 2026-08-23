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
