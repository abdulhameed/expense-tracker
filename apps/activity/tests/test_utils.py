"""
Tests for activity/utils.py - Activity logging utilities.

Tests:
- get_client_ip - Extract client IP from request
- get_user_agent - Extract user agent from request
"""

import pytest
from unittest.mock import MagicMock
from django.test import RequestFactory


@pytest.fixture
def request_factory():
    """Provide a Django request factory."""
    return RequestFactory()


@pytest.fixture
def mock_request():
    """Create a mock request object."""
    request = MagicMock()
    request.META = {}
    return request


class TestGetClientIP:
    """Test client IP extraction from requests."""

    def test_get_client_ip_from_remote_addr(self, mock_request):
        """Test getting client IP from REMOTE_ADDR."""
        from apps.activity.utils import get_client_ip

        mock_request.META["REMOTE_ADDR"] = "192.168.1.1"

        ip = get_client_ip(mock_request)

        assert ip == "192.168.1.1"

    def test_get_client_ip_from_x_forwarded_for(self, mock_request):
        """Test getting client IP from X-Forwarded-For header."""
        from apps.activity.utils import get_client_ip

        mock_request.META["HTTP_X_FORWARDED_FOR"] = "203.0.113.1, 198.51.100.1"

        ip = get_client_ip(mock_request)

        # Should return the first IP in the list
        assert ip == "203.0.113.1"

    def test_get_client_ip_x_forwarded_for_priority(self, mock_request):
        """Test X-Forwarded-For takes priority over REMOTE_ADDR."""
        from apps.activity.utils import get_client_ip

        mock_request.META["HTTP_X_FORWARDED_FOR"] = "203.0.113.1"
        mock_request.META["REMOTE_ADDR"] = "192.168.1.1"

        ip = get_client_ip(mock_request)

        assert ip == "203.0.113.1"

    def test_get_client_ip_x_forwarded_for_strips_whitespace(self, mock_request):
        """Test whitespace is stripped from X-Forwarded-For."""
        from apps.activity.utils import get_client_ip

        # X-Forwarded-For can have spaces after commas
        mock_request.META["HTTP_X_FORWARDED_FOR"] = "203.0.113.1 , 198.51.100.1"

        ip = get_client_ip(mock_request)

        assert ip == "203.0.113.1"

    def test_get_client_ip_multiple_forward_for_gets_first(self, mock_request):
        """Test that first IP in X-Forwarded-For is returned."""
        from apps.activity.utils import get_client_ip

        mock_request.META["HTTP_X_FORWARDED_FOR"] = "203.0.113.1, 198.51.100.1, 192.0.2.1"

        ip = get_client_ip(mock_request)

        assert ip == "203.0.113.1"

    def test_get_client_ip_no_headers(self, mock_request):
        """Test get_client_ip returns None when no IP headers present."""
        from apps.activity.utils import get_client_ip

        mock_request.META = {}

        ip = get_client_ip(mock_request)

        assert ip is None

    def test_get_client_ip_with_none_request(self):
        """Test get_client_ip returns None with None request."""
        from apps.activity.utils import get_client_ip

        ip = get_client_ip(None)

        assert ip is None

    def test_get_client_ip_ipv4_address(self, mock_request):
        """Test IPv4 address extraction."""
        from apps.activity.utils import get_client_ip

        mock_request.META["REMOTE_ADDR"] = "10.0.0.1"

        ip = get_client_ip(mock_request)

        assert ip == "10.0.0.1"

    def test_get_client_ip_ipv6_address(self, mock_request):
        """Test IPv6 address extraction."""
        from apps.activity.utils import get_client_ip

        mock_request.META["REMOTE_ADDR"] = "2001:db8::1"

        ip = get_client_ip(mock_request)

        assert ip == "2001:db8::1"

    def test_get_client_ip_localhost(self, mock_request):
        """Test localhost IP extraction."""
        from apps.activity.utils import get_client_ip

        mock_request.META["REMOTE_ADDR"] = "127.0.0.1"

        ip = get_client_ip(mock_request)

        assert ip == "127.0.0.1"

    def test_get_client_ip_with_django_request(self, request_factory):
        """Test with real Django request."""
        from apps.activity.utils import get_client_ip

        request = request_factory.get("/")
        request.META["REMOTE_ADDR"] = "192.168.1.100"

        ip = get_client_ip(request)

        assert ip == "192.168.1.100"

    def test_get_client_ip_with_django_request_forwarded(self, request_factory):
        """Test with real Django request with X-Forwarded-For."""
        from apps.activity.utils import get_client_ip

        request = request_factory.get("/", HTTP_X_FORWARDED_FOR="203.0.113.1")

        ip = get_client_ip(request)

        assert ip == "203.0.113.1"


