from .config import get_config
from .logging import setup_logging

config = get_config()

SECRET_KEY = config.django_secret
DEBUG = config.debug
ALLOWED_HOSTS = config.django_allowed_hosts

setup_logging(
    log_dir=config.base_dir / "logs",
    level=config.log_level,
    diagnose=config.debug,
)

LOGGING_CONFIG = None

TIME_ZONE = "UTC"

USE_TZ = True

LANGUAGE_CODE = "en-us"

USE_I18N = True

STATIC_URL = "static/"

ROOT_URLCONF = "conf.urls"

WSGI_APPLICATION = "conf.wsgi.application"


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # -------- third-party --------
    "rest_framework",
    "drf_spectacular",
    # -------- local --------
    "iam",
]

MIDDLEWARE = [
    "api.middlewares.RequestIDMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "api.middlewares.RequestLoggingMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": config.base_dir / "db.sqlite3",
    }
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "api.error_handlers.api_error_handler",
}

SPECTACULAR_SETTINGS = {"TITLE": config.app_name, "VERSION": config.app_version}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}
