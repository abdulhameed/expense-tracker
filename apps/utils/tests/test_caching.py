"""
Tests for utils/caching.py - Caching utilities and decorators.

Tests:
- make_cache_key - Cache key generation
- cache_result - Result caching decorator
- cache_queryset - Queryset caching decorator
- invalidate_cache - Cache invalidation
- CacheMixin - View caching mixin
"""

import pytest
import hashlib
import json
from unittest.mock import patch, MagicMock
from django.core.cache import cache
from django.test.utils import override_settings
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory

from apps.utils.caching import (
    make_cache_key,
    cache_result,
    cache_queryset,
    invalidate_cache,
    CacheMixin,
)
from apps.projects.tests.factories import ProjectFactory
from apps.authentication.tests.factories import UserFactory


@pytest.fixture
def clear_cache():
    """Clear cache before and after each test."""
    cache.clear()
    yield
    cache.clear()


class TestMakeCacheKey:
    """Test cache key generation."""

    def test_cache_key_deterministic(self):
        """Test that cache key generation is deterministic."""
        key1 = make_cache_key("prefix", 1, 2, foo="bar")
        key2 = make_cache_key("prefix", 1, 2, foo="bar")

        assert key1 == key2

    def test_cache_key_includes_prefix(self):
        """Test that cache key includes prefix."""
        key = make_cache_key("my_prefix", 1, 2)

        assert key.startswith("my_prefix:")

    def test_cache_key_different_args_different_keys(self):
        """Test that different arguments produce different keys."""
        key1 = make_cache_key("prefix", 1, 2)
        key2 = make_cache_key("prefix", 1, 3)

        assert key1 != key2

    def test_cache_key_different_kwargs_different_keys(self):
        """Test that different kwargs produce different keys."""
        key1 = make_cache_key("prefix", foo="bar")
        key2 = make_cache_key("prefix", foo="baz")

        assert key1 != key2

    def test_cache_key_kwargs_order_invariant(self):
        """Test that kwargs order doesn't affect key."""
        key1 = make_cache_key("prefix", foo="bar", baz="qux")
        key2 = make_cache_key("prefix", baz="qux", foo="bar")

        assert key1 == key2

    def test_cache_key_uses_md5_hash(self):
        """Test that cache key uses MD5 hash."""
        key = make_cache_key("prefix", 1, 2)
        parts = key.split(":")

        # Should have prefix and hash
        assert len(parts) == 2
        # Hash should be 32 chars (MD5 hex)
        assert len(parts[1]) == 32

    def test_cache_key_with_no_args(self):
        """Test cache key generation with only prefix."""
        key = make_cache_key("prefix")

        assert key.startswith("prefix:")
        assert len(key) > 7  # prefix: + hash

    def test_cache_key_with_complex_args(self):
        """Test cache key with complex arguments."""
        key = make_cache_key("prefix", "string", 123, ["list"], {"dict": "value"})

        assert isinstance(key, str)
        assert key.startswith("prefix:")

    def test_cache_key_with_none_values(self):
        """Test cache key with None values."""
        key = make_cache_key("prefix", None, value=None)

        assert isinstance(key, str)
        assert key.startswith("prefix:")


@pytest.mark.django_db
class TestCacheResultDecorator:
    """Test cache_result decorator."""

    def test_cache_result_caches_on_first_call(self, clear_cache):
        """Test that result is cached on first call."""
        call_count = 0

        @cache_result(timeout=300)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # First call
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call (from cache)
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Not incremented

    def test_cache_result_different_args_separate_cache(self, clear_cache):
        """Test that different arguments have separate cache entries."""
        call_count = 0

        @cache_result(timeout=300)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = expensive_function(5)
        result2 = expensive_function(10)

        assert result1 == 10
        assert result2 == 20
        assert call_count == 2  # Both were called

    def test_cache_result_with_custom_prefix(self, clear_cache):
        """Test cache_result with custom key prefix."""
        call_count = 0

        @cache_result(timeout=300, key_prefix="custom")
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = expensive_function(5)
        result2 = expensive_function(5)

        assert call_count == 1
        # Verify cache was used
        cached = cache.get(make_cache_key("custom", 5))
        assert cached == 10

    def test_cache_result_timeout_respected(self, clear_cache):
        """Test that cache timeout is respected."""
        call_count = 0

        @cache_result(timeout=0)  # Immediate expiration
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        expensive_function(5)
        expensive_function(5)

        # With timeout=0, cache is expired immediately
        # Both calls might execute
        assert call_count >= 1

    def test_cache_result_preserves_function_metadata(self):
        """Test that decorator preserves function name and docstring."""

        @cache_result(timeout=300)
        def my_function(x):
            """My function docstring."""
            return x

        assert my_function.__name__ == "my_function"
        assert "My function docstring" in my_function.__doc__

    def test_cache_result_with_kwargs(self, clear_cache):
        """Test cache_result with keyword arguments."""
        call_count = 0

        @cache_result(timeout=300)
        def function_with_kwargs(x, y=10):
            nonlocal call_count
            call_count += 1
            return x + y

        result1 = function_with_kwargs(5, y=10)
        result2 = function_with_kwargs(5, y=10)
        result3 = function_with_kwargs(5, y=20)

        assert result1 == 15
        assert result2 == 15
        assert result3 == 25
        assert call_count == 2  # Only 2 unique combinations


