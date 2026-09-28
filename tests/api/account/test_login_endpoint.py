import pytest
from django.test import Client

from core.errors import ErrorCode

pytestmark = pytest.mark.django_db


def test_login_returns_an_access_and_refresh_token(
    client: Client, auth_creds: dict[str, str], login_url: str
):
    resp = client.post(login_url, data=auth_creds, content_type="application/json")
    assert resp.status_code == 200

    resp_data = resp.json()
    assert set(resp_data) == {"access_token", "refresh_token", "token_type", "expires_at"}
    assert resp_data["token_type"] == "Bearer"
    assert resp_data["expires_at"] is not None
    assert resp_data["access_token"] is not None
    assert resp_data["refresh_token"] is not None


def test_login_rejects_invalid_input(client: Client, login_url: str):
    resp = client.post(login_url, data={"username": "user"}, content_type="application/json")
    assert resp.status_code == 400

    resp_data = resp.json()
    assert resp_data["error"]["code"] == ErrorCode.VALIDATION_ERROR


def test_login_rejects_invalid_credentials(
    client: Client, auth_creds: dict[str, str], login_url: str
):
    resp = client.post(
        login_url,
        data={"username": auth_creds["username"], "password": "wrong-password"},
        content_type="application/json",
    )
    assert resp.status_code == 401

    resp_data = resp.json()
    assert resp_data["error"]["code"] == ErrorCode.AUTHENTICATION_FAILED
