"""
Security hardening tests.
"""
import pytest
from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from apps.security.throttling import (
    UserGeneralThrottle,
    AnonGeneralThrottle,
    BurstThrottle,
)
from apps.security.validators import (
    sanitize_html,
    validate_no_special_chars,
    validate_no_sql_injection,
    validate_secure_password,
    validate_email_domain,
    escape_user_input,
    SafeFieldValidator,
)
from apps.security.authentication import FailedLoginAttempts

User = get_user_model()


class ThrottlingTestCase(APITestCase):
    """Test rate limiting and throttling."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="TestPassword123!",
        )

    def test_authenticated_user_general_throttle(self):
        """Test authenticated user throttle rate."""
        self.client.force_authenticate(user=self.user)
        throttle = UserGeneralThrottle()

        # Throttle should allow user
        request = self.client.get("/")
        request.user = self.user
        assert throttle.allow_request(request, self.client)

    def test_anonymous_user_throttle(self):
        """Test anonymous user throttle rate."""
        throttle = AnonGeneralThrottle()

        # Create mock request
        from unittest.mock import Mock

        request = Mock()
        request.user = None
        request.META = {"REMOTE_ADDR": "127.0.0.1"}

        # Should allow request
        assert throttle.allow_request(request, self.client)

    def test_burst_throttle(self):
        """Test burst throttle for strict rate limiting."""
        self.client.force_authenticate(user=self.user)
        throttle = BurstThrottle()

        from unittest.mock import Mock

        request = Mock()
        request.user = self.user

        # Should allow initial requests
        assert throttle.allow_request(request, self.client)


class InputValidationTestCase(TestCase):
    """Test input validation and sanitization."""

    def test_sanitize_html_removes_dangerous_tags(self):
        """Test HTML sanitization removes script tags."""
        html = "<p>Hello</p><script>alert('xss')</script><p>World</p>"
        cleaned = sanitize_html(html)

        assert "<script>" not in cleaned
        assert "alert" not in cleaned
        assert "<p>Hello</p>" in cleaned

    def test_sanitize_html_preserves_safe_tags(self):
        """Test HTML sanitization preserves safe tags."""
        html = "<p>Hello <strong>world</strong></p>"
        cleaned = sanitize_html(html)

        assert "<p>" in cleaned
        assert "<strong>" in cleaned

    def test_validate_no_special_chars(self):
        """Test validation rejects special characters."""
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            validate_no_special_chars("hello<script>")

        with pytest.raises(ValidationError):
            validate_no_special_chars("test'; DROP TABLE")

        # Should not raise for safe string
        validate_no_special_chars("hello_world")

    def test_validate_no_sql_injection(self):
        """Test SQL injection pattern detection."""
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            validate_no_sql_injection("test'; DROP TABLE users;--")

        with pytest.raises(ValidationError):
            validate_no_sql_injection("UNION SELECT * FROM users")

        # Should not raise for safe string
        validate_no_sql_injection("normal user input")

    def test_validate_secure_password(self):
        """Test password strength validation."""
        from django.core.exceptions import ValidationError

        # Too short
        with pytest.raises(ValidationError):
            validate_secure_password("Short1!")

        # No uppercase
        with pytest.raises(ValidationError):
            validate_secure_password("lowercaseonly1!")

        # No lowercase
        with pytest.raises(ValidationError):
            validate_secure_password("UPPERCASEONLY1!")

        # No digit
        with pytest.raises(ValidationError):
            validate_secure_password("NoDigitsHere!")

        # No special char
        with pytest.raises(ValidationError):
            validate_secure_password("NoSpecial1234")

        # Valid password
        validate_secure_password("SecurePass123!")

    def test_validate_email_domain(self):
        """Test email domain validation."""
        from django.core.exceptions import ValidationError

        # Blocked domain
        with pytest.raises(ValidationError):
            validate_email_domain("test@tempmail.com")

        with pytest.raises(ValidationError):
            validate_email_domain("test@mailinator.com")

        # Valid domain
        validate_email_domain("test@example.com")

    def test_escape_user_input(self):
        """Test user input escaping."""
        input_str = "<script>alert('xss')</script>"
        escaped = escape_user_input(input_str)

        assert "<script>" not in escaped
        assert "&lt;script&gt;" in escaped

    def test_safe_field_validator_username(self):
        """Test username validation."""
        from django.core.exceptions import ValidationError

        # Valid usernames
        SafeFieldValidator.validate_username("john_doe")
        SafeFieldValidator.validate_username("user.name")
        SafeFieldValidator.validate_username("user-123")

        # Invalid usernames
        with pytest.raises(ValidationError):
            SafeFieldValidator.validate_username("ab")  # Too short

        with pytest.raises(ValidationError):
            SafeFieldValidator.validate_username("user@domain")  # Invalid char

    def test_safe_field_validator_filename(self):
        """Test filename validation."""
        from django.core.exceptions import ValidationError

        # Valid filenames
        SafeFieldValidator.validate_filename("document.pdf")
        SafeFieldValidator.validate_filename("image-001.jpg")

        # Invalid filenames
        with pytest.raises(ValidationError):
            SafeFieldValidator.validate_filename("../../../etc/passwd")

        with pytest.raises(ValidationError):
            SafeFieldValidator.validate_filename("/etc/passwd")

    def test_safe_field_validator_url_path(self):
        """Test URL path validation."""
        from django.core.exceptions import ValidationError

        # Valid paths
        SafeFieldValidator.validate_url_path("api/v1/users")
        SafeFieldValidator.validate_url_path("documents/file.pdf")

        # Invalid paths
        with pytest.raises(ValidationError):
            SafeFieldValidator.validate_url_path("../../../etc/passwd")

        with pytest.raises(ValidationError):
            SafeFieldValidator.validate_url_path("/admin")

    def test_safe_field_validator_search_query(self):
        """Test search query validation."""
        from django.core.exceptions import ValidationError

        # Valid queries
        SafeFieldValidator.validate_search_query("john doe")
        SafeFieldValidator.validate_search_query("project 2026")

        # Invalid queries
        with pytest.raises(ValidationError):
            SafeFieldValidator.validate_search_query("<script>alert</script>")


class BruteForceProtectionTestCase(TestCase):
    """Test brute force attack protection."""

    def setUp(self):
        self.username = "testuser"

    def test_record_failed_attempt(self):
        """Test recording failed login attempts."""
        FailedLoginAttempts.record_failed_attempt(self.username)

        # Should record attempt
        remaining = FailedLoginAttempts.get_remaining_attempts(self.username)
        assert remaining == 4  # 5 max - 1 attempt

    def test_account_locked_after_max_attempts(self):
        """Test account locks after max failed attempts."""
        for i in range(FailedLoginAttempts.MAX_ATTEMPTS):
            FailedLoginAttempts.record_failed_attempt(self.username)

        # Account should be locked
        assert FailedLoginAttempts.is_account_locked(self.username)

    def test_reset_failed_attempts(self):
        """Test resetting failed login attempts."""
        for i in range(3):
            FailedLoginAttempts.record_failed_attempt(self.username)

        # Reset attempts
        FailedLoginAttempts.reset_failed_attempts(self.username)

        # Should have all attempts available
        remaining = FailedLoginAttempts.get_remaining_attempts(self.username)
        assert remaining == FailedLoginAttempts.MAX_ATTEMPTS

    def test_get_remaining_attempts(self):
        """Test getting remaining login attempts."""
        # Fresh account
        remaining = FailedLoginAttempts.get_remaining_attempts(self.username)
        assert remaining == 5

        # After 2 failed attempts
        FailedLoginAttempts.record_failed_attempt(self.username)
        FailedLoginAttempts.record_failed_attempt(self.username)
        remaining = FailedLoginAttempts.get_remaining_attempts(self.username)
        assert remaining == 3


class SecurityHeadersTestCase(TestCase):
    """Test security headers in responses."""

    def setUp(self):
        self.client = Client()

    def test_security_headers_present_in_response(self):
        """Test that security headers are present in responses."""
        # Get any public endpoint
        response = self.client.get("/api/v1/schema/")

        # Check for security headers
        assert "X-Content-Type-Options" in response
        assert response["X-Content-Type-Options"] == "nosniff"


class CSRFProtectionTestCase(APITestCase):
    """Test CSRF protection."""

    def test_csrf_cookie_attributes(self):
        """Test CSRF cookie has secure attributes."""
        from django.conf import settings

        assert settings.CSRF_COOKIE_SECURE is True
        assert settings.CSRF_COOKIE_HTTPONLY is True
        assert settings.CSRF_COOKIE_SAMESITE == "Strict"


class SessionSecurityTestCase(TestCase):
    """Test session security."""

    def test_session_cookie_attributes(self):
        """Test session cookie has secure attributes."""
        from django.conf import settings

        assert settings.SESSION_COOKIE_SECURE is True
        assert settings.SESSION_COOKIE_HTTPONLY is True
        assert settings.SESSION_COOKIE_SAMESITE == "Strict"

    def test_session_expires_at_browser_close(self):
        """Test session expires at browser close."""
        from django.conf import settings

        assert settings.SESSION_EXPIRE_AT_BROWSER_CLOSE is True


class CORSSecurityTestCase(APITestCase):
    """Test CORS security configuration."""

    def test_cors_allows_only_configured_origins(self):
        """Test CORS only allows configured origins."""
        from django.conf import settings

        # Should have configured origins
        assert len(settings.CORS_ALLOWED_ORIGINS) > 0

    def test_cors_requires_credentials(self):
        """Test CORS allows credentials."""
        from django.conf import settings

        assert settings.CORS_ALLOW_CREDENTIALS is True


class PasswordValidationTestCase(TestCase):
    """Test password validation configuration."""

    def test_password_minimum_length_enforced(self):
        """Test password minimum length is enforced."""
        user = User()
        user.username = "testuser"
        user.email = "test@example.com"

        from django.core.exceptions import ValidationError
        from django.contrib.auth.password_validation import validate_password

        # Short password should be rejected
        with pytest.raises(ValidationError):
            validate_password("short1!")

    def test_password_complexity_enforced(self):
        """Test password complexity requirements."""
        from django.core.exceptions import ValidationError
        from django.contrib.auth.password_validation import validate_password

        # Password without uppercase
        with pytest.raises(ValidationError):
            validate_password("onlysmallletters123!")


class AuthenticationThrottleTestCase(APITestCase):
    """Test throttling on authentication endpoints."""

    def test_login_endpoint_throttled(self):
        """Test login endpoint has rate limiting."""
        from django.conf import settings

        # Check throttle settings configured
        assert "DEFAULT_THROTTLE_RATES" in settings.REST_FRAMEWORK
        throttle_rates = settings.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]

        # Should have auth throttle configured
        assert "user_auth" in throttle_rates or "user_general" in throttle_rates
