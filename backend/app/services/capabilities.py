from app.schemas.common import Capability, CapabilityState


UNVERIFIED_SCHEDULE_EXPLANATION = "Schedule coverage has not been verified."


def unverified_schedule_capability() -> Capability:
    return Capability(
        state=CapabilityState.UNKNOWN,
        explanation=UNVERIFIED_SCHEDULE_EXPLANATION,
    )
