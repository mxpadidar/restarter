import datetime
from typing import TypedDict, Unpack

import jwt


class JwtPayload(TypedDict):
    sub: str  # subject id
    jti: str  # token id
    iat: int  # issued at ts
    exp: int  # expiration ts


class JWTService:
    """Encode and validate access tokens using a fixed JWT algorithm."""

    ALG = "HS256"
    CLAIMS = ("iss", "aud", "sub", "jti", "iat", "exp")

    def __init__(
        self, *, secret: str, issuer: str, audience: str, leeway: datetime.timedelta
    ) -> None:
        """Configure access-token signing and validation.

        :param secret: Shared key used to sign and verify access tokens.
        :param issuer: Expected JWT issuer.
        :param audience: Expected JWT audience.
        :param leeway: Allowed clock skew when validating time-based claims.
        """
        self._secret = secret
        self._issuer = issuer
        self._audience = audience
        self._leeway = leeway

    def encode(self, **payload: Unpack[JwtPayload]) -> str:
        """Encode access-token claims into a signed JWT.

        :param payload: Typed application claims to include in the token.
        :return: Signed JWT string.
        :raises ValueError: If the supplied claims cannot form a valid payload.
        """
        try:
            return jwt.encode(
                {**payload, "iss": self._issuer, "aud": self._audience},
                self._secret,
                algorithm=self.ALG,
            )
        except (jwt.PyJWTError, KeyError) as exc:
            raise ValueError("could not encode access token") from exc

    def decode(self, token: str) -> JwtPayload:
        """Validate an access JWT and return its typed claims.

        Validation covers the signature, algorithm, issuer, audience, required
        claims, expiration, and application claim types.

        :param token: Encoded JWT supplied by a client.
        :return: Validated access-token payloads.
        :raises ValueError: If the JWT or any of its claims is invalid.
        """
        if not isinstance(token, str) or not token:
            raise ValueError("invalid or expired access token")

        try:
            payload = jwt.decode(
                token,
                self._secret,
                algorithms=[self.ALG],
                audience=self._audience,
                issuer=self._issuer,
                leeway=self._leeway,
                options={"require": list(self.CLAIMS)},
            )

            return {
                "sub": payload["sub"],
                "jti": payload["jti"],
                "iat": payload["iat"],
                "exp": payload["exp"],
            }
        except (jwt.PyJWTError, KeyError) as exc:
            raise ValueError("invalid or expired access token") from exc
