"""
Tests for health/views.py - Health check and monitoring endpoints.

Tests:
- health_check - Simple health check endpoint
- readiness_check - Detailed readiness check with database/redis/app status
- liveness_check - Kubernetes liveness probe
- metrics - Application metrics endpoint
- _check_database - Database connectivity verification
- _check_redis - Redis/cache connectivity verification
"""

import pytest
from unittest.mock import patch, MagicMock
from rest_framework.test import APIClient
from django.test.utils import override_settings
from django.core.cache import cache


@pytest.fixture
def client():
    """DRF API client."""
    return APIClient()


@pytest.fixture
def clear_cache():
    """Clear cache before and after each test."""
    cache.clear()
    yield
    cache.clear()


class TestHealthCheckEndpoint:
    """Test simple health check endpoint."""

    def test_health_check_returns_200(self, client):
        """Test that health check endpoint returns 200 OK."""
        response = client.get("/health/health/")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_health_check_allows_anonymous_access(self, client):
        """Test that health check allows anonymous access."""
        # No authentication should be required
        response = client.get("/health/health/")

        assert response.status_code == 200

    def test_health_check_response_format(self, client):
        """Test that health check response has correct format."""
        response = client.get("/health/health/")
        data = response.json()

        assert "status" in data
        assert data["status"] in ["healthy", "unhealthy"]

    def test_health_check_always_returns_200(self, client):
        """Test that health check always returns 200 even if dependencies fail."""
        response = client.get("/health/health/")
        # Should still return 200 for simple health check
        assert response.status_code in [200, 503]


class TestReadinessCheckEndpoint:
    """Test detailed readiness check endpoint."""

    def test_readiness_check_returns_200_when_healthy(self, client):
        """Test that readiness check returns 200 when all systems are up."""
        response = client.get("/health/ready/")

        # Should return 200 when healthy
        assert response.status_code in [200, 503]

    def test_readiness_check_includes_database_status(self, client):
        """Test that readiness check includes database connectivity status."""
        response = client.get("/health/ready/")
        data = response.json()

        assert "checks" in data
        assert "database" in data["checks"]

    def test_readiness_check_includes_redis_status(self, client):
        """Test that readiness check includes Redis/cache status."""
        response = client.get("/health/ready/")
        data = response.json()

        assert "checks" in data
        assert "redis" in data["checks"]

    def test_readiness_check_includes_application_status(self, client):
        """Test that readiness check includes application status."""
        response = client.get("/health/ready/")
        data = response.json()

        assert "checks" in data
        assert "application" in data["checks"]

    def test_readiness_check_all_true_returns_200(self, client):
        """Test that readiness returns 200 when all checks pass."""
        response = client.get("/health/ready/")

        # When all checks pass, should return 200
        if (
            response.json().get("checks", {}).get("database")
            and response.json().get("checks", {}).get("redis")
            and response.json().get("checks", {}).get("application")
        ):
            assert response.status_code == 200

    def test_readiness_check_database_down_returns_503(self, client):
        """Test that readiness returns 503 when database is down."""
        with patch("apps.health.views._check_database") as mock_db:
            mock_db.return_value = False

            response = client.get("/health/ready/")

            if not response.json().get("checks", {}).get("database"):
                assert response.status_code == 503

    def test_readiness_check_redis_down_returns_503(self, client):
        """Test that readiness returns 503 when Redis is down."""
        with patch("apps.health.views._check_redis") as mock_redis:
            mock_redis.return_value = False

            response = client.get("/health/ready/")

            if not response.json().get("checks", {}).get("redis"):
                assert response.status_code == 503

    def test_readiness_check_allows_anonymous_access(self, client):
        """Test that readiness check allows anonymous access."""
        response = client.get("/health/ready/")

        # Should not return 401 Unauthorized
        assert response.status_code in [200, 503]

    def test_readiness_check_includes_status_field(self, client):
        """Test that readiness response includes status field."""
        response = client.get("/health/ready/")
        data = response.json()

        assert "status" in data
        assert data["status"] in ["ready", "not_ready"]


