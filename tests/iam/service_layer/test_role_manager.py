import pytest
from django.db import IntegrityError

from core.rbac import Role
from iam.models import User, UserRole
from iam.service_layer.role_manager import RoleManager

pytestmark = pytest.mark.django_db


@pytest.fixture
def unassigned_user() -> User:
    """Create a user without roles."""
    return User.objects.create_user(username="unassigned-user", password="test-password")


@pytest.fixture
def role_manager() -> RoleManager:
    """Provide the application service responsible for role assignments."""
    return RoleManager()


def test_assign_adds_application_roles(unassigned_user: User, role_manager: RoleManager):
    role_manager.assign(unassigned_user, Role.NORMAL)
    role_manager.assign(unassigned_user, Role.ADMIN)
    assert role_manager.get_roles(unassigned_user) == {Role.ADMIN, Role.NORMAL}


def test_assign_rejects_duplicate_assignment(unassigned_user: User, role_manager: RoleManager):
    role_manager.assign(unassigned_user, Role.NORMAL)

    with pytest.raises(ValueError):
        role_manager.assign(unassigned_user, Role.NORMAL)


def test_assign_translates_a_concurrent_duplicate_error(
    unassigned_user: User,
    role_manager: RoleManager,
    monkeypatch: pytest.MonkeyPatch,
):
    def raise_integrity_error(**kwargs) -> None:
        raise IntegrityError

    monkeypatch.setattr(UserRole.objects, "create", raise_integrity_error)

    with pytest.raises(ValueError):
        role_manager.assign(unassigned_user, Role.NORMAL)


def test_remove_requires_an_assigned_role(unassigned_user: User, role_manager: RoleManager):
    with pytest.raises(ValueError):
        role_manager.remove(unassigned_user, Role.ADMIN)


def test_remove_removes_an_assigned_role(unassigned_user: User, role_manager: RoleManager):
    role_manager.assign(unassigned_user, Role.NORMAL)
    role_manager.remove(unassigned_user, Role.NORMAL)

    assert role_manager.get_roles(unassigned_user) == set()
    assert UserRole.objects.filter(
        user=unassigned_user,
        role=Role.NORMAL.value,
        deleted_at__isnull=False,
    ).exists()


def test_assign_allows_a_removed_role_to_be_reassigned(
    unassigned_user: User,
    role_manager: RoleManager,
):
    role_manager.assign(unassigned_user, Role.NORMAL)
    role_manager.remove(unassigned_user, Role.NORMAL)
    role_manager.assign(unassigned_user, Role.NORMAL)

    assert role_manager.get_roles(unassigned_user) == {Role.NORMAL}
    assert (
        UserRole.objects.filter(
            user=unassigned_user,
            role=Role.NORMAL.value,
            deleted_at__isnull=True,
        ).count()
        == 1
    )


def test_has_role(unassigned_user: User, role_manager: RoleManager):
    role_manager.assign(unassigned_user, Role.NORMAL)
    assert role_manager.has_role(unassigned_user, Role.NORMAL)
    assert not role_manager.has_role(unassigned_user, Role.ADMIN)
