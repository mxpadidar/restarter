"""Admin configuration for custom user and role-assignment models."""

from django.contrib import admin

from iam.admin_site import admin_site

from .models import User, UserRole


@admin.register(User, site=admin_site)
class UserAdmin(admin.ModelAdmin):
    """Display users in the superuser-only admin site."""

    list_display = ("username", "is_superuser", "deactivated_at", "deleted_at")
    search_fields = ("username",)
    exclude = ("password",)

    def has_add_permission(self, request) -> bool:
        """Prevent incomplete user creation outside the user manager."""
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(UserRole, site=admin_site)
class UserRoleAdmin(admin.ModelAdmin):
    """Display role assignments managed by the role service layer."""

    list_display = ("user", "role", "deleted_at")
    search_fields = ("user__username",)
    readonly_fields = ("id", "user", "role", "created_at", "deleted_at")

    def has_add_permission(self, request) -> bool:
        """Keep role assignment creation in the role service layer."""
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        """Keep role assignment removal in the role service layer."""
        return False
