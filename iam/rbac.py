from core.rbac import Namespace, Perm, Resource, Role


class IamResource(Resource, namespace=Namespace.IAM):
    USER = "user"
    USER_ROLE = "user_role"


class UserPerm(Perm, resource=IamResource.USER):
    ALL = "*"
    CREATE = "create"
    CREATE_SUPERUSER = "create_superuser"
    DEACTIVATE = "deactivate"
    SOFT_DELETE = "soft_delete"
    VIEW = "view"


class UserRolePerm(Perm, resource=IamResource.USER_ROLE):
    ALL = "*"
    ASSIGN = "assign"
    REMOVE = "remove"
    VIEW = "view"


ROLE_PERMS: dict[Role, set[str]] = {
    # Resource-scoped wildcards automatically include future actions for each resource.
    Role.ADMIN: {UserPerm.ALL.code, UserRolePerm.ALL.code},
    Role.NORMAL: set(),
}
