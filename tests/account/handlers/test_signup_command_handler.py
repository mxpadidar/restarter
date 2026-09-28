import pytest

from account.commands import SignupCommand
from account.handlers import handle_signup_command
from account.models import User
from conf.container import Container
from core.errors import ConflictError
from core.rbac import Role

pytestmark = pytest.mark.django_db


def test_signup_creates_a_normalized_user_with_the_normal_role(container: Container):
    user = handle_signup_command(
        SignupCommand(username="  New-User  ", password="test-password"),
        role_manager=container.role_manager,
    )

    assert user.username == "new-user"
    assert user.check_password("test-password")
    assert container.role_manager.get_roles(user) == {Role.NORMAL}


def test_signup_rejects_an_existing_username(container: Container):
    User.objects.create_user(username="existing-user", password="test-password")

    with pytest.raises(ConflictError) as exc_info:
        handle_signup_command(
            SignupCommand(username=" Existing-User ", password="another-password"),
            role_manager=container.role_manager,
        )

    assert exc_info.value.details == {"username": "existing-user"}
    assert User.objects.filter(username="existing-user").count() == 1
