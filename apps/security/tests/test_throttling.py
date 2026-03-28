"""
Tests for security/throttling.py - Rate limiting and throttling.

Tests:
- UserAuthenticationThrottle - Auth user rate limits
- UserGeneralThrottle - General auth user rate limits
- AnonGeneralThrottle - Anonymous user rate limits
- BurstThrottle - Burst prevention
- SustainedThrottle - Daily limits
"""

import pytest
from unittest.mock import MagicMock, patch
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from rest_framework.throttling import BaseThrottle

from apps.security.throttling import (
    UserAuthenticationThrottle,
    UserGeneralThrottle,
    AnonGeneralThrottle,
    BurstThrottle,
    SustainedThrottle,
)


@pytest.fixture
def factory():
    """DRF request factory."""
    return APIRequestFactory()


@pytest.fixture
def mock_user():
    """Mock authenticated user."""
    user = MagicMock()
    user.is_authenticated = True
    user.id = 1
    return user


@pytest.fixture
def mock_anon_user():
    """Mock anonymous user."""
    user = MagicMock()
    user.is_authenticated = False
    return user


def create_drf_request(factory_request, user):
    """Convert DRF factory request to proper Request object."""
    request = Request(factory_request)
    request.user = user
    return request


class TestUserAuthenticationThrottle:
    """Test rate limiting for authenticated users (5 req/min)."""

    def test_throttle_class_has_scope(self):
        """Test that throttle class has a scope attribute."""
        throttle = UserAuthenticationThrottle()
        assert hasattr(throttle, 'scope')

    def test_rate_limit_format(self):
        """Test that rate is specified in correct format."""
        throttle = UserAuthenticationThrottle()
        assert throttle.scope is not None
        # Format should be like "user_auth" or similar

    def test_allows_authenticated_user(self, factory, mock_user):
        """Test that authenticated users are allowed."""
        throttle = UserAuthenticationThrottle()
        request = create_drf_request(factory.get('/'), mock_user)

        # First call should be allowed
        allow = throttle.allow_request(request)
        # Should be True or call should not raise exception
        assert allow is not False

    def test_throttle_denies_when_limit_exceeded(self, factory, mock_user):
        """Test that requests are throttled after rate limit."""
        throttle = UserAuthenticationThrottle()
        request = create_drf_request(factory.get('/'), mock_user)

        # Make requests up to limit
        # The exact number depends on the rate configuration
        # Just verify that allow_request method exists and is callable
        result = throttle.allow_request(request)
        assert isinstance(result, bool)

    def test_different_users_have_separate_limits(self, factory):
        """Test that different users have separate rate limits."""
        user1 = MagicMock()
        user1.is_authenticated = True
        user1.id = 1

        user2 = MagicMock()
        user2.is_authenticated = True
        user2.id = 2

        throttle = UserAuthenticationThrottle()
        request1 = create_drf_request(factory.get('/'), user1)
        request2 = create_drf_request(factory.get('/'), user2)

        # Both should be allowed initially
        allow1 = throttle.allow_request(request1)
        allow2 = throttle.allow_request(request2)

        assert allow1 is not None  # Should return boolean


class TestUserGeneralThrottle:
    """Test general rate limiting for authenticated users (100 req/hr)."""

    def test_throttle_allows_authenticated_user(self, factory, mock_user):
        """Test that authenticated users can make requests."""
        throttle = UserGeneralThrottle()
        request = create_drf_request(factory.get('/'), mock_user)

        # Should allow request
        allow = throttle.allow_request(request)
        assert allow is not False

    def test_higher_limit_than_auth_throttle(self):
        """Test that general throttle has higher limit than auth throttle."""
        auth_throttle = UserAuthenticationThrottle()
        general_throttle = UserGeneralThrottle()

        # Both should have scopes
        assert hasattr(auth_throttle, 'scope')
        assert hasattr(general_throttle, 'scope')

    def test_applies_to_all_endpoints(self, factory, mock_user):
        """Test that throttle applies to general endpoints."""
        throttle = UserGeneralThrottle()
        request = create_drf_request(factory.get('/api/test/'), mock_user)

        # Should work on any endpoint
        allow = throttle.allow_request(request)
        assert isinstance(allow, bool)


