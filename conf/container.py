from dataclasses import dataclass
from functools import cache

from core.rbac import Rbac
from iam.rbac import ROLE_PERMS as IAM_RP
from iam.service_layer import RoleManager


@dataclass(frozen=True)
class Container:
    """Application service container."""

    rbac: Rbac
    role_manager: RoleManager


@cache
def get_container() -> Container:
    """Build and return the shared application service container."""
    return Container(
        rbac=Rbac([IAM_RP]),
        role_manager=RoleManager(),
    )
