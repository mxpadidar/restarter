import datetime
from typing import Any


def is_datetime_aware(value: datetime.datetime) -> bool:
    """Return whether a datetime has usable timezone information.

    :param value: Datetime to inspect.
    :return: ``True`` when the datetime is timezone-aware.
    """
    return value.tzinfo is not None and value.utcoffset() is not None


def datetime_to_timestamp(value: datetime.datetime) -> int:
    """Convert a timezone-aware datetime to a whole-second Unix timestamp.

    :param value: Timezone-aware datetime to convert.
    :return: Unix timestamp in whole seconds.
    :raises ValueError: If the datetime is timezone-naive or unsupported.
    """
    if not is_datetime_aware(value):
        raise ValueError("datetime must be timezone-aware")

    try:
        return int(value.timestamp())
    except (OSError, OverflowError, ValueError) as exc:
        raise ValueError("datetime is outside the supported range") from exc


def datetime_from_timestamp(value: Any) -> datetime.datetime:
    """Convert a numeric Unix timestamp to a timezone-aware UTC datetime.

    :param value: Integer or floating-point Unix timestamp.
    :return: Datetime normalized to UTC.
    :raises TypeError: If the value is not numeric.
    :raises ValueError: If the value is outside the supported range.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("timestamp must be numeric")

    try:
        return datetime.datetime.fromtimestamp(value, tz=datetime.UTC)
    except (OSError, OverflowError, ValueError, TypeError) as exc:
        raise ValueError("timestamp is outside the supported range") from exc


def get_current_datetime(tz: datetime.tzinfo = datetime.UTC) -> datetime.datetime:
    """Return the current second-precision datetime in the given timezone.

    :param tz: Timezone to normalize to. Defaults to UTC.
    :return: Current datetime in the given timezone.
    """
    return datetime.datetime.now(tz=tz).replace(microsecond=0)
