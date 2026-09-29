from rest_framework import permissions
from rest_framework.request import Request

from account.dtos import AuthUser
from core.rbac import Role


class HasAnyRole(permissions.BasePermission):
    """Grant access when the authenticated principal has any required role."""

    required_roles: frozenset[Role] = frozenset()

    def has_permission(self, request: Request, *args, **kwargs) -> bool:
        """Return whether the request principal has any required role."""
        return bool(
            self.required_roles
            and isinstance(request.user, AuthUser)
            and request.user.is_authenticated
            and self.required_roles.intersection(request.user.roles)
        )


def has_any_role(*roles: Role) -> tuple[type[HasAnyRole]]:
    """Build one DRF permission class requiring any of the given application roles."""
    if not roles:
        raise ValueError("at least one role is required")

    for role in roles:
        if not isinstance(role, Role):
            raise TypeError("roles must be Role instances")

    class RequiredRoles(HasAnyRole):
        required_roles = frozenset(roles)

    return (RequiredRoles,)
