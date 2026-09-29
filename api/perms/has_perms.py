from rest_framework import permissions
from rest_framework.request import Request

from account.dtos import AuthUser
from conf.container import get_container
from core.rbac import Perm


class HasPermissions(permissions.BasePermission):
    """Grant access when the authenticated principal has every required permission."""

    required_permissions: tuple[Perm, ...] = ()

    def has_permission(self, request: Request, *args, **kwargs) -> bool:
        """Return whether the request principal has every required permission."""
        if not self.required_permissions or not isinstance(request.user, AuthUser):
            return False

        if not request.user.is_authenticated:
            return False

        rbac = get_container().rbac

        return all(
            rbac.has_perm(request.user.roles, permission.code)
            for permission in self.required_permissions
        )


def has_perms(*permissions: Perm) -> tuple[type[HasPermissions]]:
    """Build one DRF permission class requiring every given RBAC permission."""
    if not permissions:
        raise ValueError("at least one permission is required")

    for permission in permissions:
        if not isinstance(permission, Perm):
            raise TypeError("permissions must be Perm instances")

    class RequiredPermissions(HasPermissions):
        required_permissions = permissions

    return (RequiredPermissions,)
