import pytest
from django.test import Client
from django.urls import reverse

from core.errors import ErrorCode

pytestmark = pytest.mark.django_db


@pytest.fixture
def login_url() -> str:
    return reverse("login")


@pytest.fixture
def rotate_refresh_token_url() -> str:
    return reverse("rotate-refresh-token")


@pytest.fixture
def user_creds(client: Client) -> dict[str, str]:
    signup_url = reverse("signup")
    creds = {"username": "test-user", "password": "test-password"}
    response = client.post(signup_url, data=creds, content_type="application/json")
    assert response.status_code == 201
    return creds


@pytest.fixture
def refresh_token(client: Client, login_url: str, user_creds: dict[str, str]) -> str:
    response = client.post(login_url, data=user_creds, content_type="application/json")
    assert response.status_code == 200
    return response.json()["refresh_token"]


def test_rotate_refresh_token_returns_a_new_token_pair(
    client: Client, rotate_refresh_token_url: str, refresh_token: str
):
    response = client.post(
        rotate_refresh_token_url,
        data={"refresh_token": refresh_token},
        content_type="application/json",
    )

    assert response.status_code == 200
    response_data = response.json()
    assert set(response_data) == {"access_token", "refresh_token", "token_type", "expires_at"}
    assert response_data["access_token"]
    assert response_data["refresh_token"]
    assert response_data["refresh_token"] != refresh_token
    assert response_data["token_type"] == "Bearer"
    assert response_data["expires_at"] is not None


def test_rotate_refresh_token_rejects_invalid_input(client: Client, rotate_refresh_token_url: str):
    response = client.post(
        rotate_refresh_token_url,
        data={},
        content_type="application/json",
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == ErrorCode.VALIDATION_ERROR


def test_rotate_refresh_token_rejects_invalid_refresh_tokens(
    client: Client, rotate_refresh_token_url: str
):
    response = client.post(
        rotate_refresh_token_url,
        data={"refresh_token": "invalid-token"},
        content_type="application/json",
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == ErrorCode.AUTHENTICATION_FAILED
