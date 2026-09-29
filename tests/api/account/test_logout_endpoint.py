import pytest
from rest_framework.test import APIClient

from core.errors import ErrorCode

pytestmark = pytest.mark.django_db


def test_logout_revokes_the_refresh_token(
    api_client: APIClient,
    logout_url: str,
    token_rotate_url: str,
    auth_tokens: dict[str, str],
):
    refresh_token = auth_tokens["refresh_token"]
    resp = api_client.post(
        logout_url,
        data={"refresh_token": refresh_token},
        format="json",
    )

    assert resp.status_code == 204
    assert resp.content == b""

    resp = api_client.post(
        token_rotate_url,
        data={"refresh_token": refresh_token},
        format="json",
    )

    assert resp.status_code == 401
    resp_data = resp.json()
    assert resp_data["error"]["code"] == ErrorCode.AUTHENTICATION_FAILED


def test_logout_rejects_invalid_input(api_client: APIClient, logout_url: str):
    resp = api_client.post(logout_url, data={}, format="json")

    assert resp.status_code == 400
    resp_data = resp.json()
    assert resp_data["error"]["code"] == ErrorCode.VALIDATION_ERROR


def test_logout_rejects_invalid_refresh_tokens(api_client: APIClient, logout_url: str):
    resp = api_client.post(
        logout_url,
        data={"refresh_token": "invalid-token"},
        format="json",
    )

    assert resp.status_code == 401
    resp_data = resp.json()
    assert resp_data["error"]["code"] == ErrorCode.AUTHENTICATION_FAILED
