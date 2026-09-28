import pytest
from django.test import Client
from django.urls import reverse

from core.errors import ErrorCode
from core.rbac import Role

pytestmark = pytest.mark.django_db


@pytest.fixture
def login_url() -> str:
    return reverse("login")


@pytest.fixture
def me_url() -> str:
    return reverse("me")


@pytest.fixture
def user_data(client: Client) -> dict[str, str]:
    creds = {"username": "test-user", "password": "test-password"}
    resp = client.post(reverse("signup"), data=creds, content_type="application/json")
    assert resp.status_code == 201
    resp_data = resp.json()
    return {**creds, "id": resp_data["id"]}


@pytest.fixture
def access_token(client: Client, login_url: str, user_data: dict[str, str]) -> str:
    resp = client.post(
        login_url,
        data={"username": user_data["username"], "password": user_data["password"]},
        content_type="application/json",
    )
    assert resp.status_code == 200
    resp_data = resp.json()
    return resp_data["access_token"]


def test_me_returns_the_authenticated_principal(
    client: Client, me_url: str, user_data: dict[str, str], access_token: str
):
    resp = client.get(me_url, HTTP_AUTHORIZATION=f"Bearer {access_token}")

    assert resp.status_code == 200
    resp_data = resp.json()
    assert resp_data == {"id": user_data["id"], "roles": [Role.NORMAL.value]}


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
