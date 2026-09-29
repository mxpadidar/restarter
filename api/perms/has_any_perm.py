from rest_framework import permissions
from rest_framework.request import Request

from account.dtos import AuthUser
from conf.container import get_container
from core.rbac import Perm


class HasAnyPerm(permissions.BasePermission):
    """Grant access when the authenticated principal has any required RBAC permission."""

    required_permissions: frozenset[Perm] = frozenset()

    def has_permission(self, request: Request, *args, **kwargs) -> bool:
        """Return whether the request principal has any required permission."""
        if not self.required_permissions or not isinstance(request.user, AuthUser):
            return False

        if not request.user.is_authenticated:
            return False

        rbac = get_container().rbac
        return any(
            rbac.has_perm(request.user.roles, permission.code)
            for permission in self.required_permissions
        )


def has_any_perm(*permissions: Perm) -> tuple[type[HasAnyPerm]]:
    """Build one DRF permission class requiring any of the given RBAC permissions."""
    if not permissions:
        raise ValueError("at least one permission is required")

    for permission in permissions:
        if not isinstance(permission, Perm):
            raise TypeError("permissions must be Perm instances")

    class RequiredAnyPerm(HasAnyPerm):
        required_permissions = frozenset(permissions)

    return (RequiredAnyPerm,)
