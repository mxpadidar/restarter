from django.db import transaction
from django.utils.translation import gettext as _

from account.commands import LogoutCommand
from account.dtos import TokenPair
from account.models import SessionGrant
from core.errors import AuthenticationError
from core.services import HMACSHA256Hasher
from core.utils import get_current_datetime


@transaction.atomic
def handle_logout_command(cmd: LogoutCommand, hasher: HMACSHA256Hasher) -> None:
    """Revoke the active session grant identified by a refresh token."""
    now = get_current_datetime()

    try:
        grant_id, refresh_secret = TokenPair.parse_refresh_token(cmd.refresh_token)
    except ValueError as exc:
        raise AuthenticationError(_("invalid or expired refresh token")) from exc

    grant = (
        SessionGrant.objects.select_for_update()
        .filter(id=grant_id)
        .filter(revoked_at__isnull=True)
        .filter(expires_at__gt=now)
        .first()
    )
    if grant is None:
        raise AuthenticationError(_("invalid or expired refresh token"))

    if not hasher.verify(plain_text=refresh_secret, expected_hash=grant.secret_hash):
        raise AuthenticationError(_("invalid or expired refresh token"))

    try:
        grant.revoke()
    except ValueError as exc:
        raise AuthenticationError(_("invalid or expired refresh token")) from exc
