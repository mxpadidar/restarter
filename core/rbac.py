from collections import defaultdict
from collections.abc import Iterable
from enum import Enum, nonmember
from fnmatch import fnmatchcase


class Role(Enum):
    """Application role used to group permissions."""

    ADMIN = "admin"
    NORMAL = "normal"  # non-admin users


class Namespace(Enum):
    """Top-level namespace shared by related RBAC resources and permissions."""

    IAM = "iam"


class Resource(Enum):
    """Base class for application resources protected by permissions."""

    # Set on each Resource subclass through the required ``namespace`` keyword.
    _namespace = nonmember(None)

    def __init_subclass__(cls, *, namespace: Namespace, **kwargs) -> None:
        """Bind a resource enum to the namespace that owns it.

        :param namespace: Top-level namespace that owns the resource.
        """
        super().__init_subclass__(**kwargs)
        cls._namespace = namespace

    @property
    def namespace(self) -> Namespace:
        """Return the top-level namespace that owns this resource."""
        assert isinstance(self._namespace, Namespace)
        return self._namespace


class Perm(Enum):
    """Base class for permissions associated with protected resources."""

    # Set on each permission enum through the required ``resource`` keyword.
    _resource = nonmember(None)

    def __init_subclass__(cls, *, resource: Resource, **kwargs) -> None:
        """Bind a permission enum to the resource it protects.

        :param resource: Resource protected by the permissions in the enum.
        """
        super().__init_subclass__(**kwargs)
        cls._resource = resource

    @property
    def resource(self) -> Resource:
        """Return the resource protected by this permission."""
        assert isinstance(self._resource, Resource)
        return self._resource

    @property
    def namespace(self) -> Namespace:
        """Return the top-level namespace that owns this permission."""
        return self.resource.namespace

    @property
    def code(self) -> str:
        """Return the ``namespace:resource:action`` authorization code."""
        return f"{self.namespace.value}:{self.resource.value}:{self.value}"


# Mapping from each role to the permissions granted to that role.
type RolePermMap = dict[Role, set[str]]


class Rbac:
    """Resolve permissions granted to one or more application roles.

    The RBAC policy is built from role-permission mappings contributed by
    different application modules. Permissions assigned to the same role are
    merged into a single immutable permission set.
    """

    def __init__(self, role_perms: Iterable[RolePermMap]) -> None:
        """Build the RBAC policy from role-permission mappings.

        :param role_perms: Role-permission mappings contributed by application namespaces.
        """
        combined: defaultdict[Role, set[str]] = defaultdict(set)

        for app_role_perms in role_perms:
            for role, perms in app_role_perms.items():
                combined[role].update(perms)

        self.ROLE_PERMISSIONS: dict[Role, frozenset[str]] = {
            role: frozenset(perms) for role, perms in combined.items()
        }

    def get_role_permissions(self, role: Role) -> frozenset[str]:
        """Return all permission codes granted to a role.

        :param role: Role whose permissions should be resolved.
        :return: Permissions granted to the role, or an empty set if none are assigned.
        """
        return self.ROLE_PERMISSIONS.get(role, frozenset())

    def get_roles_permissions(self, roles: Iterable[Role]) -> frozenset[str]:
        """Return the combined permission codes granted to multiple roles.

        :param roles: Roles whose permissions should be combined.
        :return: Union of all permissions granted to the provided roles.
        """
        permissions: set[str] = set()

        for role in roles:
            permissions.update(self.get_role_permissions(role))

        return frozenset(permissions)

    def get_all_permissions(self) -> frozenset[str]:
        """Return every permission grant known to the RBAC policy.

        This is used for superusers, whose effective permissions are not
        limited to the roles assigned to them.

        :return: All exact permission codes and wildcard grants from every role.
        """
        return frozenset(
            permission
            for permissions in self.ROLE_PERMISSIONS.values()
            for permission in permissions
        )

    def has_perm(self, roles: Iterable[Role], perm: str) -> bool:
        """Check whether any of the provided roles grants a permission code.

        :param roles: Roles to evaluate.
        :param perm: Permission code to check.
        :return: ``True`` if the permission is granted, otherwise ``False``.
        """
        return any(
            fnmatchcase(perm, granted_permission)
            for granted_permission in self.get_roles_permissions(roles)
        )

    def has_namespace_perms(self, roles: Iterable[Role], namespace: Namespace) -> bool:
        """Check whether any provided role grants a permission in a namespace.

        :param roles: Roles to evaluate.
        :param namespace: Top-level namespace to check.
        :return: ``True`` if any granted permission belongs to the namespace,
            otherwise ``False``.
        """
        # Permission codes begin with ``<namespace>:`` as defined by ``Perm.code``.
        namespace_prefix = f"{namespace.value}:"
        return any(
            permission.startswith(namespace_prefix)
            for permission in self.get_roles_permissions(roles)
        )
