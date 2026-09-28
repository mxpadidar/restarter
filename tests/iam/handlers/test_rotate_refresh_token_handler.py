from datetime import timedelta
from uuid import uuid4

import pytest
from django.utils import timezone

from conf.config import Config
from conf.container import Container
from core.errors import AuthenticationError
from core.rbac import Role
from core.utils import datetime_to_timestamp
from iam.commands import RotateRefreshTokenCommand
from iam.dtos import TokenPair
from iam.handlers import handle_rotate_refresh_token_command
from iam.models import SessionGrant, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def active_grant(container: Container, config: Config) -> tuple[SessionGrant, str]:
    user = User.objects.create_user(username="user", password="test-password")
    container.role_manager.assign(user, Role.NORMAL)
    refresh_secret = "refresh-secret"
    grant = SessionGrant.objects.create(
        user=user,
        session_id=uuid4(),
        secret_hash=container.hmac_hasher.hash(refresh_secret),
        expires_at=timezone.now() + config.refresh_token_ttl,
    )
    return grant, refresh_secret


def test_rotate_refresh_token_revokes_the_old_grant_and_issues_a_new_pair(
    active_grant: tuple[SessionGrant, str],
    container: Container,
    config: Config,
):
    grant, refresh_secret = active_grant

    token_pair = handle_rotate_refresh_token_command(
        cmd=RotateRefreshTokenCommand(
            refresh_token=f"{grant.id.hex}:{refresh_secret}",
            access_token_ttl=config.access_token_ttl,
            refresh_token_ttl=config.refresh_token_ttl,
            refresh_token_size=config.refresh_token_size,
            ip_address="192.0.2.1",
        ),
        hasher=container.hmac_hasher,
        jwt_service=container.jwt_service,
        role_manager=container.role_manager,
    )

    grant.refresh_from_db()
    new_grant_id, new_refresh_secret = TokenPair.parse_refresh_token(token_pair.refresh_token)
    new_grant = SessionGrant.objects.get(id=new_grant_id)
    payload = container.jwt_service.decode(token_pair.access_token)

    assert grant.revoked_at is not None
    assert new_grant.id != grant.id
    assert new_grant.session_id == grant.session_id
    assert new_grant.ip_address == "192.0.2.1"
    assert container.hmac_hasher.verify(
        plain_text=new_refresh_secret,
        expected_hash=new_grant.secret_hash,
    )
    assert payload["sub"] == grant.user.id.hex
    assert payload["jti"] == new_grant.id.hex
    assert payload["roles"] == [Role.NORMAL.value]
    assert payload["exp"] == datetime_to_timestamp(token_pair.expires_at)


def test_rotate_refresh_token_rejects_reusing_a_rotated_token(
    active_grant: tuple[SessionGrant, str], container: Container, config: Config
):
    grant, refresh_secret = active_grant
    command = RotateRefreshTokenCommand(
        refresh_token=f"{grant.id.hex}:{refresh_secret}",
        access_token_ttl=config.access_token_ttl,
        refresh_token_ttl=config.refresh_token_ttl,
        refresh_token_size=config.refresh_token_size,
    )

    handle_rotate_refresh_token_command(
        cmd=command,
        hasher=container.hmac_hasher,
        jwt_service=container.jwt_service,
        role_manager=container.role_manager,
    )

    with pytest.raises(AuthenticationError) as exc_info:
        handle_rotate_refresh_token_command(
            cmd=command,
            hasher=container.hmac_hasher,
            jwt_service=container.jwt_service,
            role_manager=container.role_manager,
        )

    assert exc_info.value.details == {}
    assert (
        SessionGrant.objects.filter(session_id=grant.session_id, revoked_at__isnull=True).count()
        == 1
    )


def test_rotate_refresh_token_uses_current_user_roles(
    active_grant: tuple[SessionGrant, str], container: Container, config: Config
):
    grant, refresh_secret = active_grant
    container.role_manager.assign(grant.user, Role.ADMIN)

    token_pair = handle_rotate_refresh_token_command(
        cmd=RotateRefreshTokenCommand(
            refresh_token=f"{grant.id.hex}:{refresh_secret}",
            access_token_ttl=config.access_token_ttl,
            refresh_token_ttl=config.refresh_token_ttl,
            refresh_token_size=config.refresh_token_size,
        ),
        hasher=container.hmac_hasher,
        jwt_service=container.jwt_service,
        role_manager=container.role_manager,
    )

    payload = container.jwt_service.decode(token_pair.access_token)

    assert payload["roles"] == [Role.ADMIN.value, Role.NORMAL.value]


