# type: ignore[reportAttributeAccessIssue]

"""Superuser-only Django admin site configuration."""

from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

UserModel = get_user_model()


class SuperuserAuthenticationForm(AuthenticationForm):
    """Authenticate only enabled superusers for the admin site."""

    def confirm_login_allowed(self, user) -> None:
        """Reject authenticated users that are not superusers."""
        if not isinstance(user, UserModel) or not user.is_superuser:
            raise ValidationError(
                "This account does not have access to the admin site.",
                code="admin_access_denied",
            )


class SuperuserAdminSite(AdminSite):
    """Django admin site accessible only to enabled superusers."""

    login_form = SuperuserAuthenticationForm

    def has_permission(self, request) -> bool:
        """Return whether the request user may access the admin site."""
        user = request.user
        return bool(
            isinstance(user, UserModel)
            and user.is_authenticated
            and user.is_superuser
            and user.deleted_at is None
            and user.deactivated_at is None
        )


admin_site = SuperuserAdminSite(name="admin")
