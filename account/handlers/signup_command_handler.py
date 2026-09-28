from django.db import IntegrityError, transaction
from django.utils.translation import gettext as _

from account.commands import SignupCommand
from account.models import User
from account.services import RoleManager
from core.errors import ConflictError
from core.rbac import Role


@transaction.atomic
def handle_signup_command(cmd: SignupCommand, role_manager: RoleManager) -> User:
    """Handles the SignupCommand and creates a new user.

    :param cmd: The SignupCommand containing user signup data.
    :return: The newly created User instance.
    """

    username = cmd.username.strip().lower()

    if User.objects.filter(username=username, deleted_at__isnull=True).exists():
        raise ConflictError(
            _("user with this username already exists."),
            username=username,
        )

    try:
        user = User.objects.create_user(username=username, password=cmd.password)
        role_manager.assign(user=user, role=Role.NORMAL)
        return user
    except IntegrityError as exc:  # to avoid race conditions
        raise ConflictError(
            _("user with this username already exists."),
            username=username,
        ) from exc
