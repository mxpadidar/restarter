import datetime

import pytest

from core.utils import datetime_to_timestamp


def test_datetime_to_timestamp_normalizes_timezone_and_precision():
    """Datetime conversion should produce a whole-second Unix timestamp."""
    timezone = datetime.timezone(datetime.timedelta(hours=2))
    value = datetime.datetime(2026, 1, 1, 12, 0, 0, 123456, tzinfo=timezone)
    expected_datetime = datetime.datetime(2026, 1, 1, 10, 0, tzinfo=datetime.UTC)
    expected_timestamp = int(expected_datetime.timestamp())

    assert datetime_to_timestamp(value) == expected_timestamp


def test_datetime_to_timestamp_rejects_naive_datetime():
    """Naive datetimes should not be interpreted using the host timezone."""
    value = datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC).replace(tzinfo=None)

    with pytest.raises(ValueError):
        datetime_to_timestamp(value)
