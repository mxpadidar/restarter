import pytest
from django.test import Client

from account.models import SessionGrant, User
from core.errors import ErrorCode

pytestmark = pytest.mark.django_db


def test_me_returns_the_authenticated_principal(
    client: Client,
    me_url: str,
    auth_creds: dict[str, str],
    auth_tokens: dict[str, str],
):
    access_token = auth_tokens["access_token"]
    resp = client.get(me_url, HTTP_AUTHORIZATION=f"Bearer {access_token}")

    assert resp.status_code == 200
    resp_data = resp.json()
    user = User.objects.get(username=auth_creds["username"])
    grant = SessionGrant.objects.get(user=user, revoked_at__isnull=True)
    assert set(resp_data) == {"id", "username", "created_at", "last_login"}
    assert resp_data["id"] == str(user.id)
    assert resp_data["username"] == user.username
    assert resp_data["created_at"] is not None
    assert resp_data["last_login"] is not None
    assert grant.issued_at.isoformat().startswith(resp_data["last_login"].replace("Z", "+00:00"))


def test_me_rejects_an_unauthenticated_request(client: Client, me_url: str):
    resp = client.get(me_url)

    assert resp.status_code == 401
    resp_data = resp.json()
    assert resp_data["error"]["code"] == ErrorCode.AUTHENTICATION_FAILED


def test_me_rejects_an_invalid_access_token(client: Client, me_url: str):
    resp = client.get(me_url, HTTP_AUTHORIZATION="Bearer invalid-token")

    assert resp.status_code == 401
    resp_data = resp.json()
    assert resp_data["error"]["code"] == ErrorCode.AUTHENTICATION_FAILED


def test_me_rejects_a_revoked_session_grant(
    client: Client,
    me_url: str,
    auth_creds: dict[str, str],
    auth_tokens: dict[str, str],
):
    access_token = auth_tokens["access_token"]
    user = User.objects.get(username=auth_creds["username"])
    grant = SessionGrant.objects.get(user=user, revoked_at__isnull=True)
    grant.revoke()

    resp = client.get(me_url, HTTP_AUTHORIZATION=f"Bearer {access_token}")

    assert resp.status_code == 401
    resp_data = resp.json()
    assert resp_data["error"]["code"] == ErrorCode.AUTHENTICATION_FAILED
