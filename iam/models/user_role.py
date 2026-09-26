# type: ignore[reportAssignmentType]

from django.db import models

from core.base_model import BaseModel
from core.rbac import Role

from .user import User


class UserRole(BaseModel):
    """User role model for managing user roles and permissions."""

    user: User = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roles")
    role: Role = models.CharField(
        max_length=50,
        choices=[(role.value, role.name) for role in Role],
        editable=False,
    )

    class Meta(BaseModel.Meta):
        db_table = "user_roles"

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
