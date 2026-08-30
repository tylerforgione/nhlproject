from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo


NHL_OFFICIAL_TIME_ZONE = ZoneInfo("America/New_York")


def official_date_at(instant: datetime) -> date:
    if instant.tzinfo is None:
        raise ValueError("instant must include timezone information")

    return instant.astimezone(NHL_OFFICIAL_TIME_ZONE).date()


def current_official_date() -> date:
    return official_date_at(datetime.now(timezone.utc))
