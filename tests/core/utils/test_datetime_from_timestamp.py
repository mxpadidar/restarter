import datetime

import pytest

from core.utils import datetime_from_timestamp


def test_datetime_from_timestamp_returns_utc_datetime():
    """Numeric timestamps should be converted to timezone-aware UTC values."""
    expected_datetime = datetime.datetime(2026, 1, 1, 10, 0, tzinfo=datetime.UTC)
    timestamp = int(expected_datetime.timestamp())

    assert datetime_from_timestamp(timestamp) == expected_datetime


@pytest.mark.parametrize("value", [True, "not-a-timestamp", None])
def test_datetime_from_timestamp_rejects_non_numeric_value(value: object):
    """Booleans and non-numeric values are not valid Unix timestamps."""
    with pytest.raises(TypeError):
        datetime_from_timestamp(value)


def test_datetime_from_timestamp_rejects_unsupported_range():
    """Out-of-range timestamps should produce a stable validation error."""
    unsupported_timestamp = 10**20

    with pytest.raises(ValueError):
        datetime_from_timestamp(unsupported_timestamp)
