from .base import *  # noqa

DEBUG = False

if not SECRET_KEY or SECRET_KEY == "dev-secret-key":
    raise RuntimeError("SECRET_KEY must be set in production.")

if not ALLOWED_HOSTS:
    raise RuntimeError("ALLOWED_HOSTS must be configured in production.")

SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
