import pytest

from conf.container import Container, get_container


@pytest.fixture(scope="session")
def container() -> Container:
    """Fixture to provide the application container."""
    return get_container()
