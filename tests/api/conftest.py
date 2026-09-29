import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    """Provide a DRF API client for API endpoint tests."""
    return APIClient()


@pytest.fixture
def auth_creds(api_client: APIClient) -> dict[str, str]:
    """Create a user through the signup endpoint and return its credentials."""
    creds = {"username": "test-user", "password": "test-password"}
    resp = api_client.post(reverse("signup"), data=creds, format="json")
    assert resp.status_code == 201
    return creds


@pytest.fixture
def auth_tokens(api_client: APIClient, auth_creds: dict[str, str]) -> dict[str, str]:
    """Return an access and refresh token pair for a signed-up user."""
    resp = api_client.post(reverse("login"), data=auth_creds, format="json")
    assert resp.status_code == 200
    return resp.json()
