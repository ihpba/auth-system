"""
Настройки Django-проекта «Система аутентификации и авторизации».

Все чувствительные параметры загружаются из .env через python-dotenv.
"""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-default-key")

DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1,testserver").split(",")

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "rest_framework",
    "drf_spectacular",
    "accounts",
    "rbac",
    "business",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "accounts.middleware.JWTAuthenticationMiddleware",
]

ROOT_URLCONF = "config.urls"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "accounts.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "accounts.exceptions.custom_exception_handler",
    "UNAUTHENTICATED_USER": "accounts.middleware.AnonymousUser",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Система аутентификации и авторизации",
    "DESCRIPTION": "API собственной системы аутентификации и RBAC-авторизации",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "auth_system"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "postgres"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ── JWT-параметры ───────────────────────────────────────────────
JWT_ACCESS_LIFETIME = timedelta(
    minutes=int(os.getenv("JWT_ACCESS_LIFETIME_MINUTES", "15"))
)
JWT_REFRESH_LIFETIME = timedelta(
    days=int(os.getenv("JWT_REFRESH_LIFETIME_DAYS", "7"))
)

# Используем тот же SECRET_KEY для подписи JWT
JWT_SECRET_KEY = SECRET_KEY
JWT_ALGORITHM = "HS256"

# ── Безопасность (production) ───────────────────────────────────
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# ── Логирование ──────────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "accounts": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "rbac": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
