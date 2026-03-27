"""
Security configuration and settings helpers.
"""
from typing import List, Dict, Any


class CORSConfiguration:
    """
    Secure CORS configuration.
    """

    @staticmethod
    def get_cors_allowed_origins() -> List[str]:
        """
        Get allowed CORS origins.

        Configure in environment:
            CORS_ALLOWED_ORIGINS=https://example.com,https://app.example.com
        """
        import os
        from decouple import config

        allowed = config(
            "CORS_ALLOWED_ORIGINS",
            default="http://localhost:3000,http://localhost:8080",
            cast=lambda x: [item.strip() for item in x.split(",")],
        )
        return allowed

    @staticmethod
    def get_cors_settings() -> Dict[str, Any]:
        """
        Get comprehensive CORS security settings.

        Returns:
            Dictionary of CORS configuration
        """
        return {
            "CORS_ALLOWED_ORIGINS": CORSConfiguration.get_cors_allowed_origins(),
            "CORS_ALLOW_CREDENTIALS": True,
            "CORS_ALLOW_HEADERS": [
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
            ],
            "CORS_EXPOSE_HEADERS": [
                "content-length",
                "content-type",
                "x-csrftoken",
                "x-ratelimit-limit",
                "x-ratelimit-remaining",
                "x-ratelimit-reset",
            ],
            "CORS_ALLOW_METHODS": [
                "DELETE",
                "GET",
                "OPTIONS",
                "PATCH",
                "POST",
                "PUT",
            ],
            "CORS_MAX_AGE": 86400,  # 24 hours
        }


class SecurityHeadersConfiguration:
    """
    Comprehensive security headers configuration.
    """

    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """
        Get security headers configuration.

        Returns:
            Dictionary of security headers
        """
        return {
            # Content Security Policy
            "CONTENT_SECURITY_POLICY": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self';"
            ),
            # MIME type sniffing protection
            "X_CONTENT_TYPE_OPTIONS": "nosniff",
            # Clickjacking protection
            "X_FRAME_OPTIONS": "DENY",
            # XSS protection
            "X_XSS_PROTECTION": "1; mode=block",
            # Referrer policy
            "REFERRER_POLICY": "strict-origin-when-cross-origin",
            # Permissions policy
            "PERMISSIONS_POLICY": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "accelerometer=()"
            ),
        }


class APISecurityConfiguration:
    """
    API-specific security configuration.
    """

    @staticmethod
    def get_api_security_settings() -> Dict[str, Any]:
        """
        Get API security configuration.

        Returns:
            Dictionary of API security settings
        """
        return {
            # Authentication
            "DEFAULT_AUTHENTICATION_CLASSES": [
                "rest_framework_simplejwt.authentication.JWTAuthentication",
            ],
            # Permissions - require authentication for all endpoints
            "DEFAULT_PERMISSION_CLASSES": [
                "rest_framework.permissions.IsAuthenticated",
            ],
            # Throttling - prevent abuse
            "DEFAULT_THROTTLE_CLASSES": [
                "apps.security.throttling.UserGeneralThrottle",
                "apps.security.throttling.AnonGeneralThrottle",
            ],
            "DEFAULT_THROTTLE_RATES": {
                "user_auth": "5/min",
                "user_general": "100/hour",
                "anon_general": "20/hour",
                "burst": "10/minute",
                "sustained": "1000/day",
            },
            # Pagination
            "DEFAULT_PAGINATION_CLASS": (
                "rest_framework.pagination.PageNumberPagination"
            ),
            "PAGE_SIZE": 50,
            # Filtering
            "DEFAULT_FILTER_BACKENDS": [
                "django_filters.rest_framework.DjangoFilterBackend",
                "rest_framework.filters.SearchFilter",
                "rest_framework.filters.OrderingFilter",
            ],
            # Rendering
            "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
            # Schema
            "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
        }


class EncodingConfiguration:
    """
    Character encoding and validation configuration.
    """

    @staticmethod
    def get_encoding_settings() -> Dict[str, Any]:
        """
        Get encoding security settings.

        Returns:
            Dictionary of encoding configuration
        """
        return {
            # File upload settings
            "FILE_UPLOAD_MAX_MEMORY_SIZE": 10 * 1024 * 1024,  # 10 MB
            "DATA_UPLOAD_MAX_MEMORY_SIZE": 10 * 1024 * 1024,  # 10 MB
            "FILE_UPLOAD_PERMISSIONS": 0o644,
            # JSON encoding
            "JSON_EDITOR_ENABLED": False,  # Disable in production
            # Form encoding
            "FORM_RENDERER_USE_HTML5_SEMANTIC_INPUT_TYPES": True,
        }


class PasswordSecurityConfiguration:
    """
    Password validation and policy configuration.
    """

    @staticmethod
    def get_password_validators() -> List[Dict[str, str]]:
        """
        Get password validation configuration.

        Returns:
            List of password validator configurations
        """
        return [
            {
                "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
            },
            {
                "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
                "OPTIONS": {"min_length": 12},  # Increased from default 8
            },
            {
                "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
            },
            {
                "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
            },
        ]


class CacheSecurityConfiguration:
    """
    Cache security configuration.
    """

    @staticmethod
    def get_cache_settings() -> Dict[str, Any]:
        """
        Get secure cache configuration.

        Returns:
            Dictionary of cache settings
        """
        return {
            "default": {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": "redis://localhost:6379/1",
                "OPTIONS": {
                    "CLIENT_CLASS": "django_redis.client.DefaultClient",
                    "CONNECTION_POOL_KWARGS": {"max_connections": 50},
                    "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
                },
                "KEY_PREFIX": "expense_tracker",
                "TIMEOUT": 3600,  # 1 hour default
            }
        }


class LoggingSecurityConfiguration:
    """
    Security-focused logging configuration.
    """

    @staticmethod
    def get_logging_config() -> Dict[str, Any]:
        """
        Get logging configuration with security focus.

        Logs:
        - Authentication failures
        - Authorization violations
        - Suspicious patterns
        - Rate limit violations

        Returns:
            Dictionary of logging configuration
        """
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "verbose": {
                    "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
                    "style": "{",
                },
                "security": {
                    "format": "{levelname} {asctime} {name} | {message}",
                    "style": "{",
                },
            },
            "handlers": {
                "console": {
                    "level": "DEBUG",
                    "class": "logging.StreamHandler",
                    "formatter": "verbose",
                },
                "security_file": {
                    "level": "WARNING",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "logs/security.log",
                    "maxBytes": 10485760,  # 10 MB
                    "backupCount": 10,
                    "formatter": "security",
                },
                "auth_file": {
                    "level": "INFO",
                    "class": "logging.handlers.RotatingFileHandler",
                    "filename": "logs/auth.log",
                    "maxBytes": 10485760,  # 10 MB
                    "backupCount": 5,
                    "formatter": "security",
                },
            },
            "loggers": {
                "django": {
                    "handlers": ["console"],
                    "level": "INFO",
                    "propagate": True,
                },
                "django.security": {
                    "handlers": ["security_file"],
                    "level": "WARNING",
                    "propagate": False,
                },
                "apps.security": {
                    "handlers": ["security_file"],
                    "level": "DEBUG",
                    "propagate": False,
                },
                "apps.authentication": {
                    "handlers": ["auth_file"],
                    "level": "INFO",
                    "propagate": False,
                },
            },
        }
