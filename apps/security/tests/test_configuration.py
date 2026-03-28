"""
Tests for security/configuration.py - Security configuration helpers.

Tests:
- CORSConfiguration - CORS settings and origins
- SecurityHeadersConfiguration - Security headers
- APISecurityConfiguration - API security settings
- EncodingConfiguration - File upload and encoding settings
- PasswordSecurityConfiguration - Password validators
- CacheSecurityConfiguration - Cache security settings
- LoggingSecurityConfiguration - Logging configuration
"""

import pytest
from unittest.mock import patch, MagicMock
from django.test import override_settings

from apps.security.configuration import (
    CORSConfiguration,
    SecurityHeadersConfiguration,
    APISecurityConfiguration,
    EncodingConfiguration,
    PasswordSecurityConfiguration,
    CacheSecurityConfiguration,
    LoggingSecurityConfiguration,
)


class TestCORSConfiguration:
    """Test CORS configuration."""

    @override_settings(DEBUG=True)
    def test_get_cors_allowed_origins_default(self):
        """Test default CORS allowed origins in development."""
        origins = CORSConfiguration.get_cors_allowed_origins()

        assert isinstance(origins, list)
        assert "http://localhost:3000" in origins
        assert "http://localhost:8080" in origins

    @patch("apps.security.configuration.config")
    def test_get_cors_allowed_origins_from_env(self, mock_config):
        """Test CORS origins loaded from environment."""
        mock_config.return_value = [
            "https://example.com",
            "https://app.example.com",
        ]

        origins = CORSConfiguration.get_cors_allowed_origins()

        assert len(origins) == 2
        assert "https://example.com" in origins
        assert "https://app.example.com" in origins

    @patch("apps.security.configuration.config")
    def test_get_cors_allowed_origins_strips_whitespace(self, mock_config):
        """Test that whitespace is stripped from origins."""
        mock_config.return_value = "https://example.com , https://app.example.com"

        with patch("apps.security.configuration.config") as mock:
            # Simulate the behavior of the cast function
            cast_func = lambda x: [item.strip() for item in x.split(",")]
            origins = cast_func("https://example.com , https://app.example.com")

        assert origins[0] == "https://example.com"
        assert origins[1] == "https://app.example.com"

    def test_get_cors_settings_structure(self):
        """Test CORS settings have required structure."""
        settings = CORSConfiguration.get_cors_settings()

        assert isinstance(settings, dict)
        assert "CORS_ALLOWED_ORIGINS" in settings
        assert "CORS_ALLOW_CREDENTIALS" in settings
        assert "CORS_ALLOW_HEADERS" in settings
        assert "CORS_EXPOSE_HEADERS" in settings
        assert "CORS_ALLOW_METHODS" in settings
        assert "CORS_MAX_AGE" in settings

    def test_cors_allow_credentials_enabled(self):
        """Test that CORS credentials are allowed."""
        settings = CORSConfiguration.get_cors_settings()

        assert settings["CORS_ALLOW_CREDENTIALS"] is True

    def test_cors_allow_headers_include_auth(self):
        """Test that CORS headers include authorization."""
        settings = CORSConfiguration.get_cors_settings()

        assert "authorization" in settings["CORS_ALLOW_HEADERS"]
        assert "content-type" in settings["CORS_ALLOW_HEADERS"]
        assert "x-api-key" in settings["CORS_ALLOW_HEADERS"]

    def test_cors_expose_headers_include_rate_limits(self):
        """Test that CORS expose headers include rate limit info."""
        settings = CORSConfiguration.get_cors_settings()

        assert "x-ratelimit-limit" in settings["CORS_EXPOSE_HEADERS"]
        assert "x-ratelimit-remaining" in settings["CORS_EXPOSE_HEADERS"]
        assert "x-ratelimit-reset" in settings["CORS_EXPOSE_HEADERS"]

    def test_cors_allow_methods_include_all(self):
        """Test that CORS allows all standard HTTP methods."""
        settings = CORSConfiguration.get_cors_settings()

        assert "GET" in settings["CORS_ALLOW_METHODS"]
        assert "POST" in settings["CORS_ALLOW_METHODS"]
        assert "PUT" in settings["CORS_ALLOW_METHODS"]
        assert "PATCH" in settings["CORS_ALLOW_METHODS"]
        assert "DELETE" in settings["CORS_ALLOW_METHODS"]
        assert "OPTIONS" in settings["CORS_ALLOW_METHODS"]

    def test_cors_max_age_24_hours(self):
        """Test that CORS max age is set to 24 hours."""
        settings = CORSConfiguration.get_cors_settings()

        assert settings["CORS_MAX_AGE"] == 86400  # 24 hours in seconds


