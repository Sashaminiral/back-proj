"""Настройки для автотестов на SQLite в памяти."""

from config.settings import *  # noqa: F403, F401

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
