from core.rbac import Perm, Role


class UserPerm(Perm, resource="user", namespace="account"):
    ALL = "*"
    CREATE = "create"
    DEACTIVATE = "deactivate"
    READ = "read"


class UserRolePerm(Perm, resource="user_role", namespace="account"):
    ALL = "*"
    ASSIGN = "assign"
    REMOVE = "remove"
    READ = "read"


ACCOUNT_PERMS: dict[Role, set[str]] = {
    Role.ADMIN: {UserPerm.ALL.code, UserRolePerm.ALL.code},
    Role.NORMAL: set(),
}
