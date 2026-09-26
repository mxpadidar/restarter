from django.contrib.auth import get_backends
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models

from core.base_model import BaseModel


class UserManager(BaseUserManager["User"]):
    """Create and manage users using username as the authentication identifier."""

    def create_user(self, username: str, password: str, **extra_fields) -> User:
        """Create and save a regular user."""
        username = username.strip().lower()
        if not username:
            raise ValueError("username is required")

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username: str, password: str, **extra_fields) -> User:
        """Create and save a superuser."""
        extra_fields.setdefault("is_superuser", True)

        if extra_fields["is_superuser"] is not True:
            raise ValueError("superuser must have is_superuser=True")

        return self.create_user(username=username, password=password, **extra_fields)


class User(AbstractBaseUser, BaseModel):
    """Application user used for authentication and authorization.

    The model stores user identity and authentication state while delegating
    permission checks to the configured authentication backends.
    """

    username = models.CharField(max_length=150, unique=True, editable=False)
    password = models.CharField(max_length=128)
    is_superuser = models.BooleanField(default=False)  # Grants access to the custom admin site.
    deactivated_at = models.DateTimeField(null=True, blank=True)

    objects: UserManager = UserManager()

    USERNAME_FIELD = "username"

    class Meta(BaseModel.Meta):  # type: ignore[reportIncompatibleVariableOverride]
        db_table = "users"

    def has_perm(self, perm, obj=None) -> bool:
        """Check whether any configured auth backend grants a permission.

        :param perm: Permission to check.
        :param obj: Optional object for object-level authorization.
        :return: ``True`` if any backend grants the permission.
        """
        return any(
            backend.has_perm(self, perm, obj)
            for backend in get_backends()
            if hasattr(backend, "has_perm")
        )

    def has_perms(self, perm_list, obj=None) -> bool:
        """Check whether every requested permission is granted.

        :param perm_list: Permissions to check.
        :param obj: Optional object for object-level authorization.
        :return: ``True`` when every permission is granted.
        """
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, app_label: str) -> bool:
        return any(
            backend.has_module_perms(self, app_label)  # type: ignore[reportGeneralTypeIssues]
            for backend in get_backends()
            if hasattr(backend, "has_module_perms")
        )

    def __str__(self) -> str:
        """Return the user's username."""
        return self.username