class TestGetUserAgent:
    """Test user agent extraction from requests."""

    def test_get_user_agent_present(self, mock_request):
        """Test extracting user agent when present."""
        from apps.activity.utils import get_user_agent

        mock_request.META["HTTP_USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

        user_agent = get_user_agent(mock_request)

        assert user_agent == "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

    def test_get_user_agent_missing(self, mock_request):
        """Test get_user_agent returns empty string when missing."""
        from apps.activity.utils import get_user_agent

        mock_request.META = {}

        user_agent = get_user_agent(mock_request)

        assert user_agent == ""

    def test_get_user_agent_none_request(self):
        """Test get_user_agent returns empty string with None request."""
        from apps.activity.utils import get_user_agent

        user_agent = get_user_agent(None)

        assert user_agent == ""

    def test_get_user_agent_chrome(self, mock_request):
        """Test extracting Chrome user agent."""
        from apps.activity.utils import get_user_agent

        mock_request.META["HTTP_USER_AGENT"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

        user_agent = get_user_agent(mock_request)

        assert "Chrome" in user_agent
        assert "Mozilla" in user_agent

    def test_get_user_agent_firefox(self, mock_request):
        """Test extracting Firefox user agent."""
        from apps.activity.utils import get_user_agent

        mock_request.META["HTTP_USER_AGENT"] = "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0"

        user_agent = get_user_agent(mock_request)

        assert "Firefox" in user_agent

    def test_get_user_agent_safari(self, mock_request):
        """Test extracting Safari user agent."""
        from apps.activity.utils import get_user_agent

        mock_request.META["HTTP_USER_AGENT"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"

        user_agent = get_user_agent(mock_request)

        assert "Safari" in user_agent

    def test_get_user_agent_mobile(self, mock_request):
        """Test extracting mobile user agent."""
        from apps.activity.utils import get_user_agent

        mock_request.META["HTTP_USER_AGENT"] = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"

        user_agent = get_user_agent(mock_request)

        assert "iPhone" in user_agent
        assert "Mobile" in user_agent

    def test_get_user_agent_bot(self, mock_request):
        """Test extracting bot user agent."""
        from apps.activity.utils import get_user_agent

        mock_request.META["HTTP_USER_AGENT"] = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"

        user_agent = get_user_agent(mock_request)

        assert "Googlebot" in user_agent

    def test_get_user_agent_with_django_request(self, request_factory):
        """Test with real Django request."""
        from apps.activity.utils import get_user_agent

        request = request_factory.get("/", HTTP_USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

        user_agent = get_user_agent(request)

        assert "Mozilla" in user_agent
        assert "Windows" in user_agent

    def test_get_user_agent_with_django_request_missing(self, request_factory):
        """Test with real Django request without user agent."""
        from apps.activity.utils import get_user_agent

        request = request_factory.get("/")

        user_agent = get_user_agent(request)

        # Django request should have a default or empty user agent
        assert isinstance(user_agent, str)

    def test_get_user_agent_empty_string(self, mock_request):
        """Test with empty user agent string."""
        from apps.activity.utils import get_user_agent

        mock_request.META["HTTP_USER_AGENT"] = ""

        user_agent = get_user_agent(mock_request)

        assert user_agent == ""

    def test_get_user_agent_special_characters(self, mock_request):
        """Test user agent with special characters."""
        from apps.activity.utils import get_user_agent

        mock_request.META["HTTP_USER_AGENT"] = "MyApp/1.0 (compatible; +http://example.com)"

        user_agent = get_user_agent(mock_request)

        assert user_agent == "MyApp/1.0 (compatible; +http://example.com)"

    def test_get_user_agent_case_sensitive(self, mock_request):
        """Test user agent case is preserved."""
        from apps.activity.utils import get_user_agent

        mock_request.META["HTTP_USER_AGENT"] = "Mozilla/5.0 (MiXeD CaSe)"

        user_agent = get_user_agent(mock_request)

        assert "MiXeD CaSe" in user_agent
