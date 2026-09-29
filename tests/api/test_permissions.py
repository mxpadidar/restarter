from importlib import import_module
from types import SimpleNamespace
from typing import cast
from uuid import uuid4

import pytest
from rest_framework.request import Request

from account.dtos import AuthUser
from account.perms import UserPerm, UserRolePerm
from api.perms import has_any_perm, has_any_role, has_perms
from api.perms.has_perms import HasPermissions
from core.rbac import Rbac, Role


def create_request(*, roles: set[Role]) -> Request:
    return cast(
        Request,
        SimpleNamespace(
            user=AuthUser(
                user_id=uuid4(),
                session_grant_id=uuid4(),
                roles=roles,
            )
        ),
    )


def test_has_perms_grants_access_when_a_role_grants_the_permission():
    (permission_class,) = has_perms(UserPerm.READ)
    request = create_request(roles={Role.ADMIN})

    assert permission_class().has_permission(request) is True


def test_has_perms_denies_access_when_no_role_grants_the_permission():
    (permission_class,) = has_perms(UserPerm.READ)
    request = create_request(roles={Role.NORMAL})

    assert permission_class().has_permission(request) is False


def test_has_perms_denies_requests_without_an_auth_user():
    (permission_class,) = has_perms(UserPerm.READ)
    request = cast(Request, SimpleNamespace(user=object()))

    assert permission_class().has_permission(request) is False


def test_has_permissions_denies_access_without_a_declared_permission():
    request = create_request(roles={Role.ADMIN})

    assert HasPermissions().has_permission(request) is False


def test_has_perms_requires_every_permission(monkeypatch: pytest.MonkeyPatch):
    rbac = Rbac([{Role.NORMAL: {UserPerm.READ.code}}])
    permission_module = import_module("api.perms.has_perms")
    monkeypatch.setattr(permission_module, "get_container", lambda: SimpleNamespace(rbac=rbac))
    request = create_request(roles={Role.NORMAL})
    (permission_class,) = has_perms(UserPerm.READ, UserRolePerm.READ)

    assert permission_class().has_permission(request) is False


def test_has_perms_grants_access_when_every_permission_is_granted(
    monkeypatch: pytest.MonkeyPatch,
):
    rbac = Rbac([{Role.NORMAL: {UserPerm.READ.code, UserRolePerm.READ.code}}])
    permission_module = import_module("api.perms.has_perms")
    monkeypatch.setattr(permission_module, "get_container", lambda: SimpleNamespace(rbac=rbac))
    request = create_request(roles={Role.NORMAL})
    (permission_class,) = has_perms(UserPerm.READ, UserRolePerm.READ)

    assert permission_class().has_permission(request) is True


def test_has_perms_rejects_an_empty_permission_list():
    with pytest.raises(ValueError):
        has_perms()


def test_has_perms_rejects_non_permission_values():
    with pytest.raises(TypeError):
        has_perms(UserPerm.READ, "account:user:create")  # type: ignore[arg-type]


def test_has_any_perm_grants_access_when_a_role_grants_any_required_permission(monkeypatch):
    rbac = Rbac([{Role.NORMAL: {UserPerm.READ.code}}])
    permission_module = import_module("api.perms.has_any_perm")
    monkeypatch.setattr(permission_module, "get_container", lambda: SimpleNamespace(rbac=rbac))
    (permission_class,) = has_any_perm(UserRolePerm.READ, UserPerm.READ)
    request = create_request(roles={Role.NORMAL})

    assert permission_class().has_permission(request) is True


def test_has_any_perm_denies_access_when_no_role_grants_a_required_permission():
    (permission_class,) = has_any_perm(UserPerm.READ, UserRolePerm.READ)
    request = create_request(roles={Role.NORMAL})

    assert permission_class().has_permission(request) is False


def test_has_any_role_grants_access_when_the_principal_has_a_required_role():
    (permission_class,) = has_any_role(Role.ADMIN, Role.NORMAL)
    request = create_request(roles={Role.NORMAL})

    assert permission_class().has_permission(request) is True


def test_has_any_role_denies_access_when_the_principal_has_no_required_role():
    (permission_class,) = has_any_role(Role.ADMIN)
    request = create_request(roles={Role.NORMAL})

    assert permission_class().has_permission(request) is False


def test_has_any_perm_rejects_an_empty_permission_list():
    with pytest.raises(ValueError):
        has_any_perm()


def test_has_any_perm_rejects_non_permission_values():
    with pytest.raises(TypeError):
        has_any_perm(UserPerm.READ, "account:user:create")  # type: ignore[arg-type]


def test_has_any_role_rejects_an_empty_role_list():
    with pytest.raises(ValueError):
        has_any_role()


def test_has_any_role_rejects_non_role_values():
    with pytest.raises(TypeError):
        has_any_role(Role.ADMIN, "normal")  # type: ignore[arg-type]
