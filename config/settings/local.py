"""
Central Contexto 2.0 - Local / development settings.
"""

from decouple import config

from .base import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------
DEBUG = True

ALLOWED_HOSTS = ["*"]

# ---------------------------------------------------------------------------
# Database  --  SQLite fallback when DB_NAME is not set or PostgreSQL is
# unavailable. Set USE_SQLITE=True in .env to force SQLite.
# ---------------------------------------------------------------------------
_use_sqlite = config("USE_SQLITE", default="False", cast=bool)
if _use_sqlite or not config("DB_NAME", default=""):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }

# ---------------------------------------------------------------------------
# Email  --  console backend for development
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ---------------------------------------------------------------------------
# Cache  --  local memory in dev when Redis is unavailable
# ---------------------------------------------------------------------------
if not config("REDIS_URL", default=""):
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }

# ---------------------------------------------------------------------------
# Django Debug Toolbar (optional)
# ---------------------------------------------------------------------------
try:
    import debug_toolbar  # noqa: F401

    INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
    INTERNAL_IPS = ["127.0.0.1", "localhost"]
except ImportError:
    pass

# ---------------------------------------------------------------------------
# WhiteNoise  --  use plain storage in development
# ---------------------------------------------------------------------------
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# ---------------------------------------------------------------------------
# CORS  --  allow all in development
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True