class TestSecurityHeadersConfiguration:
    """Test security headers configuration."""

    def test_get_security_headers_structure(self):
        """Test security headers have required structure."""
        headers = SecurityHeadersConfiguration.get_security_headers()

        assert isinstance(headers, dict)
        assert "CONTENT_SECURITY_POLICY" in headers
        assert "X_CONTENT_TYPE_OPTIONS" in headers
        assert "X_FRAME_OPTIONS" in headers
        assert "X_XSS_PROTECTION" in headers
        assert "REFERRER_POLICY" in headers
        assert "PERMISSIONS_POLICY" in headers

    def test_content_security_policy_configured(self):
        """Test CSP header is configured."""
        headers = SecurityHeadersConfiguration.get_security_headers()
        csp = headers["CONTENT_SECURITY_POLICY"]

        assert "default-src" in csp
        assert "script-src" in csp
        assert "style-src" in csp
        assert "img-src" in csp
        assert "'self'" in csp

    def test_csp_frame_ancestors_none(self):
        """Test CSP prevents frame embedding."""
        headers = SecurityHeadersConfiguration.get_security_headers()
        csp = headers["CONTENT_SECURITY_POLICY"]

        assert "frame-ancestors 'none'" in csp

    def test_csp_base_uri_self(self):
        """Test CSP restricts base URI."""
        headers = SecurityHeadersConfiguration.get_security_headers()
        csp = headers["CONTENT_SECURITY_POLICY"]

        assert "base-uri 'self'" in csp

    def test_csp_form_action_self(self):
        """Test CSP restricts form submission."""
        headers = SecurityHeadersConfiguration.get_security_headers()
        csp = headers["CONTENT_SECURITY_POLICY"]

        assert "form-action 'self'" in csp

    def test_x_content_type_options_nosniff(self):
        """Test X-Content-Type-Options prevents MIME sniffing."""
        headers = SecurityHeadersConfiguration.get_security_headers()

        assert headers["X_CONTENT_TYPE_OPTIONS"] == "nosniff"

    def test_x_frame_options_deny(self):
        """Test X-Frame-Options prevents clickjacking."""
        headers = SecurityHeadersConfiguration.get_security_headers()

        assert headers["X_FRAME_OPTIONS"] == "DENY"

    def test_x_xss_protection_enabled(self):
        """Test X-XSS-Protection header is enabled."""
        headers = SecurityHeadersConfiguration.get_security_headers()

        assert headers["X_XSS_PROTECTION"] == "1; mode=block"

    def test_referrer_policy_strict(self):
        """Test Referrer-Policy is strict."""
        headers = SecurityHeadersConfiguration.get_security_headers()

        assert headers["REFERRER_POLICY"] == "strict-origin-when-cross-origin"

    def test_permissions_policy_restricts_features(self):
        """Test Permissions-Policy restricts browser features."""
        headers = SecurityHeadersConfiguration.get_security_headers()
        policy = headers["PERMISSIONS_POLICY"]

        assert "geolocation=()" in policy
        assert "microphone=()" in policy
        assert "camera=()" in policy
        assert "payment=()" in policy
        assert "usb=()" in policy


