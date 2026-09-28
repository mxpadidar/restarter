from uuid import uuid4

import pytest
from django.utils import timezone

from account.commands import LogoutCommand
from account.handlers import handle_logout_command
from account.models import SessionGrant, User
from conf.config import Config
from conf.container import Container
from core.errors import AuthenticationError

pytestmark = pytest.mark.django_db


@pytest.fixture
def active_grant(container: Container, config: Config) -> tuple[SessionGrant, str]:
    user = User.objects.create_user(username="user", password="test-password")
    refresh_secret = "refresh-secret"
    grant = SessionGrant.objects.create(
        user=user,
        session_id=uuid4(),
        secret_hash=container.hmac_hasher.hash(refresh_secret),
        expires_at=timezone.now() + config.refresh_token_ttl,
    )
    return grant, refresh_secret


def test_handle_logout_command_revokes_the_active_grant(
    active_grant: tuple[SessionGrant, str], container: Container
):
    grant, refresh_secret = active_grant

    handle_logout_command(
        cmd=LogoutCommand(refresh_token=f"{grant.id.hex}:{refresh_secret}"),
        hasher=container.hmac_hasher,
    )

    grant.refresh_from_db()

    assert grant.revoked_at is not None


def test_handle_logout_command_rejects_a_malformed_token(container: Container):
    with pytest.raises(AuthenticationError):
        handle_logout_command(
            cmd=LogoutCommand(refresh_token="malformed"),
            hasher=container.hmac_hasher,
        )


def test_handle_logout_command_rejects_an_incorrect_refresh_secret(
    active_grant: tuple[SessionGrant, str], container: Container
):
    grant, _ = active_grant

    with pytest.raises(AuthenticationError):
        handle_logout_command(
            cmd=LogoutCommand(refresh_token=f"{grant.id.hex}:incorrect-secret"),
            hasher=container.hmac_hasher,
        )

    grant.refresh_from_db()

    assert grant.revoked_at is None


def test_handle_logout_command_rejects_an_already_revoked_grant(
    active_grant: tuple[SessionGrant, str], container: Container
):
    grant, refresh_secret = active_grant
    grant.revoke()

    with pytest.raises(AuthenticationError):
        handle_logout_command(
            cmd=LogoutCommand(refresh_token=f"{grant.id.hex}:{refresh_secret}"),
            hasher=container.hmac_hasher,
        )
