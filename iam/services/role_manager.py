from django.db import IntegrityError, transaction

from core.rbac import Role
from core.utils.dt import get_current_datetime
from iam.models import User
from iam.models.user_role import UserRole


class RoleManager:
    """Manage application role assignments for users."""

    def assign(self, user: User, role: Role) -> None:
        """Assign an active role to a user.

        :param user: User receiving the role.
        :param role: Role to assign.
        :raises ValueError: If the user already has an active assignment for the role.
        """
        if UserRole.objects.filter(user=user, role=role.value, deleted_at__isnull=True).exists():
            raise ValueError(f"user already has role '{role.value}'")
        try:
            # The database constraint is the final guard against concurrent assignments.
            with transaction.atomic():
                UserRole.objects.create(user=user, role=role.value)
        except IntegrityError as exc:
            raise ValueError(f"user already has role '{role.value}'") from exc

    def remove(self, user: User, role: Role) -> None:
        """Remove an active role assignment from a user.

        :param user: User losing the role.
        :param role: Role to remove.
        :raises ValueError: If the user does not have an active assignment for the role.
        """
        user_role = UserRole.objects.filter(
            user=user,
            role=role.value,
            deleted_at__isnull=True,
        ).first()
        if user_role is None:
            raise ValueError(f"user does not have role '{role.value}'")

        user_role.deleted_at = get_current_datetime()
        user_role.save(update_fields=["deleted_at"])

    def get_roles(self, user: User) -> set[Role]:
        """Return all active roles assigned to a user.

        :param user: User whose roles should be retrieved.
        :return: Set of active roles assigned to the user.
        """
        user_roles = UserRole.objects.filter(user=user, deleted_at__isnull=True)
        return {Role(user_role.role) for user_role in user_roles}

    def has_role(self, user: User, role: Role) -> bool:
        """Check whether a user has an active role assignment.

        :param user: User whose role assignment should be checked.
        :param role: Role to check for.
        :return: ``True`` if the role is assigned, otherwise ``False``.
        """
        return UserRole.objects.filter(user=user, role=role.value, deleted_at__isnull=True).exists()