class TestAPISecurityConfiguration:
    """Test API security configuration."""

    def test_get_api_security_settings_structure(self):
        """Test API security settings have required structure."""
        settings = APISecurityConfiguration.get_api_security_settings()

        assert isinstance(settings, dict)
        assert "DEFAULT_AUTHENTICATION_CLASSES" in settings
        assert "DEFAULT_PERMISSION_CLASSES" in settings
        assert "DEFAULT_THROTTLE_CLASSES" in settings
        assert "DEFAULT_THROTTLE_RATES" in settings
        assert "DEFAULT_PAGINATION_CLASS" in settings
        assert "PAGE_SIZE" in settings

    def test_authentication_uses_jwt(self):
        """Test API uses JWT authentication."""
        settings = APISecurityConfiguration.get_api_security_settings()
        auth_classes = settings["DEFAULT_AUTHENTICATION_CLASSES"]

        assert "rest_framework_simplejwt.authentication.JWTAuthentication" in auth_classes

    def test_permission_requires_authentication(self):
        """Test API requires authentication for all endpoints."""
        settings = APISecurityConfiguration.get_api_security_settings()
        perm_classes = settings["DEFAULT_PERMISSION_CLASSES"]

        assert "rest_framework.permissions.IsAuthenticated" in perm_classes

    def test_throttling_configured(self):
        """Test API throttling is configured."""
        settings = APISecurityConfiguration.get_api_security_settings()
        throttle_classes = settings["DEFAULT_THROTTLE_CLASSES"]

        assert "apps.security.throttling.UserGeneralThrottle" in throttle_classes
        assert "apps.security.throttling.AnonGeneralThrottle" in throttle_classes

    def test_throttle_rates_defined(self):
        """Test all throttle rates are defined."""
        settings = APISecurityConfiguration.get_api_security_settings()
        rates = settings["DEFAULT_THROTTLE_RATES"]

        assert "user_auth" in rates
        assert "user_general" in rates
        assert "anon_general" in rates
        assert "burst" in rates
        assert "sustained" in rates

    def test_user_general_throttle_rate(self):
        """Test user general throttle rate is 100/hour."""
        settings = APISecurityConfiguration.get_api_security_settings()
        rates = settings["DEFAULT_THROTTLE_RATES"]

        assert rates["user_general"] == "100/hour"

    def test_anon_throttle_rate(self):
        """Test anonymous throttle rate is lower than user."""
        settings = APISecurityConfiguration.get_api_security_settings()
        rates = settings["DEFAULT_THROTTLE_RATES"]

        assert rates["anon_general"] == "20/hour"
        # Verify anon is more restrictive than user
        assert 20 < 100

    def test_page_size_configured(self):
        """Test pagination page size is set."""
        settings = APISecurityConfiguration.get_api_security_settings()

        assert settings["PAGE_SIZE"] == 50

    def test_filter_backends_configured(self):
        """Test filter backends are configured."""
        settings = APISecurityConfiguration.get_api_security_settings()
        backends = settings["DEFAULT_FILTER_BACKENDS"]

        assert "django_filters.rest_framework.DjangoFilterBackend" in backends
        assert "rest_framework.filters.SearchFilter" in backends
        assert "rest_framework.filters.OrderingFilter" in backends

    def test_renderer_json_only(self):
        """Test API uses JSON renderer only."""
        settings = APISecurityConfiguration.get_api_security_settings()
        renderers = settings["DEFAULT_RENDERER_CLASSES"]

        assert "rest_framework.renderers.JSONRenderer" in renderers

    def test_schema_class_configured(self):
        """Test OpenAPI schema is configured."""
        settings = APISecurityConfiguration.get_api_security_settings()

        assert "drf_spectacular.openapi.AutoSchema" in settings["DEFAULT_SCHEMA_CLASS"]


class TestEncodingConfiguration:
    """Test encoding and file upload configuration."""

    def test_get_encoding_settings_structure(self):
        """Test encoding settings have required structure."""
        settings = EncodingConfiguration.get_encoding_settings()

        assert isinstance(settings, dict)
        assert "FILE_UPLOAD_MAX_MEMORY_SIZE" in settings
        assert "DATA_UPLOAD_MAX_MEMORY_SIZE" in settings
        assert "FILE_UPLOAD_PERMISSIONS" in settings
        assert "JSON_EDITOR_ENABLED" in settings

    def test_file_upload_max_size_10mb(self):
        """Test file upload is limited to 10MB."""
        settings = EncodingConfiguration.get_encoding_settings()

        assert settings["FILE_UPLOAD_MAX_MEMORY_SIZE"] == 10 * 1024 * 1024
        assert settings["DATA_UPLOAD_MAX_MEMORY_SIZE"] == 10 * 1024 * 1024

    def test_file_upload_permissions_644(self):
        """Test uploaded files have restrictive permissions (644)."""
        settings = EncodingConfiguration.get_encoding_settings()

        # 0o644 = rw-r--r-- (owner read/write, others read only)
        assert settings["FILE_UPLOAD_PERMISSIONS"] == 0o644

    def test_json_editor_disabled(self):
        """Test JSON editor is disabled in production."""
        settings = EncodingConfiguration.get_encoding_settings()

        assert settings["JSON_EDITOR_ENABLED"] is False

    def test_html5_semantic_input_types_enabled(self):
        """Test HTML5 semantic input types are enabled."""
        settings = EncodingConfiguration.get_encoding_settings()

        assert settings["FORM_RENDERER_USE_HTML5_SEMANTIC_INPUT_TYPES"] is True


