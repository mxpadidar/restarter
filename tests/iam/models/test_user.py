import pytest
from django.utils import timezone

from iam.models import User

pytestmark = pytest.mark.django_db


def test_user_is_active_when_neither_deleted_nor_deactivated():
    user = User.objects.create_user(username="user", password="test-password")

    assert user.is_active


def test_user_is_inactive_when_deleted():
    user = User.objects.create_user(username="user", password="test-password")
    user.deleted_at = timezone.now()
    user.save(update_fields=("deleted_at",))

    assert not user.is_active


def test_user_is_inactive_when_deactivated():
    user = User.objects.create_user(username="user", password="test-password")
    user.deactivated_at = timezone.now()
    user.save(update_fields=("deactivated_at",))

    assert not user.is_active
