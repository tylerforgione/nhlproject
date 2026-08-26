from app.schemas.common import (
    Capability,
    CapabilityState,
    Freshness,
    FreshnessState,
)


UNVERIFIED_SCHEDULE_EXPLANATION = "Schedule coverage has not been verified."
UNVERIFIED_FRESHNESS_EXPLANATION = "Schedule freshness has not been verified."


def unverified_schedule_capability() -> Capability:
    return Capability(
        state=CapabilityState.UNKNOWN,
        explanation=UNVERIFIED_SCHEDULE_EXPLANATION,
    )


def unverified_schedule_freshness() -> Freshness:
    return Freshness(
        state=FreshnessState.UNKNOWN,
        updated_at=None,
        explanation=UNVERIFIED_FRESHNESS_EXPLANATION,
    )
