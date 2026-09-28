import pytest
from django.test import Client
from django.urls import reverse

from core.errors import ErrorCode

pytestmark = pytest.mark.django_db


@pytest.fixture
def logout_url() -> str:
    return reverse("logout")


@pytest.fixture
def rotate_refresh_token_url() -> str:
    return reverse("rotate-refresh-token")


@pytest.fixture
def refresh_token(client: Client) -> str:
    creds = {"username": "test-user", "password": "test-password"}
    resp = client.post(reverse("signup"), data=creds, content_type="application/json")
    assert resp.status_code == 201

    resp = client.post(reverse("login"), data=creds, content_type="application/json")
    assert resp.status_code == 200
    resp_data = resp.json()
    return resp_data["refresh_token"]


def test_logout_revokes_the_refresh_token(
    client: Client, logout_url: str, rotate_refresh_token_url: str, refresh_token: str
):
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
