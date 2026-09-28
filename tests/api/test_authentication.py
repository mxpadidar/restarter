from typing import cast
from uuid import UUID, uuid4

import pytest
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from api.authentication import JWTAuthentication
from conf.config import Config
from conf.container import Container
from core.rbac import Role
from core.utils import datetime_to_timestamp
from iam.dtos import AuthUser
from iam.models import User
from iam.services.jwt_service import JwtPayload

pytestmark = pytest.mark.django_db


@pytest.fixture
def request_factory() -> APIRequestFactory:
    return APIRequestFactory()


@pytest.fixture
def active_user() -> User:
    return User.objects.create_user(username="user", password="test-password")


def create_access_token(
    *, container: Container, config: Config, user: User, roles: list[Role]
) -> tuple[str, str]:
    session_grant_id = uuid4()
    issued_at = timezone.now()
    token = container.jwt_service.encode(
        sub=user.id.hex,
        jti=session_grant_id.hex,
        roles=[role.value for role in roles],
        iat=datetime_to_timestamp(issued_at),
        exp=datetime_to_timestamp(issued_at + config.access_token_ttl),
    )
    return token, session_grant_id.hex


def test_jwt_authentication_sets_an_auth_user_and_roles(
    request_factory: APIRequestFactory,
    active_user: User,
    container: Container,
    config: Config,
):
    token, session_grant_id = create_access_token(
        container=container,
        config=config,
        user=active_user,
        roles=[Role.NORMAL],
    )
    request = Request(
        request_factory.get("/", HTTP_AUTHORIZATION=f"Bearer {token}"),
        authenticators=[JWTAuthentication()],
    )

    auth_user = cast(AuthUser, request.user)
    assert auth_user == AuthUser(
        user_id=active_user.id,
        session_grant_id=UUID(hex=session_grant_id),
        roles={Role.NORMAL},
    )
    assert auth_user.roles == {Role.NORMAL}
    auth_payload = cast(JwtPayload, request.auth)
    assert auth_payload["sub"] == active_user.id.hex
    assert auth_payload["jti"] == session_grant_id


def test_jwt_authentication_allows_requests_without_an_authorization_header(
    request_factory: APIRequestFactory,
):
    request = Request(request_factory.get("/"))

    result = JWTAuthentication().authenticate(request)

    assert result is None


def test_jwt_authentication_rejects_a_bearer_header_without_a_token(
    request_factory: APIRequestFactory,
):
    request = Request(request_factory.get("/", HTTP_AUTHORIZATION="Bearer"))

    with pytest.raises(exceptions.AuthenticationFailed):
        JWTAuthentication().authenticate(request)


def test_jwt_authentication_rejects_an_invalid_access_token(
    request_factory: APIRequestFactory,
):
    request = Request(request_factory.get("/", HTTP_AUTHORIZATION="Bearer invalid-token"))

    with pytest.raises(exceptions.AuthenticationFailed):
        JWTAuthentication().authenticate(request)
