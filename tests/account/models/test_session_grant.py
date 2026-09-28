"""Tests for the SessionGrant model."""

import uuid
from datetime import timedelta

import pytest
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.utils import timezone

from account.models import SessionGrant, User

pytestmark = pytest.mark.django_db


def test_session_grant_rejects_expiry_before_issue():
    """A grant must expire after it is issued."""
    user = User.objects.create_user(username="user@example.com", password="password")
    grant = SessionGrant(
        user=user,
        session_id=uuid.uuid7(),
        secret_hash="a" * 64,
        expires_at=timezone.now() - timedelta(seconds=1),
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        grant.save()


def test_session_grant_rejects_revocation_before_issue():
    """A grant cannot be revoked before it is issued."""
    user = User.objects.create_user(username="user@example.com", password="password")
    grant = SessionGrant(
        user=user,
        session_id=uuid.uuid7(),
        secret_hash="a" * 64,
        expires_at=timezone.now() + timedelta(days=1),
        revoked_at=timezone.now() - timedelta(days=1),
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        grant.save()


def test_session_grant_allows_only_one_unrevoked_grant_per_session():
    """A logical session may have only one active refresh grant."""
    user = User.objects.create_user(username="user@example.com", password="password")
    session_id = uuid.uuid7()
    SessionGrant.objects.create(
        user=user,
        session_id=session_id,
        secret_hash="a" * 64,
        expires_at=timezone.now() + timedelta(days=1),
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        SessionGrant.objects.create(
            user=user,
            session_id=session_id,
            secret_hash="b" * 64,
            expires_at=timezone.now() + timedelta(days=1),
        )


def test_session_grant_revoke_deactivates_grant():
    """Revoking an active grant should persist its lifecycle state."""
    user = User.objects.create_user(username="user@example.com", password="password")
    grant = SessionGrant.objects.create(
        user=user,
        session_id=uuid.uuid7(),
        secret_hash="a" * 64,
        expires_at=timezone.now() + timedelta(days=1),
    )

    grant.revoke()

    grant.refresh_from_db()
    assert grant.revoked_at is not None
    assert not grant.is_active


def test_session_grant_rejects_revoking_an_inactive_grant():
    """An already revoked grant cannot be revoked again."""
    user = User.objects.create_user(username="user@example.com", password="password")
    grant = SessionGrant.objects.create(
        user=user,
        session_id=uuid.uuid7(),
        secret_hash="a" * 64,
        expires_at=timezone.now() + timedelta(days=1),
    )
    grant.revoke()

    with pytest.raises(ValueError):
        grant.revoke()


def test_session_grant_protects_user_from_deletion():
    """Users with grants should not be deletable."""
    user = User.objects.create_user(username="user@example.com", password="password")
    SessionGrant.objects.create(
        user=user,
        session_id=uuid.uuid7(),
        secret_hash="a" * 64,
        expires_at=timezone.now() + timedelta(days=1),
    )

    with pytest.raises(ProtectedError):
        user.delete()
