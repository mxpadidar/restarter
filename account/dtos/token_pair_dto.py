import dataclasses
import datetime
import uuid
from typing import Self


@dataclasses.dataclass(frozen=True, slots=True)
class TokenPair:
    """Represent an access token and its associated refresh token."""

    access_token: str
    refresh_token: str
    expires_at: datetime.datetime

    @classmethod
    def create(
        cls,
        access_token: str,
        refresh_secret: str,
        grant_id: uuid.UUID,
        access_expires_at: datetime.datetime,
    ) -> Self:
        """Create a token pair from an access token and refresh grant.

        The refresh token is composed of the grant ID and refresh secret
        using the format ``<grant_id>:<secret>``.

        :param access_token: The encoded access token.
        :param refresh_secret: The opaque secret associated with the grant.
        :param grant_id: The UUID identifying the session grant.
        :param access_expires_at: The expiration datetime of the access token.
        :return: A new token pair.
        """
        return cls(
            access_token=access_token,
            refresh_token=f"{grant_id.hex}:{refresh_secret}",
            expires_at=access_expires_at,
        )

    @staticmethod
    def parse_refresh_token(refresh_token: str) -> tuple[uuid.UUID, str]:
        """Parse a refresh token into its grant ID and secret.

        The refresh token must use the format ``<grant_id>:<secret>``.

        :param refresh_token: The refresh token to parse.
        :return: A tuple containing the grant UUID and refresh secret.
        :raises ValueError: If the refresh token has an invalid format.
        """
        if not isinstance(refresh_token, str):
            raise ValueError("invalid refresh token format")  # noqa: TRY004

        grant_id, separator, refresh_secret = refresh_token.partition(":")
        if not separator or not grant_id or not refresh_secret:
            raise ValueError("invalid refresh token format")

        try:
            grant_uuid = uuid.UUID(hex=grant_id)
        except ValueError as exc:
            raise ValueError("invalid refresh token format") from exc

        return grant_uuid, refresh_secret