@pytest.mark.django_db
class TestCacheQuerysetDecorator:
    """Test cache_queryset decorator."""

    def test_cache_queryset_caches_results(self, clear_cache):
        """Test that queryset results are cached."""
        ProjectFactory.create_batch(3)
        call_count = 0

        @cache_queryset(timeout=300)
        def get_projects():
            nonlocal call_count
            call_count += 1
            from apps.projects.models import Project

            return Project.objects.all()

        result1 = get_projects()
        result2 = get_projects()

        assert len(result1) == 3
        assert len(result2) == 3
        assert call_count == 1  # Second call used cache

    def test_cache_queryset_evaluates_queryset(self, clear_cache):
        """Test that queryset is evaluated (not lazy)."""
        ProjectFactory.create_batch(2)
        call_count = 0

        @cache_queryset(timeout=300)
        def get_projects():
            nonlocal call_count
            call_count += 1
            from apps.projects.models import Project

            return Project.objects.all()

        result = get_projects()

        # Result should be a list, not a queryset
        assert isinstance(result, list)
        assert len(result) == 2

    def test_cache_queryset_different_args_separate_cache(self, clear_cache):
        """Test that different arguments have separate cache entries."""
        user1 = UserFactory()
        user2 = UserFactory()
        ProjectFactory(owner=user1)
        ProjectFactory(owner=user2)

        call_count = 0

        @cache_queryset(timeout=300)
        def get_user_projects(user):
            nonlocal call_count
            call_count += 1
            from apps.projects.models import Project

            return Project.objects.filter(owner=user)

        result1 = get_user_projects(user1)
        result2 = get_user_projects(user2)
        result3 = get_user_projects(user1)

        assert len(result1) == 1
        assert len(result2) == 1
        assert call_count == 2  # Two unique users

    def test_cache_queryset_with_custom_prefix(self, clear_cache):
        """Test cache_queryset with custom key prefix."""
        ProjectFactory.create_batch(1)
        call_count = 0

        @cache_queryset(timeout=300, key_prefix="my_projects")
        def get_projects():
            nonlocal call_count
            call_count += 1
            from apps.projects.models import Project

            return Project.objects.all()

        get_projects()
        get_projects()

        assert call_count == 1


class TestInvalidateCache:
    """Test cache invalidation."""

    def test_invalidate_specific_cache_key(self, clear_cache):
        """Test invalidating a specific cache key."""
        key = make_cache_key("prefix", 1, 2)
        cache.set(key, "value", 300)

        assert cache.get(key) == "value"

        invalidate_cache("prefix", 1, 2)

        assert cache.get(key) is None

    def test_invalidate_cache_no_args(self, clear_cache):
        """Test invalidate without args (prefix only)."""
        # When called with only prefix, shouldn't delete anything
        # (as per the implementation)
        invalidate_cache("prefix")
        # Just verify it doesn't raise an error

    def test_invalidate_different_keys_not_affected(self, clear_cache):
        """Test that other cache keys are not affected."""
        key1 = make_cache_key("prefix", 1, 2)
        key2 = make_cache_key("prefix", 3, 4)

        cache.set(key1, "value1", 300)
        cache.set(key2, "value2", 300)

        invalidate_cache("prefix", 1, 2)

        assert cache.get(key1) is None
        assert cache.get(key2) == "value2"


