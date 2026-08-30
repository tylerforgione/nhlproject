from datetime import datetime, timezone

import pytest

from app.domain.official_date import official_date_at


def test_official_date_stays_on_the_previous_nhl_day_after_utc_midnight():
    instant = datetime(2026, 1, 16, 0, 30, tzinfo=timezone.utc)

    assert official_date_at(instant).isoformat() == "2026-01-15"


def test_official_date_accounts_for_eastern_daylight_time():
    before_eastern_midnight = datetime(2026, 6, 16, 3, 30, tzinfo=timezone.utc)
    after_eastern_midnight = datetime(2026, 6, 16, 4, 30, tzinfo=timezone.utc)

    assert official_date_at(before_eastern_midnight).isoformat() == "2026-06-15"
    assert official_date_at(after_eastern_midnight).isoformat() == "2026-06-16"


def test_official_date_rejects_an_instant_without_a_timezone():
    with pytest.raises(ValueError, match="timezone information"):
        official_date_at(datetime(2026, 1, 16, 0, 30))
