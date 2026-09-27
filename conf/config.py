from datetime import timedelta
from functools import cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Config(BaseSettings):
    """Typed application configuration loaded from environment variables."""

    base_dir: Path = BASE_DIR
    environment: Literal["dev", "prod"] = "dev"
    app_name: str = "app-name"
    app_version: str = "0.1.0"
    django_secret: str = "change-me"
    django_allowed_hosts: list[str] = []
    log_level: str = "INFO"
    hmac_secret: str = "change-me"
    jwt_secret: str = "insecure-development-jwt-secret-replace-me"
    jwt_issuer: str = "drf-starter"
    jwt_audience: str = "drf-starter-api"
    jwt_leeway_seconds: int = 30
    access_token_ttl_seconds: int = 15 * 60
    refresh_token_ttl_seconds: int = 30 * 24 * 60 * 60
    refresh_token_size: int = 32

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        frozen=True,
    )

    @property
    def debug(self) -> bool:
        """Return True if the application is running in development mode."""
        return self.environment == "dev"

    @property
    def hmac_key(self) -> bytes:
        """Return the configured HMAC secret as bytes."""
        return self.hmac_secret.encode("utf-8")

    @property
    def jwt_leeway(self) -> timedelta:
        """Return the JWT validation leeway as a duration."""
        return timedelta(seconds=self.jwt_leeway_seconds)

    @property
    def access_token_ttl(self) -> timedelta:
        """Return the access-token lifetime as a duration."""
        return timedelta(seconds=self.access_token_ttl_seconds)

    @property
    def refresh_token_ttl(self) -> timedelta:
        """Return the refresh-token lifetime as a duration."""
        return timedelta(seconds=self.refresh_token_ttl_seconds)


@cache
def get_config() -> Config:
    """Build and cache the process-wide application configuration."""
    return Config()
