from django.db import transaction
from django.utils.translation import gettext as _

from account.commands import RotateRefreshTokenCommand
from account.dtos import TokenPair
from account.models import SessionGrant
from account.services import JWTService, RoleManager
from core.errors import AuthenticationError
from core.services import HMACSHA256Hasher
from core.utils import datetime_to_timestamp, generate_urlsafe_token, get_current_datetime


@transaction.atomic
def handle_rotate_refresh_token_command(
    cmd: RotateRefreshTokenCommand,
    hasher: HMACSHA256Hasher,
    jwt_service: JWTService,
    role_manager: RoleManager,
) -> TokenPair:
    """Rotate a refresh token and issue a new access/refresh token pair."""

    now = get_current_datetime()

    try:
        grant_id, refresh_secret = TokenPair.parse_refresh_token(cmd.refresh_token)
    except ValueError as exc:
        raise AuthenticationError(_("invalid or expired refresh token")) from exc

    grant = (
        SessionGrant.objects.select_for_update()
        .select_related("user")
        .filter(id=grant_id)
        .filter(revoked_at__isnull=True)
        .filter(expires_at__gt=now)
        .first()
    )

    if grant is None:
        raise AuthenticationError(_("invalid or expired refresh token"))

    if not hasher.verify(plain_text=refresh_secret, expected_hash=grant.secret_hash):
        raise AuthenticationError(_("invalid or expired refresh token"))

    if not grant.user.is_active:
        raise AuthenticationError(_("invalid or expired refresh token"))

    try:
        grant.revoke()
    except ValueError as exc:
        raise AuthenticationError(_("invalid or expired refresh token")) from exc

    new_refresh_secret = generate_urlsafe_token(size=cmd.refresh_token_size)

    new_grant = SessionGrant.objects.create(
        user=grant.user,
        session_id=grant.session_id,
        secret_hash=hasher.hash(new_refresh_secret),
        ip_address=cmd.ip_address,
        issued_at=now,
        expires_at=now + cmd.refresh_token_ttl,
    )

    access_exp = now + cmd.access_token_ttl
    roles = sorted(role.value for role in role_manager.get_roles(grant.user))

    return TokenPair.create(
        access_token=jwt_service.encode(
            sub=grant.user.id.hex,
            jti=new_grant.id.hex,
            roles=roles,
            iat=datetime_to_timestamp(now),
            exp=datetime_to_timestamp(access_exp),
        ),
        refresh_secret=new_refresh_secret,
        grant_id=new_grant.id,
        access_expires_at=access_exp,
    )
