import pytest
from django.utils import timezone

from conf.config import Config
from conf.container import Container
from core.errors import AuthenticationError
from core.rbac import Role
from core.utils import datetime_to_timestamp
from iam.commands import LoginCommand
from iam.dtos import TokenPair
from iam.handlers import handle_login_command
from iam.models import SessionGrant, User

pytestmark = pytest.mark.django_db


def test_handle_login_command_creates_session_and_tokens(container: Container, config: Config):
    """A valid login should create a session and return both token types."""
    user = User.objects.create_user(username="user", password="strong-password")
    container.role_manager.assign(user, Role.NORMAL)

    result = handle_login_command(
        LoginCommand(
            username=" USER ",
            password="strong-password",
            access_token_ttl=config.access_token_ttl,
            refresh_token_ttl=config.refresh_token_ttl,
            refresh_token_size=config.refresh_token_size,
            ip_address="192.0.2.1",
        ),
        hasher=container.hmac_hasher,
        jwt_service=container.jwt_service,
        role_manager=container.role_manager,
    )

    grant = SessionGrant.objects.get(user=user)
    grant_id, refresh_secret = TokenPair.parse_refresh_token(result.refresh_token)
    payload = container.jwt_service.decode(result.access_token)

    assert payload["exp"] == datetime_to_timestamp(result.expires_at)
    assert grant.id == grant_id
    assert grant.ip_address == "192.0.2.1"
    assert container.hmac_hasher.verify(plain_text=refresh_secret, expected_hash=grant.secret_hash)
    assert refresh_secret
    assert payload["sub"] == user.id.hex
    assert payload["jti"] == grant.id.hex
    assert payload["roles"] == [Role.NORMAL.value]


def test_handle_login_command_rejects_unknown_username(container: Container, config: Config):
    """An unknown username should produce a generic authentication error."""
    User.objects.create_user(username="user", password="strong-password")

    with pytest.raises(AuthenticationError):
        handle_login_command(
            LoginCommand(
                username="missing-user",
                password="strong-password",
                access_token_ttl=config.access_token_ttl,
                refresh_token_ttl=config.refresh_token_ttl,
                refresh_token_size=config.refresh_token_size,
            ),
            hasher=container.hmac_hasher,
            jwt_service=container.jwt_service,
            role_manager=container.role_manager,
        )

    assert not SessionGrant.objects.exists()


def test_handle_login_command_rejects_incorrect_password(container: Container, config: Config):
    """An incorrect password should produce a generic authentication error."""
    User.objects.create_user(username="user", password="strong-password")

    with pytest.raises(AuthenticationError):
        handle_login_command(
            LoginCommand(
                username="user",
                password="wrong",
                access_token_ttl=config.access_token_ttl,
                refresh_token_ttl=config.refresh_token_ttl,
                refresh_token_size=config.refresh_token_size,
            ),
            hasher=container.hmac_hasher,
            jwt_service=container.jwt_service,
            role_manager=container.role_manager,
        )

    assert not SessionGrant.objects.exists()


def test_handle_login_command_rejects_a_deleted_user(container: Container, config: Config):
    """Deleted users should not be able to create an authenticated session."""
    user = User.objects.create_user(username="user", password="strong-password")
    user.deleted_at = timezone.now()
    user.save(update_fields=("deleted_at",))

    with pytest.raises(AuthenticationError):
        handle_login_command(
            LoginCommand(
                username="user",
                password="strong-password",
                access_token_ttl=config.access_token_ttl,
                refresh_token_ttl=config.refresh_token_ttl,
                refresh_token_size=config.refresh_token_size,
            ),
            hasher=container.hmac_hasher,
            jwt_service=container.jwt_service,
            role_manager=container.role_manager,
        )

    assert not SessionGrant.objects.exists()


def test_handle_login_command_rejects_a_deactivated_user(container: Container, config: Config):
    """Deactivated users should not be able to create an authenticated session."""
    user = User.objects.create_user(username="user", password="strong-password")
    user.deactivated_at = timezone.now()
    user.save(update_fields=("deactivated_at",))

    with pytest.raises(AuthenticationError):
        handle_login_command(
            LoginCommand(
                username="user",
                password="strong-password",
                access_token_ttl=config.access_token_ttl,
                refresh_token_ttl=config.refresh_token_ttl,
                refresh_token_size=config.refresh_token_size,
            ),
            hasher=container.hmac_hasher,
            jwt_service=container.jwt_service,
            role_manager=container.role_manager,
        )

    assert not SessionGrant.objects.exists()