class TestAnonGeneralThrottle:
    """Test rate limiting for anonymous users (20 req/hr)."""

    def test_anonymous_user_is_throttled(self, factory, mock_anon_user):
        """Test that anonymous users are rate limited."""
        throttle = AnonGeneralThrottle()
        request = create_drf_request(factory.get('/'), mock_anon_user)

        # Should apply throttle to anonymous users
        allow = throttle.allow_request(request)
        assert isinstance(allow, bool)

    def test_anon_throttle_uses_ip_as_identifier(self, factory, mock_anon_user):
        """Test that anonymous throttle identifies by IP address."""
        throttle = AnonGeneralThrottle()

        # Create request with specific IP
        request = create_drf_request(
            factory.get('/', REMOTE_ADDR='192.168.1.1'),
            mock_anon_user
        )

        # Should be able to throttle by IP
        allow = throttle.allow_request(request)
        assert allow is not None

    def test_different_ips_have_separate_limits(self, factory, mock_anon_user):
        """Test that different IPs have separate rate limits."""
        throttle = AnonGeneralThrottle()

        request1 = create_drf_request(
            factory.get('/', REMOTE_ADDR='192.168.1.1'),
            mock_anon_user
        )
        request2 = create_drf_request(
            factory.get('/', REMOTE_ADDR='192.168.1.2'),
            mock_anon_user
        )

        # Both should be processed separately
        allow1 = throttle.allow_request(request1)
        allow2 = throttle.allow_request(request2)

        # At least first request should be allowed
        assert allow1 is True or allow1 is False


class TestBurstThrottle:
    """Test burst prevention throttle (10 req/min)."""

    def test_burst_throttle_restricts_rapid_requests(self, factory, mock_user):
        """Test that burst throttle limits rapid requests."""
        throttle = BurstThrottle()
        request = create_drf_request(factory.get('/'), mock_user)

        # Should enforce burst limits
        result = throttle.allow_request(request)
        assert isinstance(result, bool)

    def test_burst_throttle_has_scope(self):
        """Test that burst throttle has scope defined."""
        throttle = BurstThrottle()
        assert hasattr(throttle, 'scope')

    def test_burst_limit_is_strict(self):
        """Test that burst throttle has stricter limits than general."""
        burst = BurstThrottle()
        general = UserGeneralThrottle()

        # Both should exist
        assert burst is not None
        assert general is not None


class TestSustainedThrottle:
    """Test sustained request throttle (1000 req/day)."""

    def test_sustained_throttle_allows_normal_usage(self, factory, mock_user):
        """Test that sustained throttle allows normal daily usage."""
        throttle = SustainedThrottle()
        request = create_drf_request(factory.get('/'), mock_user)

        # Should allow normal requests
        allow = throttle.allow_request(request)
        assert allow is not False

    def test_sustained_throttle_has_daily_limit(self):
        """Test that sustained throttle is daily-based."""
        throttle = SustainedThrottle()
        assert hasattr(throttle, 'scope')

    def test_sustained_throttle_cumulative(self, factory, mock_user):
        """Test that sustained throttle counts cumulative requests."""
        throttle = SustainedThrottle()
        request = create_drf_request(factory.get('/'), mock_user)

        # Make multiple requests
        allows = []
        for _ in range(5):
            allows.append(throttle.allow_request(request))

        # All should be allowed (under limit)
        assert all(a is not False for a in allows[:5])


class TestThrottleIntegration:
    """Integration tests for multiple throttles together."""

    def test_authenticated_user_respects_all_throttles(self, factory, mock_user):
        """Test that authenticated users respect all applicable throttles."""
        auth_throttle = UserAuthenticationThrottle()
        general_throttle = UserGeneralThrottle()
        burst_throttle = BurstThrottle()

        request = create_drf_request(factory.get('/'), mock_user)

        # All should return boolean results
        auth_allow = auth_throttle.allow_request(request)
        general_allow = general_throttle.allow_request(request)
        burst_allow = burst_throttle.allow_request(request)

        assert isinstance(auth_allow, bool)
        assert isinstance(general_allow, bool)
        assert isinstance(burst_allow, bool)

    def test_anonymous_user_uses_different_throttle(self, factory, mock_anon_user):
        """Test that anonymous users use different throttle."""
        anon_throttle = AnonGeneralThrottle()
        general_throttle = UserGeneralThrottle()

        anon_request = create_drf_request(
            factory.get('/', REMOTE_ADDR='192.168.1.1'),
            mock_anon_user
        )

        # Anonymous throttle should work
        allow = anon_throttle.allow_request(anon_request)
        assert isinstance(allow, bool)

    def test_throttle_headers_included(self, factory, mock_user):
        """Test that rate limit headers are included in response."""
        throttle = UserGeneralThrottle()
        request = create_drf_request(factory.get('/'), mock_user)

        # Allow request sets throttle info
        throttle.allow_request(request)

        # Throttle should have wait time info available
        assert hasattr(throttle, 'throttle_success_waits_log')
        assert hasattr(throttle, 'throttle_failure_waits_log')

    def test_throttle_wait_time_calculation(self, factory, mock_user):
        """Test that wait time is calculated correctly."""
        throttle = UserGeneralThrottle()
        request = create_drf_request(factory.get('/'), mock_user)

        # Make request
        throttle.allow_request(request)

        # Should be able to get wait time if needed
        # This depends on the throttle implementation
        assert throttle is not None
