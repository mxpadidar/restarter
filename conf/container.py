from dataclasses import dataclass
from functools import cache

from iam.service_layer import RoleManager


@dataclass(frozen=True)
class Container:
    """Application service container."""

    role_manager: RoleManager


@cache
def get_container() -> Container:
    """Build and return the shared application service container."""
    return Container(
        role_manager=RoleManager(),
    )