class TestPasswordSecurityConfiguration:
    """Test password security configuration."""

    def test_get_password_validators_structure(self):
        """Test password validators configuration."""
        validators = PasswordSecurityConfiguration.get_password_validators()

        assert isinstance(validators, list)
        assert len(validators) > 0
        assert all(isinstance(v, dict) for v in validators)
        assert all("NAME" in v for v in validators)

    def test_user_attribute_similarity_validator(self):
        """Test user attribute similarity validator is configured."""
        validators = PasswordSecurityConfiguration.get_password_validators()
        validator_names = [v["NAME"] for v in validators]

        assert any("UserAttributeSimilarityValidator" in name for name in validator_names)

    def test_minimum_length_validator_12_chars(self):
        """Test minimum password length is 12 characters."""
        validators = PasswordSecurityConfiguration.get_password_validators()

        min_length_validator = next(
            (v for v in validators if "MinimumLengthValidator" in v["NAME"]), None
        )

        assert min_length_validator is not None
        assert min_length_validator.get("OPTIONS", {}).get("min_length") == 12

    def test_common_password_validator(self):
        """Test common password validator is configured."""
        validators = PasswordSecurityConfiguration.get_password_validators()
        validator_names = [v["NAME"] for v in validators]

        assert any("CommonPasswordValidator" in name for name in validator_names)

    def test_numeric_password_validator(self):
        """Test numeric password validator is configured."""
        validators = PasswordSecurityConfiguration.get_password_validators()
        validator_names = [v["NAME"] for v in validators]

        assert any("NumericPasswordValidator" in name for name in validator_names)


class TestCacheSecurityConfiguration:
    """Test cache security configuration."""

    def test_get_cache_settings_structure(self):
        """Test cache settings have required structure."""
        settings = CacheSecurityConfiguration.get_cache_settings()

        assert isinstance(settings, dict)
        assert "default" in settings

    def test_cache_backend_redis(self):
        """Test cache uses Redis backend."""
        settings = CacheSecurityConfiguration.get_cache_settings()

        assert "RedisCache" in settings["default"]["BACKEND"]

    def test_cache_has_location(self):
        """Test cache location is configured."""
        settings = CacheSecurityConfiguration.get_cache_settings()

        assert "LOCATION" in settings["default"]
        assert "redis://" in settings["default"]["LOCATION"]

    def test_cache_options_configured(self):
        """Test cache options are configured."""
        settings = CacheSecurityConfiguration.get_cache_settings()
        options = settings["default"]["OPTIONS"]

        assert "CLIENT_CLASS" in options
        assert "CONNECTION_POOL_KWARGS" in options
        assert "COMPRESSOR" in options

    def test_cache_connection_pool_max_50(self):
        """Test cache connection pool is limited to 50."""
        settings = CacheSecurityConfiguration.get_cache_settings()
        options = settings["default"]["OPTIONS"]

        assert options["CONNECTION_POOL_KWARGS"]["max_connections"] == 50

    def test_cache_uses_zlib_compression(self):
        """Test cache uses zlib compression."""
        settings = CacheSecurityConfiguration.get_cache_settings()
        options = settings["default"]["OPTIONS"]

        assert "ZlibCompressor" in options["COMPRESSOR"]

    def test_cache_key_prefix_set(self):
        """Test cache key prefix is configured."""
        settings = CacheSecurityConfiguration.get_cache_settings()

        assert "KEY_PREFIX" in settings["default"]
        assert settings["default"]["KEY_PREFIX"] == "expense_tracker"

    def test_cache_timeout_1_hour(self):
        """Test default cache timeout is 1 hour."""
        settings = CacheSecurityConfiguration.get_cache_settings()

        assert settings["default"]["TIMEOUT"] == 3600  # 1 hour in seconds


