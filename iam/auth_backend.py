from uuid import UUID

from django.contrib.auth.backends import BaseBackend

from conf.container import get_container
from core.rbac import Namespace
from iam.models import User

container = get_container()


class AuthBackend(BaseBackend):
    """Authenticate users and resolve permissions through application RBAC."""

    def authenticate(self, request, username=None, password=None, **kwargs) -> User | None:
        """Authenticate a user that is neither deleted nor deactivated."""
        if username is None or password is None:
            return None

        # normalize username
        username = str(username).strip().lower()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Run password hashing to mitigate username-enumeration timing attacks.
            User().set_password(password)
            return None

        if not user.is_active:
            return None

        if not user.check_password(password):
            return None

        return user

    def get_user(self, user_id: UUID) -> User | None:
        """Return a user that is neither deleted nor deactivated by primary key."""
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

        return user if user.deleted_at is None and user.deactivated_at is None else None

    def get_all_permissions(self, user_obj, obj=None) -> set[str]:
        """Return all permissions granted through the user's active roles."""
        if not isinstance(user_obj, User):
            return set()

        if not user_obj.is_active:
            return set()

        if obj is not None:
            return set()

        if user_obj.is_superuser:
            return set(container.rbac.get_all_permissions())

        user_roles = container.role_manager.get_roles(user_obj)
        return set(container.rbac.get_roles_permissions(user_roles))

    def has_perm(self, user_obj, perm: str, obj=None) -> bool:
        """Check whether a user has a permission."""
        if not isinstance(user_obj, User):
            return False

        if not user_obj.is_active:
            return False

        if user_obj.is_superuser:
            return True

        if obj is not None:
            return False

        user_roles = container.role_manager.get_roles(user_obj)

        return container.rbac.has_perm(user_roles, perm)

    def has_module_perms(self, user_obj, app_label: str) -> bool:
        """Check whether a user has any permission in a Django app namespace."""
        if not isinstance(user_obj, User):
            return False

        if not user_obj.is_active:
            return False

        if user_obj.is_superuser:
            return True

        try:
            namespace = Namespace(app_label)
        except ValueError:
            return False

        user_roles = container.role_manager.get_roles(user_obj)

        return container.rbac.has_namespace_perms(user_roles, namespace)
