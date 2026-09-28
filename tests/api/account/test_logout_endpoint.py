import pytest
from django.test import Client

from core.errors import ErrorCode

pytestmark = pytest.mark.django_db


def test_logout_revokes_the_refresh_token(
    client: Client,
    logout_url: str,
    rotate_refresh_token_url: str,
    auth_tokens: dict[str, str],
):
    refresh_token = auth_tokens["refresh_token"]
    resp = client.post(
        logout_url,
        data={"refresh_token": refresh_token},
        content_type="application/json",
    )

    assert resp.status_code == 204
    assert resp.content == b""

    resp = client.post(
        rotate_refresh_token_url,
        data={"refresh_token": refresh_token},
        content_type="application/json",
    )

    assert resp.status_code == 401
    resp_data = resp.json()
    assert resp_data["error"]["code"] == ErrorCode.AUTHENTICATION_FAILED


def test_logout_rejects_invalid_input(client: Client, logout_url: str):
    resp = client.post(logout_url, data={}, content_type="application/json")

    assert resp.status_code == 400
    resp_data = resp.json()
    assert resp_data["error"]["code"] == ErrorCode.VALIDATION_ERROR


def test_logout_rejects_invalid_refresh_tokens(client: Client, logout_url: str):
    resp = client.post(
        logout_url,
        data={"refresh_token": "invalid-token"},
        content_type="application/json",
    )

    assert resp.status_code == 401
    resp_data = resp.json()
    assert resp_data["error"]["code"] == ErrorCode.AUTHENTICATION_FAILED
