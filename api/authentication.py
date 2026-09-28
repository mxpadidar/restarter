from uuid import UUID

from django.utils.translation import gettext as _
from rest_framework import authentication, exceptions

from conf.container import get_container
from core.rbac import Role
from iam.dtos import AuthUser
from iam.services.jwt_service import JwtPayload


class JWTAuthentication(authentication.TokenAuthentication):
    """Authenticate API requests from signed Bearer access tokens."""

    keyword = "Bearer"

    def authenticate_credentials(self, key: str) -> tuple[AuthUser, JwtPayload]:
        """Authenticate the given access token and return the associated user and payload."""
        try:
            payload = get_container().jwt_service.decode(key)
            auth_user = AuthUser(
                user_id=UUID(hex=payload["sub"]),
                session_grant_id=UUID(hex=payload["jti"]),
                roles={Role(role) for role in payload["roles"]},
            )
        except (TypeError, ValueError) as exc:
            raise exceptions.AuthenticationFailed(_("invalid or expired access token")) from exc

        return auth_user, payload
