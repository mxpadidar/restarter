from dataclasses import dataclass
from functools import cache

from conf.config import get_config
from core.rbac import Rbac
from core.services import HMACSHA256Hasher
from iam.rbac import ROLE_PERMS as IAM_RP
from iam.services import RoleManager


@dataclass(frozen=True)
class Container:
    """Application service container."""

    rbac: Rbac
    role_manager: RoleManager
    hmac_hasher: HMACSHA256Hasher


@cache
def get_container() -> Container:
    """Build and return the shared application service container."""
    config = get_config()

    return Container(
        rbac=Rbac([IAM_RP]),
        role_manager=RoleManager(),
        hmac_hasher=HMACSHA256Hasher(key=config.hmac_key),
    )
