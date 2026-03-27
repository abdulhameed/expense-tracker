"""
Utilities package for performance optimization, caching, and monitoring.
"""
from .caching import (
    cache_result,
    cache_queryset,
    invalidate_cache,
    make_cache_key,
    CacheMixin,
)
from .monitoring import (
    QueryCounterContext,
    PerformanceTimer,
    monitor_queries,
    profile_performance,
    get_slow_queries,
    log_slow_queries,
    DatabaseMetrics,
)

__all__ = [
    # Caching
    "cache_result",
    "cache_queryset",
    "invalidate_cache",
    "make_cache_key",
    "CacheMixin",
    # Monitoring
    "QueryCounterContext",
    "PerformanceTimer",
    "monitor_queries",
    "profile_performance",
    "get_slow_queries",
    "log_slow_queries",
    "DatabaseMetrics",
]
