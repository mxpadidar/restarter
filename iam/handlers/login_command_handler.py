import uuid

from django.db import transaction
from django.utils.translation import gettext as _

from core.errors import AuthenticationError
from core.services import HMACSHA256Hasher
from core.utils import datetime_to_timestamp, generate_urlsafe_token, get_current_datetime
from iam.commands import LoginCommand
from iam.dtos import TokenPair
from iam.models import SessionGrant, User
from iam.services import JWTService


@transaction.atomic
def handle_login_command(
    cmd: LoginCommand, hasher: HMACSHA256Hasher, jwt_service: JWTService
) -> TokenPair:
    """Authenticate a user and create an access/refresh token pair."""
    username = cmd.username.strip().lower()
    user = User.objects.filter(username=username).first()
    if user is None:
        User().set_password(cmd.password)
        raise AuthenticationError(_("invalid username or password"))

    if (
        user.deleted_at is not None
        or user.deactivated_at is not None
        or not user.check_password(cmd.password)
    ):
        raise AuthenticationError(_("invalid username or password"))

    issued_at = get_current_datetime()
    secret = generate_urlsafe_token(cmd.refresh_token_size)

    grant = SessionGrant.objects.create(
        user=user,
        session_id=uuid.uuid4(),
        secret_hash=hasher.hash(secret),
        ip_address=cmd.ip_address,
        issued_at=issued_at,
        expires_at=issued_at + cmd.refresh_token_ttl,
    )

    access_exp = issued_at + cmd.access_token_ttl

    return TokenPair.create(
        access_token=jwt_service.encode(
            sub=user.id.hex,
            jti=grant.id.hex,
            iat=datetime_to_timestamp(issued_at),
            exp=datetime_to_timestamp(access_exp),
        ),
        refresh_secret=secret,
        grant_id=grant.id,
        access_expires_at=access_exp,
    )
