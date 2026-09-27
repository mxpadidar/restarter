import datetime

from core.utils import is_datetime_aware


def test_is_datetime_aware_identifies_timezone_information():
    """Timezone awareness should require a usable UTC offset."""
    aware = datetime.datetime(2026, 1, 1, tzinfo=datetime.UTC)
    naive = aware.replace(tzinfo=None)

    assert is_datetime_aware(aware)
    assert not is_datetime_aware(naive)
