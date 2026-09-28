from account.services import RoleManager
from conf.container import Container, get_container


def test_get_container_builds_application_services():
    get_container.cache_clear()

    container = get_container()

    assert isinstance(container, Container)
    assert isinstance(container.role_manager, RoleManager)


def test_get_container_returns_the_cached_instance():
    get_container.cache_clear()

    assert get_container() is get_container()
