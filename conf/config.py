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

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        frozen=True,
    )

    @property
    def debug(self) -> bool:
        """Return True if the application is running in development mode."""
        return self.environment == "dev"


@cache
def get_config() -> Config:
    """Build and cache the process-wide application configuration."""
    return Config()
