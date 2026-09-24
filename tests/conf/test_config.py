from conf.config import Config


def test_config_loads_values_from_environment(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "prod")
    monkeypatch.setenv("APP_NAME", "test-app")
    monkeypatch.setenv("DJANGO_ALLOWED_HOSTS", '["example.com", "api.example.com"]')
    config = Config()

    assert config.environment == "prod"
    assert config.app_name == "test-app"
    assert config.django_allowed_hosts == ["example.com", "api.example.com"]
    assert config.debug is False
