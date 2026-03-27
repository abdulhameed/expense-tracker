from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# Console email — printed to terminal
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Local filesystem storage
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# Allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True

# Nicer error pages / shell extras (optional)
try:
    import django_extensions  # noqa: F401
    INSTALLED_APPS += ["django_extensions"]  # noqa: F405
except ImportError:
    pass  # django_extensions not installed

# --- LOCAL DEVELOPMENT DATABASE ---
# Use SQLite for local development (no PostgreSQL needed)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# --- LOCAL DEVELOPMENT CACHE ---
# Use local memory cache (no Redis needed)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "expense-tracker-cache",
    }
}

# --- LOCAL DEVELOPMENT CELERY ---
# Use eager task execution (tasks run synchronously)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"

# --- API DOCUMENTATION ---
# Allow unauthenticated access to Swagger UI in development
SPECTACULAR_SETTINGS.update({  # noqa: F405
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
})

# --- RATE LIMITING ---
# Disable rate limiting in development for easier testing
# Note: We override specific throttle settings while keeping auth intact
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []  # noqa: F405
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {}  # noqa: F405

