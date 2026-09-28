# type: ignore[reportAssignmentType]

import uuid

from django.db import models

from core.rbac import Role

from .user import User


class UserRole(models.Model):
    """User role model for managing user roles and permissions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    user: User = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roles")
    role: Role = models.CharField(
        max_length=50,
        choices=[(role.value, role.name) for role in Role],
        editable=False,
    )

    class Meta:
        db_table = "user_roles"
        default_permissions = ()
        ordering = ("-created_at", "-id")

        constraints = [  # noqa: RUF012
            models.CheckConstraint(
                condition=models.Q(role__in=[role.value for role in Role]),
                name="user_roles_role_is_valid",
            ),
            models.UniqueConstraint(
                fields=("user", "role"),
                condition=models.Q(deleted_at__isnull=True),
                name="user_roles_active_assignment_is_unique",
            ),
        ]

    def __str__(self) -> str:
        """Return the user's role name as a string representation."""
        return f"{self.user.username} - {self.role}"
