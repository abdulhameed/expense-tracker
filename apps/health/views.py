"""
Health check and monitoring views.
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Simple health check endpoint for load balancers.

    Returns 200 OK if application is running.
    """
    return Response({"status": "healthy"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def readiness_check(request):
    """
    Detailed readiness check for Kubernetes probes.

    Checks:
    - Database connectivity
    - Redis connectivity
    - Application status

    Returns 200 OK if all systems are ready.
    Returns 503 Service Unavailable if any system is down.
    """
    checks = {
        "database": _check_database(),
        "redis": _check_redis(),
        "application": True,
    }

    if not all(checks.values()):
        return Response(
            {"status": "not_ready", "checks": checks},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return Response(
        {"status": "ready", "checks": checks},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def liveness_check(request):
    """
    Liveness check for Kubernetes probes.

    Checks if application is still alive (no deadlocks).

    Returns 200 OK if application is alive.
    Returns 503 Service Unavailable if application appears dead.
    """
    try:
        # Try to set and get a cache value
        test_key = "liveness_check"
        cache.set(test_key, "alive", 10)
        value = cache.get(test_key)

        if value != "alive":
            logger.error("Liveness check failed: Cache test failed")
            return Response(
                {"status": "dead"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({"status": "alive"}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        return Response(
            {"status": "dead", "error": str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def metrics(request):
    """
    Simple metrics endpoint.

    Returns basic application metrics.
    """
    db_status = _check_database()
    redis_status = _check_redis()
    db_queries = len(connection.queries)

    return Response(
        {
            "timestamp": _get_timestamp(),
            "application": {
                "status": "running",
                "debug": False,
            },
            "database": {
                "status": "connected" if db_status else "disconnected",
                "queries": db_queries,
            },
            "cache": {
                "status": "connected" if redis_status else "disconnected",
            },
        },
        status=status.HTTP_200_OK,
    )


def _check_database() -> bool:
    """Check if database is accessible."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database check failed: {e}")
        return False


def _check_redis() -> bool:
    """Check if Redis/cache is accessible."""
    try:
        cache.set("health_check", "ok", 10)
        value = cache.get("health_check")
        return value == "ok"
    except Exception as e:
        logger.error(f"Redis check failed: {e}")
        return False


def _get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


class HealthCheckResponse:
    """Helper class for health check responses."""

    @staticmethod
    def healthy():
        """Return healthy response."""
        return JsonResponse(
            {"status": "healthy"},
            status=200,
        )

    @staticmethod
    def ready():
        """Return ready response."""
        return JsonResponse(
            {"status": "ready"},
            status=200,
        )

    @staticmethod
    def not_ready():
        """Return not ready response."""
        return JsonResponse(
            {"status": "not_ready"},
            status=503,
        )

    @staticmethod
    def alive():
        """Return alive response."""
        return JsonResponse(
            {"status": "alive"},
            status=200,
        )

    @staticmethod
    def dead():
        """Return dead response."""
        return JsonResponse(
            {"status": "dead"},
            status=503,
        )