def test_rotate_refresh_token_rejects_a_malformed_token(container: Container, config: Config):
    with pytest.raises(AuthenticationError):
        handle_rotate_refresh_token_command(
            cmd=RotateRefreshTokenCommand(
                refresh_token="malformed",
                access_token_ttl=config.access_token_ttl,
                refresh_token_ttl=config.refresh_token_ttl,
                refresh_token_size=config.refresh_token_size,
            ),
            hasher=container.hmac_hasher,
            jwt_service=container.jwt_service,
            role_manager=container.role_manager,
        )


def test_rotate_refresh_token_rejects_an_unknown_grant(container: Container, config: Config):
    with pytest.raises(AuthenticationError):
        handle_rotate_refresh_token_command(
            cmd=RotateRefreshTokenCommand(
                refresh_token=f"{uuid4().hex}:refresh-secret",
                access_token_ttl=config.access_token_ttl,
                refresh_token_ttl=config.refresh_token_ttl,
                refresh_token_size=config.refresh_token_size,
            ),
            hasher=container.hmac_hasher,
            jwt_service=container.jwt_service,
            role_manager=container.role_manager,
        )


def test_rotate_refresh_token_rejects_an_incorrect_refresh_secret(
    active_grant: tuple[SessionGrant, str], container: Container, config: Config
):
    grant, _ = active_grant

    with pytest.raises(AuthenticationError):
        handle_rotate_refresh_token_command(
            cmd=RotateRefreshTokenCommand(
                refresh_token=f"{grant.id.hex}:incorrect-secret",
                access_token_ttl=config.access_token_ttl,
                refresh_token_ttl=config.refresh_token_ttl,
                refresh_token_size=config.refresh_token_size,
            ),
            hasher=container.hmac_hasher,
            jwt_service=container.jwt_service,
            role_manager=container.role_manager,
        )

    grant.refresh_from_db()
    assert grant.revoked_at is None


def test_rotate_refresh_token_rejects_a_deleted_user(
    active_grant: tuple[SessionGrant, str], container: Container, config: Config
):
    grant, refresh_secret = active_grant
    grant.user.deleted_at = timezone.now()
    grant.user.save(update_fields=("deleted_at",))

    with pytest.raises(AuthenticationError):
        handle_rotate_refresh_token_command(
            cmd=RotateRefreshTokenCommand(
                refresh_token=f"{grant.id.hex}:{refresh_secret}",
                access_token_ttl=config.access_token_ttl,
                refresh_token_ttl=config.refresh_token_ttl,
                refresh_token_size=config.refresh_token_size,
            ),
            hasher=container.hmac_hasher,
            jwt_service=container.jwt_service,
            role_manager=container.role_manager,
        )

    grant.refresh_from_db()
    assert grant.revoked_at is None


def test_rotate_refresh_token_rejects_a_deactivated_user(
    active_grant: tuple[SessionGrant, str], container: Container, config: Config
):
    grant, refresh_secret = active_grant
    grant.user.deactivated_at = timezone.now()
    grant.user.save(update_fields=("deactivated_at",))

    with pytest.raises(AuthenticationError):
        handle_rotate_refresh_token_command(
            cmd=RotateRefreshTokenCommand(
                refresh_token=f"{grant.id.hex}:{refresh_secret}",
                access_token_ttl=config.access_token_ttl,
                refresh_token_ttl=config.refresh_token_ttl,
                refresh_token_size=config.refresh_token_size,
            ),
            hasher=container.hmac_hasher,
            jwt_service=container.jwt_service,
            role_manager=container.role_manager,
        )

    grant.refresh_from_db()
    assert grant.revoked_at is None


def test_rotate_refresh_token_rejects_expired_grants(
    active_grant: tuple[SessionGrant, str],
    container: Container,
    config: Config,
):
    grant, refresh_secret = active_grant
    now = timezone.now()
    SessionGrant.objects.filter(id=grant.id).update(
        issued_at=now - timedelta(days=2),
        expires_at=now - timedelta(days=1),
    )

    with pytest.raises(AuthenticationError):
        handle_rotate_refresh_token_command(
            cmd=RotateRefreshTokenCommand(
                refresh_token=f"{grant.id.hex}:{refresh_secret}",
                access_token_ttl=config.access_token_ttl,
                refresh_token_ttl=config.refresh_token_ttl,
                refresh_token_size=config.refresh_token_size,
            ),
            hasher=container.hmac_hasher,
            jwt_service=container.jwt_service,
            role_manager=container.role_manager,
        )
