import pytest
from django.urls import reverse


@pytest.fixture
def user_list_url() -> str:
    return reverse("user-list")


@pytest.fixture
def signup_url() -> str:
    return reverse("signup")


@pytest.fixture
def login_url() -> str:
    return reverse("login")


@pytest.fixture
def logout_url() -> str:
    return reverse("logout")


@pytest.fixture
def me_url() -> str:
    return reverse("me")


@pytest.fixture
def token_rotate_url() -> str:
    return reverse("token-rotate")