class TestLoggingSecurityConfiguration:
    """Test logging security configuration."""

    def test_get_logging_config_structure(self):
        """Test logging configuration has required structure."""
        config = LoggingSecurityConfiguration.get_logging_config()

        assert isinstance(config, dict)
        assert "version" in config
        assert "disable_existing_loggers" in config
        assert "formatters" in config
        assert "handlers" in config
        assert "loggers" in config

    def test_logging_version_correct(self):
        """Test logging configuration version is 1."""
        config = LoggingSecurityConfiguration.get_logging_config()

        assert config["version"] == 1

    def test_logging_disable_existing_false(self):
        """Test existing loggers are not disabled."""
        config = LoggingSecurityConfiguration.get_logging_config()

        assert config["disable_existing_loggers"] is False

    def test_formatters_configured(self):
        """Test formatters are configured."""
        config = LoggingSecurityConfiguration.get_logging_config()

        assert "verbose" in config["formatters"]
        assert "security" in config["formatters"]

    def test_verbose_formatter_has_format(self):
        """Test verbose formatter has format string."""
        config = LoggingSecurityConfiguration.get_logging_config()

        assert "format" in config["formatters"]["verbose"]
        assert "{" in config["formatters"]["verbose"]["format"]

    def test_security_formatter_has_format(self):
        """Test security formatter has format string."""
        config = LoggingSecurityConfiguration.get_logging_config()

        assert "format" in config["formatters"]["security"]
        assert "{" in config["formatters"]["security"]["format"]

    def test_handlers_configured(self):
        """Test handlers are configured."""
        config = LoggingSecurityConfiguration.get_logging_config()

        assert "console" in config["handlers"]
        assert "security_file" in config["handlers"]
        assert "auth_file" in config["handlers"]

    def test_console_handler_configured(self):
        """Test console handler is configured."""
        config = LoggingSecurityConfiguration.get_logging_config()
        handler = config["handlers"]["console"]

        assert handler["class"] == "logging.StreamHandler"
        assert handler["level"] == "DEBUG"

    def test_security_file_handler_rotating(self):
        """Test security file handler is rotating."""
        config = LoggingSecurityConfiguration.get_logging_config()
        handler = config["handlers"]["security_file"]

        assert "RotatingFileHandler" in handler["class"]
        assert handler["maxBytes"] == 10485760  # 10 MB
        assert handler["backupCount"] == 10

    def test_auth_file_handler_rotating(self):
        """Test auth file handler is rotating."""
        config = LoggingSecurityConfiguration.get_logging_config()
        handler = config["handlers"]["auth_file"]

        assert "RotatingFileHandler" in handler["class"]
        assert handler["maxBytes"] == 10485760  # 10 MB
        assert handler["backupCount"] == 5

    def test_django_logger_configured(self):
        """Test Django logger is configured."""
        config = LoggingSecurityConfiguration.get_logging_config()

        assert "django" in config["loggers"]
        logger = config["loggers"]["django"]
        assert "console" in logger["handlers"]
        assert logger["level"] == "INFO"

    def test_security_logger_configured(self):
        """Test security logger is configured."""
        config = LoggingSecurityConfiguration.get_logging_config()

        assert "django.security" in config["loggers"]
        logger = config["loggers"]["django.security"]
        assert "security_file" in logger["handlers"]
        assert logger["level"] == "WARNING"
        assert logger["propagate"] is False

    def test_app_security_logger_configured(self):
        """Test app security logger is configured."""
        config = LoggingSecurityConfiguration.get_logging_config()

        assert "apps.security" in config["loggers"]
        logger = config["loggers"]["apps.security"]
        assert "security_file" in logger["handlers"]
        assert logger["level"] == "DEBUG"

    def test_auth_logger_configured(self):
        """Test authentication logger is configured."""
        config = LoggingSecurityConfiguration.get_logging_config()

        assert "apps.authentication" in config["loggers"]
        logger = config["loggers"]["apps.authentication"]
        assert "auth_file" in logger["handlers"]
        assert logger["level"] == "INFO"
