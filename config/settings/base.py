from datetime import timedelta
from pathlib import Path

from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "corsheaders",
    "django_filters",
    "django_celery_beat",
]

LOCAL_APPS = [
    "apps.authentication",
    "apps.projects",
    "apps.transactions",
    "apps.documents",
    "apps.budgets",
    "apps.reports",
    "apps.activity",
    "apps.security",
    "apps.health",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.security.middleware.SecurityHeadersMiddleware",
    "apps.security.middleware.RateLimitHeadersMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="expense_tracker"),
        "USER": config("DB_USER", default="expense_user"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        # Connection pooling for production
        "CONN_MAX_AGE": 600,  # Close connections after 10 minutes
        "ATOMIC_REQUESTS": False,
        # Options for better performance
        "OPTIONS": {
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000",  # 30 second query timeout
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "authentication.User"

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- DRF ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    # Rate limiting and throttling
    "DEFAULT_THROTTLE_CLASSES": (
        "apps.security.throttling.UserGeneralThrottle",
        "apps.security.throttling.AnonGeneralThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {
        "user_auth": "5/min",
        "user_general": "100/hour",
        "anon_general": "20/hour",
        "burst": "10/minute",
        "sustained": "1000/day",
    },
}

# --- drf-spectacular ---
SPECTACULAR_SETTINGS = {
    "TITLE": "Expense Tracker API",
    "DESCRIPTION": "A comprehensive expense tracking system with project management, budgets, reports, and team collaboration.",
    "VERSION": "1.0.0",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAuthenticated"],
    "AUTHENTICATION_WHITELIST": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "SCHEMA_PATH_PREFIX": "/api/v1",
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorizationData": True,
        "displayOperationId": True,
    },
    "CONTACT": {
        "name": "API Support",
        "email": "support@expensetracker.com",
    },
    "LICENSE": {
        "name": "MIT",
    },
    "SERVERS": [
        {
            "url": "http://localhost:8000",
            "description": "Development server",
        },
        {
            "url": "https://api.expensetracker.com",
            "description": "Production server",
        },
    ],
    "COMPONENTS": {
        "securitySchemes": {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
                "description": "JWT token authentication",
            }
        }
    },
    "SECURITY": [{"Bearer": []}],
}

# --- JWT ---
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# --- Celery ---
CELERY_BROKER_URL = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = config("REDIS_URL", default="redis://localhost:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# Celery Beat schedule for periodic tasks
from celery.schedules import crontab  # noqa: E402

CELERY_BEAT_SCHEDULE = {
    "check-budget-alerts": {
        "task": "apps.budgets.tasks.check_budget_alerts",
        "schedule": crontab(hour=9, minute=0),  # Run daily at 9:00 AM UTC
    },
}

# --- Cache ---
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://localhost:6379/1"),
    }
}

DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@expensetracker.com")

# --- Logging ---
# Production overrides this with a rotating file handler (see production.py).
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# --- File uploads ---
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB

ALLOWED_DOCUMENT_TYPES = [
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/csv",
]

# --- Security Configuration ---
# CORS Settings
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:3000,http://localhost:8080",
    cast=lambda x: [item.strip() for item in x.split(",")],
)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
    "x-api-key",
]

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'",),
    "style-src": ("'self'", "'unsafe-inline'"),
    "img-src": ("'self'", "data:", "https:"),
    "font-src": ("'self'", "data:"),
    "connect-src": ("'self'", "https:"),
    "frame-ancestors": ("'none'",),
    "base-uri": ("'self'",),
    "form-action": ("'self'",),
}

# Session Security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Strict"
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# CSRF Protection
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Strict"

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Brute force protection
FAILED_LOGIN_ATTEMPTS_LIMIT = 5
FAILED_LOGIN_LOCKOUT_DURATION = 15 * 60  # 15 minutes
