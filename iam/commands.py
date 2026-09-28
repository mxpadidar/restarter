import dataclasses
from datetime import timedelta


@dataclasses.dataclass(frozen=True)
class SignupCommand:
    username: str
    password: str


@dataclasses.dataclass(frozen=True)
class LoginCommand:
    username: str
    password: str
    access_token_ttl: timedelta
    refresh_token_ttl: timedelta
    refresh_token_size: int
    ip_address: str | None = None


@dataclasses.dataclass(frozen=True)
class LogoutCommand:
    refresh_token: str


@dataclasses.dataclass(frozen=True)
class RotateRefreshTokenCommand:
    refresh_token: str
    access_token_ttl: timedelta
    refresh_token_ttl: timedelta
    refresh_token_size: int
    ip_address: str | None = None