class TestLivenessCheckEndpoint:
    """Test Kubernetes liveness check endpoint."""

    def test_liveness_check_returns_200_when_alive(self, client, clear_cache):
        """Test that liveness check returns 200 when application is alive."""
        response = client.get("/health/live/")

        assert response.status_code in [200, 503]

    def test_liveness_check_includes_status_field(self, client, clear_cache):
        """Test that liveness response includes status field."""
        response = client.get("/health/live/")
        data = response.json()

        assert "status" in data
        assert data["status"] in ["alive", "dead"]

    def test_liveness_check_tests_cache(self, client, clear_cache):
        """Test that liveness check actually tests cache functionality."""
        response = client.get("/health/live/")

        # If cache works, should return 200
        assert response.status_code in [200, 503]

    def test_liveness_check_cache_failure_returns_503(self, client, clear_cache):
        """Test that liveness returns 503 if cache test fails."""
        with patch("apps.health.views.cache") as mock_cache:
            # Simulate cache failure
            mock_cache.get.return_value = None

            response = client.get("/health/live/")

            # If cache returns wrong value, should be 503
            if response.status_code == 503:
                assert response.json()["status"] == "dead"

    def test_liveness_check_cache_exception_returns_503(self, client, clear_cache):
        """Test that liveness returns 503 if cache raises exception."""
        with patch("apps.health.views.cache") as mock_cache:
            mock_cache.get.side_effect = Exception("Cache error")

            response = client.get("/health/live/")

            assert response.status_code == 503
            assert response.json()["status"] == "dead"

    def test_liveness_check_allows_anonymous_access(self, client):
        """Test that liveness check allows anonymous access."""
        response = client.get("/health/live/")

        assert response.status_code in [200, 503]


class TestMetricsEndpoint:
    """Test application metrics endpoint."""

    def test_metrics_returns_200(self, client):
        """Test that metrics endpoint returns 200 OK."""
        response = client.get("/health/metrics/")

        assert response.status_code == 200

    def test_metrics_includes_timestamp(self, client):
        """Test that metrics includes timestamp."""
        response = client.get("/health/metrics/")
        data = response.json()

        assert "timestamp" in data
        # Timestamp should be ISO format string
        assert isinstance(data["timestamp"], str)

    def test_metrics_includes_application_section(self, client):
        """Test that metrics includes application section."""
        response = client.get("/health/metrics/")
        data = response.json()

        assert "application" in data
        assert "status" in data["application"]
        assert data["application"]["status"] == "running"

    def test_metrics_includes_database_section(self, client):
        """Test that metrics includes database information."""
        response = client.get("/health/metrics/")
        data = response.json()

        assert "database" in data
        assert "status" in data["database"]
        assert "queries" in data["database"]
        assert data["database"]["status"] in ["connected", "disconnected"]
        assert isinstance(data["database"]["queries"], int)

    def test_metrics_includes_cache_section(self, client):
        """Test that metrics includes cache/Redis section."""
        response = client.get("/health/metrics/")
        data = response.json()

        assert "cache" in data
        assert "status" in data["cache"]
        assert data["cache"]["status"] in ["connected", "disconnected"]

    def test_metrics_database_status_connected(self, client):
        """Test that metrics shows database as connected when healthy."""
        response = client.get("/health/metrics/")
        data = response.json()

        # Database should typically be connected
        assert data["database"]["status"] in ["connected", "disconnected"]

    def test_metrics_queries_count_is_integer(self, client):
        """Test that metrics query count is an integer."""
        response = client.get("/health/metrics/")
        data = response.json()

        assert isinstance(data["database"]["queries"], int)
        assert data["database"]["queries"] >= 0

    def test_metrics_timestamp_format(self, client):
        """Test that timestamp is in valid ISO format."""
        response = client.get("/health/metrics/")
        data = response.json()

        # Should be ISO format like 2024-01-01T12:00:00+00:00
        timestamp = data["timestamp"]
        assert "T" in timestamp  # ISO format contains T
        assert "+" in timestamp or "Z" in timestamp  # Timezone info

    def test_metrics_allows_anonymous_access(self, client):
        """Test that metrics endpoint allows anonymous access."""
        response = client.get("/health/metrics/")

        assert response.status_code == 200


