from .base import *  # noqa

DEBUG = True

SECRET_KEY = SECRET_KEY or "dev-secret-key"

ALLOWED_HOSTS = ALLOWED_HOSTS or ["localhost", "127.0.0.1"]
