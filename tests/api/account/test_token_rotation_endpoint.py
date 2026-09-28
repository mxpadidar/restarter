import pytest
from django.test import Client

from core.errors import ErrorCode

pytestmark = pytest.mark.django_db


def test_token_rotation_returns_a_new_token_pair(
    client: Client, token_rotate_url: str, auth_tokens: dict[str, str]
):
    refresh_token = auth_tokens["refresh_token"]
    resp = client.post(
        token_rotate_url,
        data={"refresh_token": refresh_token},
        content_type="application/json",
    )

    assert resp.status_code == 200
    resp_data = resp.json()
    assert set(resp_data) == {"access_token", "refresh_token", "token_type", "expires_at"}
    assert resp_data["access_token"]
    assert resp_data["refresh_token"]
    assert resp_data["refresh_token"] != refresh_token
    assert resp_data["token_type"] == "Bearer"
    assert resp_data["expires_at"] is not None


def test_token_rotation_rejects_invalid_input(client: Client, token_rotate_url: str):
    resp = client.post(
        token_rotate_url,
        data={},
        content_type="application/json",
    )

    assert resp.status_code == 400
    resp_data = resp.json()
    assert resp_data["error"]["code"] == ErrorCode.VALIDATION_ERROR


def test_token_rotation_rejects_invalid_refresh_tokens(client: Client, token_rotate_url: str):
    resp = client.post(
        token_rotate_url,
        data={"refresh_token": "invalid-token"},
        content_type="application/json",
    )

    assert resp.status_code == 401
    resp_data = resp.json()
    assert resp_data["error"]["code"] == ErrorCode.AUTHENTICATION_FAILED
