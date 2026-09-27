from uuid import UUID

import pytest
from django.test import Client
from django.urls import reverse

from core.errors import ErrorCode

pytestmark = pytest.mark.django_db


@pytest.fixture
def signup_url() -> str:
    return reverse("signup")


def test_signup_creates_a_user(client: Client, signup_url: str):
    resp = client.post(
        signup_url,
        data={"username": "  New-User  ", "password": "test-password"},
        content_type="application/json",
    )
    assert resp.status_code == 201

    resp_data = resp.json()
    assert set(resp_data) == {"id"}
    assert UUID(resp_data["id"]).version == 7


def test_signup_rejects_invalid_input(client: Client, signup_url: str):
    resp = client.post(
        signup_url,
        data={"username": "new-user", "password": "short"},
        content_type="application/json",
    )
    assert resp.status_code == 400

    resp_data = resp.json()
    assert resp_data["error"]["code"] == ErrorCode.VALIDATION_ERROR


def test_signup_rejects_an_existing_username(client: Client, signup_url: str):
    success_resp = client.post(
        signup_url,
        data={"username": "existing-user", "password": "test-password"},
        content_type="application/json",
    )
    assert success_resp.status_code == 201

    resp = client.post(
        signup_url,
        data={"username": " Existing-User ", "password": "another-password"},
        content_type="application/json",
    )
    assert resp.status_code == 409

    resp_data = resp.json()
    assert resp_data["error"]["code"] == ErrorCode.CONFLICT
