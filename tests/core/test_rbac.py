from core.rbac import Rbac, Role
from iam.perms import UserPerm, UserRolePerm


def test_resource_wildcard_grants_only_its_resource_permissions():
    rbac = Rbac([{Role.ADMIN: {UserPerm.ALL.code}}])

    assert rbac.has_perm([Role.ADMIN], UserPerm.CREATE.code)
    assert not rbac.has_perm([Role.ADMIN], UserRolePerm.ASSIGN.code)


def test_iam_permissions_use_meaningful_action_codes():
    assert UserPerm.CREATE.code == "iam:user:create"
    assert UserPerm.CREATE_SUPERUSER.code == "iam:user:create_superuser"
    assert UserPerm.DEACTIVATE.code == "iam:user:deactivate"
    assert UserPerm.SOFT_DELETE.code == "iam:user:soft_delete"
    assert UserRolePerm.ASSIGN.code == "iam:user_role:assign"
    assert UserRolePerm.REMOVE.code == "iam:user_role:remove"
    assert UserRolePerm.VIEW.code == "iam:user_role:view"


def test_namespace_permission_check_uses_the_permission_code_prefix():
    rbac = Rbac([{Role.ADMIN: {UserPerm.ALL.code}}])

    assert rbac.has_namespace_perms([Role.ADMIN], "iam")
