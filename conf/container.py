from dataclasses import dataclass
from functools import cache

from account.perms import ACCOUNT_PERMS
from account.services import JWTService, RoleManager
from conf.config import get_config
from core.rbac import Rbac
from core.services import HMACSHA256Hasher


@dataclass(frozen=True)
class Container:
    """Application service container."""

    rbac: Rbac
    role_manager: RoleManager
    hmac_hasher: HMACSHA256Hasher
    jwt_service: JWTService


@cache
def get_container() -> Container:
    """Build and return the shared application service container."""
    config = get_config()

    return Container(
        rbac=Rbac([ACCOUNT_PERMS]),
        role_manager=RoleManager(),
        hmac_hasher=HMACSHA256Hasher(key=config.hmac_key),
        jwt_service=JWTService(
            secret=config.jwt_secret,
            issuer=config.jwt_issuer,
            audience=config.jwt_audience,
            leeway=config.jwt_leeway,
        ),
    )
