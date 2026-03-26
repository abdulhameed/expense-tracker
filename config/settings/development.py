from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Console email — printed to terminal
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Local filesystem storage
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Nicer error pages / shell extras
INSTALLED_APPS += ["django_extensions"]  # noqa: F405
