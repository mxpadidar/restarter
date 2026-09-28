import pytest
from django.test import Client
from django.urls import reverse


@pytest.fixture
def auth_creds(client: Client) -> dict[str, str]:
    """Create a user through the signup endpoint and return its credentials."""
    creds = {"username": "test-user", "password": "test-password"}
    resp = client.post(reverse("signup"), data=creds, content_type="application/json")
    assert resp.status_code == 201
    return creds


@pytest.fixture
def auth_tokens(client: Client, auth_creds: dict[str, str]) -> dict[str, str]:
    """Return an access and refresh token pair for a signed-up user."""
    resp = client.post(reverse("login"), data=auth_creds, content_type="application/json")
    assert resp.status_code == 200
    return resp.json()
