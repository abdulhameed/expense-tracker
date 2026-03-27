"""
Performance monitoring and profiling utilities.
"""
import logging
import time
from functools import wraps
from typing import Callable

from django.db import connection

logger = logging.getLogger(__name__)


class QueryCounterContext:
    """
    Context manager to count database queries.

    Usage:
        with QueryCounterContext() as counter:
            # Code that makes queries
            expensive_operation()
        print(f"Executed {counter.count} queries in {counter.time}ms")
    """

    def __init__(self):
        self.count = 0
        self.time = 0
        self.start_time = None
        self.start_queries = None

    def __enter__(self):
        self.start_time = time.time()
        self.start_queries = len(connection.queries)
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):  # noqa: F841
        self.time = (time.time() - self.start_time) * 1000  # Convert to ms
        self.count = len(connection.queries) - self.start_queries

        if self.count > 10:
            logger.warning(
                f"High query count: {self.count} queries executed in {self.time:.2f}ms"
            )


def monitor_queries(threshold: int = 10):
    """
    Decorator to monitor and log database queries.

    Args:
        threshold: Log warning if more than this many queries executed

    Usage:
        @monitor_queries(threshold=5)
        def expensive_view(request):
            return response
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with QueryCounterContext() as counter:
                result = func(*args, **kwargs)

            logger.debug(
                f"{func.__name__}: {counter.count} queries in {counter.time:.2f}ms"
            )

            if counter.count > threshold:
                logger.warning(
                    f"{func.__name__}: High query count ({counter.count} queries, "
                    f"{counter.time:.2f}ms) - consider optimizing"
                )

            return result

        return wrapper

    return decorator


class PerformanceTimer:
    """
    Context manager to measure execution time.

    Usage:
        with PerformanceTimer("database_operation") as timer:
            # Code to measure
            expensive_operation()
        print(timer.elapsed_ms)  # Elapsed time in milliseconds
    """

    def __init__(self, name: str = "", threshold_ms: int = 1000):
        self.name = name
        self.threshold_ms = threshold_ms
        self.start_time = None
        self.elapsed_ms = 0

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):  # noqa: F841
        self.elapsed_ms = (time.time() - self.start_time) * 1000

        if self.name:
            logger.debug(f"{self.name}: {self.elapsed_ms:.2f}ms")

        if self.elapsed_ms > self.threshold_ms:
            logger.warning(
                f"{self.name}: Slow operation ({self.elapsed_ms:.2f}ms, "
                f"threshold: {self.threshold_ms}ms)"
            )


def profile_performance(threshold_ms: int = 1000):
    """
    Decorator to profile function execution time.

    Args:
        threshold_ms: Log warning if execution exceeds this threshold

    Usage:
        @profile_performance(threshold_ms=500)
        def slow_function():
            return result
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            with PerformanceTimer(
                name=f"{func.__module__}.{func.__name__}",
                threshold_ms=threshold_ms,
            ):
                return func(*args, **kwargs)

        return wrapper

    return decorator


def get_slow_queries(time_threshold_ms: int = 500) -> list:
    """
    Get list of slow database queries.

    Args:
        time_threshold_ms: Only return queries slower than this

    Returns:
        List of slow query information
    """
    slow_queries = []

    for query in connection.queries:
        time_ms = float(query.get("time", 0)) * 1000

        if time_ms >= time_threshold_ms:
            slow_queries.append({
                "sql": query["sql"],
                "time_ms": time_ms,
            })

    return slow_queries


def log_slow_queries(time_threshold_ms: int = 500):
    """
    Log all slow queries executed during a request.

    Args:
        time_threshold_ms: Log queries slower than this
    """
    slow_queries = get_slow_queries(time_threshold_ms)

    if slow_queries:
        logger.warning(f"Slow queries detected: {len(slow_queries)}")
        for query in slow_queries:
            logger.warning(
                f"  {query['time_ms']:.2f}ms: {query['sql'][:200]}..."
            )


class DatabaseMetrics:
    """Collect database performance metrics."""

    @staticmethod
    def get_connection_info() -> dict:
        """Get database connection information."""
        db_conn = connection
        return {
            "alias": db_conn.alias,
            "engine": db_conn.settings_dict.get("ENGINE"),
            "host": db_conn.settings_dict.get("HOST"),
            "port": db_conn.settings_dict.get("PORT"),
            "name": db_conn.settings_dict.get("NAME"),
        }

    @staticmethod
    def get_query_stats() -> dict:
        """Get statistics about executed queries."""
        queries = connection.queries
        if not queries:
            return {
                "total_queries": 0,
                "total_time_ms": 0,
                "average_time_ms": 0,
            }

        total_time = sum(float(q.get("time", 0)) for q in queries)
        return {
            "total_queries": len(queries),
            "total_time_ms": total_time * 1000,
            "average_time_ms": (total_time / len(queries)) * 1000,
            "min_time_ms": min(float(q.get("time", 0)) for q in queries) * 1000,
            "max_time_ms": max(float(q.get("time", 0)) for q in queries) * 1000,
        }
