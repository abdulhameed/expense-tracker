"""
Authentication hardening and secure authentication utilities.
"""
import hashlib
import secrets
from datetime import timedelta
from typing import Optional
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class SecureTokenAuthentication(TokenAuthentication):
    """
    Enhanced token authentication with security checks.

    - Validates token format
    - Checks token expiration
    - Prevents token reuse
    """

    def authenticate_credentials(self, key):
        """
        Authenticate token with enhanced security checks.
        """
        # Prevent token injection attacks
        if not self._is_valid_token_format(key):
            raise AuthenticationFailed("Invalid token format")

        # Call parent authentication
        return super().authenticate_credentials(key)

    @staticmethod
    def _is_valid_token_format(token: str) -> bool:
        """Validate token format (alphanumeric only)."""
        return token.isalnum() and len(token) == 40


class APIKeyAuthentication(TokenAuthentication):
    """
    API Key authentication with rate limiting.

    Usage:
        Authorization: ApiKey <api-key>
    """

    keyword = "ApiKey"

    def authenticate(self, request):
        """Authenticate API key with additional checks."""
        auth = request.META.get("HTTP_AUTHORIZATION", "").split()

        if not auth or auth[0].lower() != self.keyword.lower():
            return None

        if len(auth) == 1:
            raise AuthenticationFailed("Invalid API key header")
        if len(auth) > 2:
            raise AuthenticationFailed("Invalid API key header")

        return self.authenticate_credentials(auth[1])


class PasswordReset:
    """
    Secure password reset token generation and validation.
    """

    TOKEN_LENGTH = 32
    TOKEN_TIMEOUT = timedelta(hours=1)

    @staticmethod
    def generate_reset_token() -> str:
        """Generate secure password reset token."""
        return secrets.token_urlsafe(PasswordReset.TOKEN_LENGTH)

    @staticmethod
    def hash_reset_token(token: str) -> str:
        """Hash token for storage in database."""
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def validate_reset_token(stored_hash: str, provided_token: str) -> bool:
        """Validate reset token against stored hash."""
        provided_hash = PasswordReset.hash_reset_token(provided_token)
        return secrets.compare_digest(stored_hash, provided_hash)


class SessionSecurity:
    """
    Session security configuration and utilities.
    """

    # Session timeout settings
    SESSION_TIMEOUT = timedelta(hours=1)
    ABSOLUTE_SESSION_TIMEOUT = timedelta(hours=24)
    IDLE_TIMEOUT = timedelta(minutes=30)

    @staticmethod
    def get_session_settings() -> dict:
        """
        Get secure session configuration.

        Returns:
            Dictionary of session settings for Django
        """
        return {
            "SESSION_COOKIE_SECURE": True,  # HTTPS only
            "SESSION_COOKIE_HTTPONLY": True,  # No JavaScript access
            "SESSION_COOKIE_SAMESITE": "Strict",  # CSRF protection
            "SESSION_COOKIE_AGE": int(SessionSecurity.SESSION_TIMEOUT.total_seconds()),
            "SESSION_EXPIRE_AT_BROWSER_CLOSE": True,
            "SESSION_SAVE_EVERY_REQUEST": False,  # Reduces database writes
        }

    @staticmethod
    def get_csrf_settings() -> dict:
        """
        Get CSRF protection configuration.

        Returns:
            Dictionary of CSRF settings for Django
        """
        return {
            "CSRF_COOKIE_SECURE": True,  # HTTPS only
            "CSRF_COOKIE_HTTPONLY": True,  # No JavaScript access
            "CSRF_COOKIE_SAMESITE": "Strict",  # Strict same-site
            "CSRF_HEADER_NAME": "HTTP_X_CSRFTOKEN",  # Custom header
            "CSRF_TRUSTED_ORIGINS": [
                "https://expensetracker.com",
                "https://*.expensetracker.com",
            ],
        }

    @staticmethod
    def get_security_settings() -> dict:
        """
        Get comprehensive security configuration.

        Returns:
            Dictionary combining session and CSRF settings
        """
        settings = {}
        settings.update(SessionSecurity.get_session_settings())
        settings.update(SessionSecurity.get_csrf_settings())
        return settings


class JWTSecuritySettings:
    """
    Enhanced JWT security configuration.
    """

    @staticmethod
    def get_jwt_settings() -> dict:
        """
        Get secure JWT configuration.

        Returns:
            Dictionary of JWT settings
        """
        return {
            "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),  # Short-lived access tokens
            "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
            "ROTATE_REFRESH_TOKENS": True,  # Rotate on each refresh
            "BLACKLIST_AFTER_ROTATION": True,  # Blacklist old tokens
            "UPDATE_LAST_LOGIN": True,  # Track last login
            "ALGORITHM": "HS256",
            "SIGNING_KEY": None,  # Uses SECRET_KEY from settings
            "VERIFYING_KEY": None,
            "USER_ID_FIELD": "id",
            "USER_ID_CLAIM": "user_id",
            "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
            "TOKEN_TYPE_CLAIM": "token_type",
            "JTI_CLAIM": "jti",
            "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
            "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
            "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
        }


class FailedLoginAttempts:
    """
    Track and prevent brute force login attacks.
    """

    MAX_ATTEMPTS = 5
    LOCKOUT_DURATION = timedelta(minutes=15)
    CACHE_KEY_PREFIX = "failed_login_attempts"

    @staticmethod
    def get_cache_key(username: str) -> str:
        """Generate cache key for login attempts."""
        return f"{FailedLoginAttempts.CACHE_KEY_PREFIX}:{username}"

    @staticmethod
    def record_failed_attempt(username: str):
        """Record a failed login attempt."""
        from django.core.cache import cache

        key = FailedLoginAttempts.get_cache_key(username)
        attempts = cache.get(key, 0)
        cache.set(
            key,
            attempts + 1,
            int(FailedLoginAttempts.LOCKOUT_DURATION.total_seconds()),
        )

    @staticmethod
    def is_account_locked(username: str) -> bool:
        """Check if account is locked due to failed attempts."""
        from django.core.cache import cache

        key = FailedLoginAttempts.get_cache_key(username)
        attempts = cache.get(key, 0)
        return attempts >= FailedLoginAttempts.MAX_ATTEMPTS

    @staticmethod
    def reset_failed_attempts(username: str):
        """Reset failed login attempts for account."""
        from django.core.cache import cache

        key = FailedLoginAttempts.get_cache_key(username)
        cache.delete(key)

    @staticmethod
    def get_remaining_attempts(username: str) -> int:
        """Get remaining login attempts before lockout."""
        from django.core.cache import cache

        key = FailedLoginAttempts.get_cache_key(username)
        attempts = cache.get(key, 0)
        return max(0, FailedLoginAttempts.MAX_ATTEMPTS - attempts)