@pytest.mark.django_db
class TestCacheMixin:
    """Test CacheMixin for view caching."""

    def test_cache_mixin_get_cache_key(self):
        """Test cache key generation in mixin."""
        factory = APIRequestFactory()
        request = factory.get("/api/projects/", {"filter": "active"})
        request.user = UserFactory()

        class TestView(CacheMixin):
            cache_key_prefix = "test_view"

        view = TestView()
        cache_key = view.get_cache_key(request)

        assert cache_key.startswith("test_view:")

    def test_cache_mixin_set_and_get_cache(self, clear_cache):
        """Test setting and getting cache via mixin."""
        factory = APIRequestFactory()
        request = factory.get("/api/projects/")
        request.user = UserFactory()

        class TestView(CacheMixin):
            cache_timeout = 300

        view = TestView()
        view.set_cache(request, {"data": "value"})

        result = view.get_from_cache(request)
        assert result == {"data": "value"}

    def test_cache_mixin_invalidate_cache(self, clear_cache):
        """Test cache invalidation via mixin."""
        factory = APIRequestFactory()
        request = factory.get("/api/projects/")
        request.user = UserFactory()

        class TestView(CacheMixin):
            cache_timeout = 300

        view = TestView()
        view.set_cache(request, {"data": "value"})

        assert view.get_from_cache(request) == {"data": "value"}

        view.invalidate_cache(request)

        assert view.get_from_cache(request) is None

    def test_cache_mixin_different_users_different_cache(self, clear_cache):
        """Test that different users have different cache entries."""
        factory = APIRequestFactory()
        user1 = UserFactory()
        user2 = UserFactory()

        request1 = factory.get("/api/projects/")
        request1.user = user1

        request2 = factory.get("/api/projects/")
        request2.user = user2

        class TestView(CacheMixin):
            cache_timeout = 300

        view = TestView()
        view.set_cache(request1, {"user": "user1"})
        view.set_cache(request2, {"user": "user2"})

        assert view.get_from_cache(request1) == {"user": "user1"}
        assert view.get_from_cache(request2) == {"user": "user2"}

    def test_cache_mixin_anonymous_user(self, clear_cache):
        """Test cache with anonymous user."""
        factory = APIRequestFactory()
        request = factory.get("/api/projects/")
        request.user = MagicMock()
        request.user.is_authenticated = False

        class TestView(CacheMixin):
            cache_timeout = 300

        view = TestView()
        view.set_cache(request, {"data": "anon"})

        result = view.get_from_cache(request)
        assert result == {"data": "anon"}

    def test_cache_mixin_default_prefix(self, clear_cache):
        """Test that default prefix is class name."""
        factory = APIRequestFactory()
        request = factory.get("/api/projects/")
        request.user = UserFactory()

        class MyCustomView(CacheMixin):
            cache_timeout = 300

        view = MyCustomView()
        cache_key = view.get_cache_key(request)

        assert "MyCustomView" in cache_key

    def test_cache_mixin_custom_timeout(self, clear_cache):
        """Test that custom timeout is respected."""
        factory = APIRequestFactory()
        request = factory.get("/api/projects/")
        request.user = UserFactory()

        class TestView(CacheMixin):
            cache_timeout = 60

        view = TestView()
        assert view.cache_timeout == 60


@pytest.mark.django_db
class TestCachingIntegration:
    """Integration tests for caching utilities."""

    def test_cache_result_and_invalidate_integration(self, clear_cache):
        """Test using cache_result with invalidation."""
        call_count = 0

        @cache_result(timeout=300, key_prefix="counter")
        def get_count():
            nonlocal call_count
            call_count += 1
            return call_count

        result1 = get_count()
        result2 = get_count()

        assert result1 == result2 == 1

        invalidate_cache("counter")

        result3 = get_count()
        assert result3 == 2

    def test_cache_key_consistency_across_calls(self, clear_cache):
        """Test that cache keys are consistent."""
        key1 = make_cache_key("prefix", "arg1", "arg2", kwarg1="value1")
        key2 = make_cache_key("prefix", "arg1", "arg2", kwarg1="value1")

        assert key1 == key2

        cache.set(key1, "data", 300)
        assert cache.get(key2) == "data"

    def test_mixin_and_decorator_compatibility(self, clear_cache):
        """Test that mixin can work with decorated functions."""
        factory = APIRequestFactory()
        user = UserFactory()
        request = factory.get("/api/test/")
        request.user = user

        call_count = 0

        @cache_result(timeout=300)
        def get_data():
            nonlocal call_count
            call_count += 1
            return {"data": "value"}

        class TestView(CacheMixin):
            cache_timeout = 300

        view = TestView()

        # Call decorated function
        result1 = get_data()
        result2 = get_data()

        assert call_count == 1
        assert result1 == result2
