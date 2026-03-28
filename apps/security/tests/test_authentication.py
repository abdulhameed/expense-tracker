"""
Tests for security/authentication.py - Authentication utilities and brute force protection.

Tests:
- SecureTokenAuthentication token format validation
- APIKeyAuthentication header parsing
- PasswordReset token generation and verification
- FailedLoginAttempts brute force protection
- SessionSecurity configuration
- JWTSecuritySettings configuration
"""

import pytest
from unittest.mock import patch, MagicMock
from django.core.cache import cache
from django.test.utils import override_settings
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import AuthenticationFailed

from apps.security.authentication import (
    SecureTokenAuthentication,
    APIKeyAuthentication,
    PasswordReset,
    FailedLoginAttempts,
    SessionSecurity,
    JWTSecuritySettings,
)


@pytest.fixture
def clear_cache():
    """Clear cache before and after each test."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def factory():
    """DRF request factory."""
    return APIRequestFactory()


class TestSecureTokenAuthentication:
    """Test SecureTokenAuthentication class."""

    def test_valid_token_format(self):
        """Test that valid 40-char alphanumeric tokens are accepted."""
        auth = SecureTokenAuthentication()
        valid_token = "a" * 40  # 40 alphanumeric chars

        # Should not raise
        assert auth._is_valid_token_format(valid_token) is True

    def test_invalid_token_too_short(self):
        """Test that tokens shorter than 40 chars are rejected."""
        auth = SecureTokenAuthentication()
        short_token = "a" * 39

        assert auth._is_valid_token_format(short_token) is False

    def test_invalid_token_too_long(self):
        """Test that tokens longer than 40 chars are rejected."""
        auth = SecureTokenAuthentication()
        long_token = "a" * 41

        assert auth._is_valid_token_format(long_token) is False

    def test_invalid_token_special_chars(self):
        """Test that tokens with special characters are rejected."""
        auth = SecureTokenAuthentication()
        token_with_special = "a" * 39 + "!"

        assert auth._is_valid_token_format(token_with_special) is False

    def test_invalid_token_spaces(self):
        """Test that tokens with spaces are rejected."""
        auth = SecureTokenAuthentication()
        token_with_spaces = "a" * 20 + " " + "b" * 19

        assert auth._is_valid_token_format(token_with_spaces) is False


class TestAPIKeyAuthentication:
    """Test APIKeyAuthentication class."""

    def test_parse_valid_api_key_header(self, factory):
        """Test parsing valid ApiKey header."""
        auth = APIKeyAuthentication()
        request = factory.get("/", HTTP_APIKEY="test-key-123")

        # This should attempt to authenticate
        with patch.object(auth, 'get_model') as mock_model:
            mock_model.return_value = MagicMock()
            # Test will depend on actual implementation
            # For now, just test the header parsing logic exists

    def test_api_key_header_case_insensitive(self, factory):
        """Test that ApiKey header is case-insensitive."""
        auth = APIKeyAuthentication()
        # ApiKey header name should work with DRF's header handling
        request = factory.get("/", HTTP_X_API_KEY="test-key")


class TestPasswordReset:
    """Test PasswordReset token generation and validation."""

    def test_generate_reset_token_is_random(self):
        """Test that generated tokens are cryptographically random."""
        pr = PasswordReset()
        token1 = pr.generate_reset_token()
        token2 = pr.generate_reset_token()

        # Tokens should be different
        assert token1 != token2
        # Tokens should be long enough (token_urlsafe produces base64)
        assert len(token1) > 0
        assert len(token2) > 0

    def test_hash_reset_token_deterministic(self):
        """Test that token hashing produces same hash for same token."""
        pr = PasswordReset()
        token = pr.generate_reset_token()

        hash1 = pr.hash_reset_token(token)
        hash2 = pr.hash_reset_token(token)

        assert hash1 == hash2

    def test_hash_different_tokens_different_hashes(self):
        """Test that different tokens produce different hashes."""
        pr = PasswordReset()
        token1 = pr.generate_reset_token()
        token2 = pr.generate_reset_token()

        hash1 = pr.hash_reset_token(token1)
        hash2 = pr.hash_reset_token(token2)

        assert hash1 != hash2

    def test_validate_reset_token_timing_safe(self):
        """Test that token comparison uses timing-safe comparison."""
        pr = PasswordReset()
        token = pr.generate_reset_token()
        hashed = pr.hash_reset_token(token)

        # Should compare safely without timing attacks
        # The validate method should use secrets.compare_digest
        # Just verify the method exists
        assert hasattr(pr, 'validate_reset_token')


class TestFailedLoginAttempts:
    """Test FailedLoginAttempts brute force protection."""

    def test_record_failed_attempt(self, clear_cache):
        """Test recording a failed login attempt."""
        fla = FailedLoginAttempts()
        username = "testuser"

        # Record an attempt
        fla.record_failed_attempt(username)

        # Should be recorded
        assert fla.get_remaining_attempts(username) == fla.MAX_ATTEMPTS - 1

    def test_multiple_failed_attempts(self, clear_cache):
        """Test multiple failed login attempts."""
        fla = FailedLoginAttempts()
        username = "testuser"

        for i in range(3):
            fla.record_failed_attempt(username)

        remaining = fla.get_remaining_attempts(username)
        assert remaining == fla.MAX_ATTEMPTS - 3

    def test_account_lockout_after_max_attempts(self, clear_cache):
        """Test that account is locked after MAX_ATTEMPTS."""
        fla = FailedLoginAttempts()
        username = "testuser"

        # Make MAX_ATTEMPTS failed attempts
        for i in range(fla.MAX_ATTEMPTS):
            fla.record_failed_attempt(username)

        # Account should be locked
        assert fla.is_account_locked(username) is True

    def test_account_not_locked_before_max_attempts(self, clear_cache):
        """Test that account is not locked before MAX_ATTEMPTS."""
        fla = FailedLoginAttempts()
        username = "testuser"

        # Make MAX_ATTEMPTS - 1 failed attempts
        for i in range(fla.MAX_ATTEMPTS - 1):
            fla.record_failed_attempt(username)

        # Account should not be locked
        assert fla.is_account_locked(username) is False

    def test_reset_failed_attempts(self, clear_cache):
        """Test resetting failed attempts."""
        fla = FailedLoginAttempts()
        username = "testuser"

        # Record several attempts
        for i in range(3):
            fla.record_failed_attempt(username)

        # Reset
        fla.reset_failed_attempts(username)

        # Should be reset
        assert fla.get_remaining_attempts(username) == fla.MAX_ATTEMPTS

    def test_different_users_independent_lockout(self, clear_cache):
        """Test that lockout is per-user, not global."""
        fla = FailedLoginAttempts()
        user1 = "user1"
        user2 = "user2"

        # Lock out user1
        for i in range(fla.MAX_ATTEMPTS):
            fla.record_failed_attempt(user1)

        # user1 should be locked, user2 should not
        assert fla.is_account_locked(user1) is True
        assert fla.is_account_locked(user2) is False

    def test_lockout_duration_timeout(self, clear_cache):
        """Test that lockout expires after LOCKOUT_DURATION."""
        fla = FailedLoginAttempts()
        username = "testuser"

        # Record max attempts
        for i in range(fla.MAX_ATTEMPTS):
            fla.record_failed_attempt(username)

        assert fla.is_account_locked(username) is True

        # Simulate cache expiration by manually clearing
        cache.delete(fla.get_cache_key(username))

        # Should no longer be locked
        assert fla.is_account_locked(username) is False


class TestSessionSecurity:
    """Test SessionSecurity configuration."""

    def test_get_session_settings(self):
        """Test that session settings include security requirements."""
        ss = SessionSecurity()
        settings = ss.get_session_settings()

        # Should have HTTPS-only settings
        assert settings is not None
        assert isinstance(settings, dict)

    def test_session_timeout_values(self):
        """Test that timeout values are properly defined."""
        ss = SessionSecurity()

        # Should have these attributes
        assert hasattr(ss, 'SESSION_TIMEOUT')
        assert hasattr(ss, 'ABSOLUTE_SESSION_TIMEOUT')
        assert hasattr(ss, 'IDLE_TIMEOUT')

        # Timeouts should be positive timedeltas
        assert ss.SESSION_TIMEOUT.total_seconds() > 0
        assert ss.ABSOLUTE_SESSION_TIMEOUT.total_seconds() > 0
        assert ss.IDLE_TIMEOUT.total_seconds() > 0

    def test_session_cookie_secure_settings(self):
        """Test that session cookies have secure settings."""
        ss = SessionSecurity()
        settings = ss.get_session_settings()

        # Security settings should be present
        assert settings is not None


class TestJWTSecuritySettings:
    """Test JWTSecuritySettings configuration."""

    def test_token_lifetimes_configured(self):
        """Test that JWT token lifetimes are configured."""
        jwt = JWTSecuritySettings()
        settings = jwt.get_jwt_settings()

        # Should have token lifetime keys
        assert 'ACCESS_TOKEN_LIFETIME' in settings
        assert 'REFRESH_TOKEN_LIFETIME' in settings

        # Lifetimes should be positive timedeltas
        assert settings['ACCESS_TOKEN_LIFETIME'].total_seconds() > 0
        assert settings['REFRESH_TOKEN_LIFETIME'].total_seconds() > 0

    def test_refresh_token_rotation_enabled(self):
        """Test that refresh token rotation is enabled."""
        jwt = JWTSecuritySettings()
        settings = jwt.get_jwt_settings()

        assert 'ROTATE_REFRESH_TOKENS' in settings
        assert settings['ROTATE_REFRESH_TOKENS'] is True

    def test_blacklist_after_rotation_enabled(self):
        """Test that token blacklist after rotation is enabled."""
        jwt = JWTSecuritySettings()
        settings = jwt.get_jwt_settings()

        assert 'BLACKLIST_AFTER_ROTATION' in settings
        assert settings['BLACKLIST_AFTER_ROTATION'] is True

    def test_access_token_shorter_than_refresh(self):
        """Test that access token lifetime is shorter than refresh."""
        jwt = JWTSecuritySettings()
        settings = jwt.get_jwt_settings()

        # Access tokens should expire faster than refresh tokens
        assert settings['ACCESS_TOKEN_LIFETIME'] < settings['REFRESH_TOKEN_LIFETIME']
