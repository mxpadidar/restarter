import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from account.models import User
from conf.container import Container
from core.errors import ErrorCode
from core.rbac import Role

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin_access_token(
    api_client: APIClient,
    auth_creds: dict[str, str],
    container: Container,
    login_url: str,
) -> str:
    user = User.objects.get(username=auth_creds["username"])
    container.role_manager.assign(user, Role.ADMIN)

    resp = api_client.post(login_url, data=auth_creds, format="json")
    assert resp.status_code == 200
    resp_data = resp.json()
    return resp_data["access_token"]


def test_user_list_returns_non_deleted_users(
    api_client: APIClient, user_list_url: str, admin_access_token: str
):
    User.objects.create_user(username="active-user", password="test-password")
    deleted_user = User.objects.create_user(username="deleted-user", password="test-password")
    deleted_user.deleted_at = timezone.now()
    deleted_user.save(update_fields=["deleted_at"])

    resp = api_client.get(
        user_list_url,
        HTTP_AUTHORIZATION=f"Bearer {admin_access_token}",
    )

    assert resp.status_code == 200
    resp_data = resp.json()
    assert {user["username"] for user in resp_data} == {"test-user", "active-user"}
    assert all(
        set(user) == {"id", "username", "created_at", "deactivated_at"} for user in resp_data
    )


def test_user_list_rejects_an_unauthenticated_request(api_client: APIClient, user_list_url: str):
    resp = api_client.get(user_list_url)

    assert resp.status_code == 401
    resp_data = resp.json()
    assert resp_data["error"]["code"] == ErrorCode.AUTHENTICATION_FAILED


def test_user_list_rejects_a_user_without_read_permission(
    api_client: APIClient, user_list_url: str, auth_tokens: dict[str, str]
):
    resp = api_client.get(
        user_list_url,
        HTTP_AUTHORIZATION=f"Bearer {auth_tokens['access_token']}",
    )

    assert resp.status_code == 403
    resp_data = resp.json()
    assert resp_data["error"]["code"] == ErrorCode.PERMISSION_DENIED
