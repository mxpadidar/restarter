import pytest

from conf.config import Config, get_config
from conf.container import Container, get_container


@pytest.fixture(scope="session")
def container() -> Container:
    """Fixture to provide the application container."""
    return get_container()


@pytest.fixture(scope="session")
def config() -> Config:
    """Fixture to provide the application configuration."""
    return get_config()
