import os

from .base import *

DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1"]
PRODUCTION_DOMAIN = os.getenv("PRODUCTION_DOMAIN")
if PRODUCTION_DOMAIN:
    ALLOWED_HOSTS.append(PRODUCTION_DOMAIN)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_DB_PORT", "5432"),
        "OPTIONS": {"sslmode": "require", "channel_binding": "require"},
    }
}
