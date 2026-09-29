from uuid import UUID

import pytest
from rest_framework.test import APIClient

from core.errors import ErrorCode

pytestmark = pytest.mark.django_db


def test_signup_creates_a_user(api_client: APIClient, signup_url: str):
    resp = api_client.post(
        signup_url,
        data={"username": "  New-User  ", "password": "test-password"},
        format="json",
    )
    assert resp.status_code == 201

    resp_data = resp.json()
    assert set(resp_data) == {"id"}
    assert UUID(resp_data["id"]).version == 7


def test_signup_rejects_invalid_input(api_client: APIClient, signup_url: str):
    resp = api_client.post(
        signup_url,
        data={"username": "new-user", "password": "short"},
        format="json",
    )
    assert resp.status_code == 400

    resp_data = resp.json()
    assert resp_data["error"]["code"] == ErrorCode.VALIDATION_ERROR


def test_signup_rejects_an_existing_username(api_client: APIClient, signup_url: str):
    success_resp = api_client.post(
        signup_url,
        data={"username": "existing-user", "password": "test-password"},
        format="json",
    )
    assert success_resp.status_code == 201

    resp = api_client.post(
        signup_url,
        data={"username": " Existing-User ", "password": "another-password"},
        format="json",
    )
    assert resp.status_code == 409

    resp_data = resp.json()
    assert resp_data["error"]["code"] == ErrorCode.CONFLICT