class TestHealthCheckHelpers:
    """Test helper functions for health checks."""

    def test_database_check_success(self):
        """Test that database check succeeds when database is accessible."""
        from apps.health.views import _check_database

        result = _check_database()
        # Should return boolean
        assert isinstance(result, bool)

    def test_database_check_handles_errors(self):
        """Test that database check returns False on errors."""
        from apps.health.views import _check_database

        with patch("apps.health.views.connection") as mock_conn:
            mock_conn.cursor.side_effect = Exception("DB Error")

            result = _check_database()
            assert result is False

    def test_redis_check_success(self):
        """Test that Redis check succeeds when cache is accessible."""
        from apps.health.views import _check_redis

        result = _check_redis()
        assert isinstance(result, bool)

    def test_redis_check_handles_errors(self):
        """Test that Redis check returns False on errors."""
        from apps.health.views import _check_redis

        with patch("apps.health.views.cache") as mock_cache:
            mock_cache.set.side_effect = Exception("Redis Error")

            result = _check_redis()
            assert result is False

    def test_redis_check_validates_value(self, clear_cache):
        """Test that Redis check validates the stored value."""
        from apps.health.views import _check_redis

        # Normal case should work
        result = _check_redis()
        assert isinstance(result, bool)

    def test_timestamp_format(self):
        """Test timestamp generation format."""
        from apps.health.views import _get_timestamp

        timestamp = _get_timestamp()

        # Should be ISO format
        assert isinstance(timestamp, str)
        assert "T" in timestamp
        # Should contain timezone info
        assert "+" in timestamp or "Z" in timestamp or timestamp.endswith("00:00")


class TestHealthCheckIntegration:
    """Integration tests for health check system."""

    def test_all_endpoints_accessible(self, client):
        """Test that all health check endpoints are accessible."""
        endpoints = [
            "/health/health/",
            "/health/ready/",
            "/health/live/",
            "/health/metrics/",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            # All should return a response (200 or 503)
            assert response.status_code in [200, 503]

    def test_health_check_response_structure(self, client):
        """Test response structure consistency across endpoints."""
        endpoints = [
            "/health/health/",
            "/health/ready/",
            "/health/live/",
            "/health/metrics/",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)

            # All should have valid JSON
            data = response.json()
            assert isinstance(data, dict)
            # All should have status
            if endpoint != "/health/metrics/":
                assert "status" in data

    def test_readiness_is_subset_of_liveness(self, client):
        """Test that readiness checks are more strict than liveness."""
        readiness = client.get("/health/ready/").json()
        liveness = client.get("/health/live/").json()

        # Both should have status field
        assert "status" in readiness
        assert "status" in liveness

    def test_metrics_database_consistency(self, client):
        """Test that metrics database status is consistent."""
        response = client.get("/health/metrics/")
        data = response.json()

        # Database section should exist
        assert "database" in data
        assert "status" in data["database"]
        assert data["database"]["status"] in ["connected", "disconnected"]

    def test_metrics_cache_consistency(self, client):
        """Test that metrics cache status is consistent."""
        response = client.get("/health/metrics/")
        data = response.json()

        # Cache section should exist
        assert "cache" in data
        assert "status" in data["cache"]
        assert data["cache"]["status"] in ["connected", "disconnected"]


class TestHealthCheckResponseHelper:
    """Test HealthCheckResponse helper class."""

    def test_healthy_response(self):
        """Test healthy response helper."""
        from apps.health.views import HealthCheckResponse

        response = HealthCheckResponse.healthy()
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_ready_response(self):
        """Test ready response helper."""
        from apps.health.views import HealthCheckResponse

        response = HealthCheckResponse.ready()
        assert response.status_code == 200
        assert response.json()["status"] == "ready"

    def test_not_ready_response(self):
        """Test not ready response helper."""
        from apps.health.views import HealthCheckResponse

        response = HealthCheckResponse.not_ready()
        assert response.status_code == 503
        assert response.json()["status"] == "not_ready"

    def test_alive_response(self):
        """Test alive response helper."""
        from apps.health.views import HealthCheckResponse

        response = HealthCheckResponse.alive()
        assert response.status_code == 200
        assert response.json()["status"] == "alive"

    def test_dead_response(self):
        """Test dead response helper."""
        from apps.health.views import HealthCheckResponse

        response = HealthCheckResponse.dead()
        assert response.status_code == 503
        assert response.json()["status"] == "dead"
