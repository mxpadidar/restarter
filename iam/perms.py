from core.rbac import Perm, Role


class UserPerm(Perm, resource="user", namespace="iam"):
    ALL = "*"
    CREATE = "create"
    CREATE_SUPERUSER = "create_superuser"
    DEACTIVATE = "deactivate"
    SOFT_DELETE = "soft_delete"
    VIEW = "view"


class UserRolePerm(Perm, resource="user_role", namespace="iam"):
    ALL = "*"
    ASSIGN = "assign"
    REMOVE = "remove"
    VIEW = "view"


IAM_PERMS: dict[Role, set[str]] = {
    Role.ADMIN: {UserPerm.ALL.code, UserRolePerm.ALL.code},
    Role.NORMAL: set(),
}
