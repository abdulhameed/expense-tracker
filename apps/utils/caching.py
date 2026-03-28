"""
Caching utilities and decorators for performance optimization.
"""
import hashlib
import json
from functools import wraps
from typing import Any, Callable, Optional

from django.core.cache import cache
from django.views.decorators.cache import cache_page as django_cache_page


def make_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a cache key from arguments and keyword arguments.

    Args:
        prefix: Cache key prefix
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key

    Returns:
        Cache key string
    """
    key_data = {
        "args": [str(arg) for arg in args],
        "kwargs": {k: str(v) for k, v in sorted(kwargs.items())},
    }
    key_hash = hashlib.md5(
        json.dumps(key_data, sort_keys=True).encode()
    ).hexdigest()
    return f"{prefix}:{key_hash}"


def cache_result(
    timeout: int = 3600,
    key_prefix: Optional[str] = None,
):
    """
    Decorator to cache function results.

    Args:
        timeout: Cache timeout in seconds (default: 1 hour)
        key_prefix: Cache key prefix (default: function name)

    Usage:
        @cache_result(timeout=3600, key_prefix="my_view")
        def expensive_operation(user_id, project_id):
            return result
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            prefix = key_prefix or func.__name__
            cache_key = make_cache_key(prefix, *args, **kwargs)

            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result

        return wrapper

    return decorator


def invalidate_cache(key_prefix: str, *args, **kwargs):
    """
    Invalidate cache entries.

    Args:
        key_prefix: Cache key prefix to invalidate
        *args: Arguments for specific key (if provided, only that key is invalidated)
        **kwargs: Keyword arguments for specific key
    """
    # Always invalidate the specific cache key created with the given arguments
    cache_key = make_cache_key(key_prefix, *args, **kwargs)
    cache.delete(cache_key)


class CacheMixin:
    """
    Mixin for views to add caching support.

    Usage:
        class MyView(CacheMixin, generics.ListAPIView):
            cache_timeout = 3600
            cache_key_prefix = "myview"
    """

    cache_timeout = 3600
    cache_key_prefix = None

    def get_cache_key(self, request):
        """Generate cache key for request."""
        prefix = self.cache_key_prefix or self.__class__.__name__
        cache_params = {
            "path": request.path,
            "params": str(request.GET),
            "user": str(request.user.id) if request.user.is_authenticated else "anon",
        }
        return make_cache_key(prefix, **cache_params)

    def get_from_cache(self, request):
        """Get response from cache if available."""
        cache_key = self.get_cache_key(request)
        return cache.get(cache_key)

    def set_cache(self, request, response_data):
        """Cache response data."""
        cache_key = self.get_cache_key(request)
        cache.set(cache_key, response_data, self.cache_timeout)
        return response_data

    def invalidate_cache(self, request):
        """Invalidate cache for this view."""
        cache_key = self.get_cache_key(request)
        cache.delete(cache_key)


def cache_queryset(
    timeout: int = 3600,
    key_prefix: Optional[str] = None,
):
    """
    Decorator to cache queryset results.

    Useful for expensive database queries that are called frequently.

    Args:
        timeout: Cache timeout in seconds
        key_prefix: Cache key prefix

    Usage:
        @cache_queryset(timeout=1800)
        def get_user_projects(user):
            return Project.objects.filter(owner=user)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            prefix = key_prefix or f"{func.__module__}.{func.__name__}"
            cache_key = make_cache_key(prefix, *args, **kwargs)

            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result

            # Execute queryset and cache results
            queryset = func(*args, **kwargs)
            # Force evaluation by converting to list
            result = list(queryset)
            cache.set(cache_key, result, timeout)
            return result

        return wrapper

    return decorator
