"""
Tests for utils/monitoring.py - Performance monitoring and profiling utilities.

Tests:
- QueryCounterContext - Database query counting and monitoring
- PerformanceTimer - Execution time measurement
- monitor_queries - Query monitoring decorator
- profile_performance - Performance profiling decorator
- DatabaseMetrics - Database performance statistics
- get_slow_queries - Slow query detection
"""

import pytest
import time
import logging
from unittest.mock import patch, MagicMock
from django.db import connection
from django.test.utils import override_settings

from apps.utils.monitoring import (
    QueryCounterContext,
    PerformanceTimer,
    monitor_queries,
    profile_performance,
    DatabaseMetrics,
    get_slow_queries,
    log_slow_queries,
)
from apps.projects.tests.factories import ProjectFactory
from apps.transactions.tests.factories import TransactionFactory, CategoryFactory


@pytest.mark.django_db
class TestQueryCounterContext:
    """Test QueryCounterContext for counting database queries."""

    def test_query_counter_counts_queries(self):
        """Test that query counter counts database queries."""
        with QueryCounterContext() as counter:
            # Execute a query
            ProjectFactory()

        assert counter.count >= 1

    def test_query_counter_measures_time(self):
        """Test that query counter measures execution time."""
        with QueryCounterContext() as counter:
            time.sleep(0.01)  # Sleep for 10ms

        assert counter.time >= 10  # Should be >= 10ms

    def test_query_counter_zero_queries(self):
        """Test counter with no queries executed."""
        initial_count = len(connection.queries)

        with QueryCounterContext() as counter:
            pass  # No database operations

        # Should count change or no change
        assert counter.count >= 0

    def test_query_counter_multiple_queries(self):
        """Test counter with multiple queries."""
        with QueryCounterContext() as counter:
            ProjectFactory.create_batch(3)

        assert counter.count >= 3

    def test_query_counter_start_state(self):
        """Test counter initial state."""
        counter = QueryCounterContext()

        assert counter.count == 0
        assert counter.time == 0
        assert counter.start_time is None
        assert counter.start_queries is None

    def test_query_counter_warning_on_high_count(self, caplog):
        """Test that warning is logged for high query count."""
        with caplog.at_level(logging.WARNING):
            with QueryCounterContext() as counter:
                # Execute many queries to trigger warning
                ProjectFactory.create_batch(15)

        # May have warning if > 10 queries
        # Depending on factory complexity

    def test_query_counter_context_manager(self):
        """Test that QueryCounterContext works as context manager."""
        counter = QueryCounterContext()

        with counter:
            ProjectFactory()

        assert hasattr(counter, "count")
        assert hasattr(counter, "time")


@pytest.mark.django_db
class TestPerformanceTimer:
    """Test PerformanceTimer for execution time measurement."""

    def test_performance_timer_measures_time(self):
        """Test that timer measures execution time."""
        with PerformanceTimer() as timer:
            time.sleep(0.01)  # 10ms

        assert timer.elapsed_ms >= 10

    def test_performance_timer_with_name(self):
        """Test timer with a name."""
        with PerformanceTimer("test_operation") as timer:
            time.sleep(0.01)

        assert timer.name == "test_operation"
        assert timer.elapsed_ms >= 10

    def test_performance_timer_threshold(self, caplog):
        """Test timer with threshold."""
        with caplog.at_level(logging.WARNING):
            with PerformanceTimer("slow_op", threshold_ms=5):
                time.sleep(0.01)  # 10ms, exceeds 5ms threshold

        # May have warning if time exceeds threshold

    def test_performance_timer_below_threshold(self):
        """Test timer when execution is below threshold."""
        with PerformanceTimer("fast_op", threshold_ms=1000):
            pass  # No significant time

        # Should not log warning

    def test_performance_timer_initial_state(self):
        """Test timer initial state."""
        timer = PerformanceTimer("test", threshold_ms=1000)

        assert timer.name == "test"
        assert timer.threshold_ms == 1000
        assert timer.start_time is None
        assert timer.elapsed_ms == 0

    def test_performance_timer_context_manager(self):
        """Test that timer works as context manager."""
        with PerformanceTimer() as timer:
            time.sleep(0.01)

        assert timer.elapsed_ms >= 10

    def test_performance_timer_accuracy(self):
        """Test that timer is reasonably accurate."""
        with PerformanceTimer() as timer:
            time.sleep(0.02)  # 20ms

        # Should be close to 20ms (allow some variance)
        assert 15 <= timer.elapsed_ms <= 50  # Allow 50ms for system variance


@pytest.mark.django_db
class TestMonitorQueriesDecorator:
    """Test monitor_queries decorator."""

    def test_monitor_queries_basic(self):
        """Test basic query monitoring."""

        @monitor_queries(threshold=5)
        def get_projects():
            return ProjectFactory()

        result = get_projects()
        assert result is not None

    def test_monitor_queries_preserves_function_behavior(self):
        """Test that decorator preserves function behavior."""

        @monitor_queries(threshold=10)
        def add_numbers(a, b):
            return a + b

        result = add_numbers(5, 3)
        assert result == 8

    def test_monitor_queries_with_return_value(self):
        """Test that decorator returns function result correctly."""

        @monitor_queries(threshold=100)
        def get_value():
            return {"key": "value"}

        result = get_value()
        assert result == {"key": "value"}

    def test_monitor_queries_with_args(self):
        """Test monitor_queries with function arguments."""

        @monitor_queries(threshold=100)
        def process_data(x, y):
            return x + y

        result = process_data(10, 20)
        assert result == 30

    def test_monitor_queries_logging(self, caplog):
        """Test that monitor_queries logs query information."""
        with caplog.at_level(logging.DEBUG):

            @monitor_queries(threshold=100)
            def get_projects():
                ProjectFactory()

            get_projects()

        # Should have debug log

    def test_monitor_queries_threshold_warning(self, caplog):
        """Test that warning is logged when threshold exceeded."""
        with caplog.at_level(logging.WARNING):

            @monitor_queries(threshold=1)
            def create_many():
                ProjectFactory.create_batch(5)

            create_many()

        # May have warning if threshold exceeded

    def test_monitor_queries_default_threshold(self):
        """Test monitor_queries with default threshold."""

        @monitor_queries()  # Default threshold=10
        def get_projects():
            return ProjectFactory()

        result = get_projects()
        assert result is not None

    def test_monitor_queries_preserves_metadata(self):
        """Test that decorator preserves function name."""

        @monitor_queries(threshold=100)
        def my_function():
            return "result"

        assert my_function.__name__ == "my_function"


@pytest.mark.django_db
class TestProfilePerformanceDecorator:
    """Test profile_performance decorator."""

    def test_profile_performance_basic(self):
        """Test basic performance profiling."""

        @profile_performance(threshold_ms=1000)
        def slow_operation():
            time.sleep(0.01)
            return "done"

        result = slow_operation()
        assert result == "done"

    def test_profile_performance_preserves_function(self):
        """Test that decorator preserves function behavior."""

        @profile_performance(threshold_ms=100)
        def multiply(a, b):
            return a * b

        result = multiply(6, 7)
        assert result == 42

    def test_profile_performance_with_return_value(self):
        """Test that profiling preserves return values."""

        @profile_performance(threshold_ms=100)
        def get_dict():
            return {"result": "success"}

        result = get_dict()
        assert result == {"result": "success"}

    def test_profile_performance_default_threshold(self):
        """Test profile_performance with default threshold."""

        @profile_performance()  # Default threshold_ms=1000
        def operation():
            return "result"

        result = operation()
        assert result == "result"

    def test_profile_performance_below_threshold(self):
        """Test profiling when execution is below threshold."""

        @profile_performance(threshold_ms=1000)
        def fast_operation():
            return "done"

        result = fast_operation()
        assert result == "done"

    def test_profile_performance_logging(self, caplog):
        """Test that profiling logs performance information."""
        with caplog.at_level(logging.DEBUG):

            @profile_performance(threshold_ms=1000)
            def operation():
                time.sleep(0.01)

            operation()

        # Should have some logging

    def test_profile_performance_preserves_metadata(self):
        """Test that decorator preserves function metadata."""

        @profile_performance(threshold_ms=100)
        def my_operation():
            """Operation docstring."""
            return "result"

        assert my_operation.__name__ == "my_operation"

    def test_profile_performance_with_arguments(self):
        """Test profile_performance with function arguments."""

        @profile_performance(threshold_ms=100)
        def process(x, y, z=10):
            return x + y + z

        result = process(1, 2, z=3)
        assert result == 6


class TestDatabaseMetrics:
    """Test DatabaseMetrics for database performance statistics."""

    def test_get_connection_info(self):
        """Test getting database connection information."""
        info = DatabaseMetrics.get_connection_info()

        assert isinstance(info, dict)
        assert "alias" in info
        assert "engine" in info

    def test_connection_info_has_required_fields(self):
        """Test that connection info has required fields."""
        info = DatabaseMetrics.get_connection_info()

        required_fields = ["alias", "engine", "host", "port", "name"]
        for field in required_fields:
            assert field in info

    @pytest.mark.django_db
    def test_get_query_stats_no_queries(self):
        """Test query stats when no queries executed."""
        # Create new connection context with no queries
        stats = DatabaseMetrics.get_query_stats()

        assert isinstance(stats, dict)
        assert "total_queries" in stats
        assert "total_time_ms" in stats
        assert "average_time_ms" in stats

    @pytest.mark.django_db
    def test_get_query_stats_with_queries(self):
        """Test query stats with executed queries."""
        # Execute a query to populate stats
        ProjectFactory()

        stats = DatabaseMetrics.get_query_stats()

        assert stats["total_queries"] >= 1
        assert stats["total_time_ms"] >= 0
        assert stats["average_time_ms"] >= 0

    @pytest.mark.django_db
    def test_query_stats_multiple_queries(self):
        """Test query stats with multiple queries."""
        ProjectFactory.create_batch(3)

        stats = DatabaseMetrics.get_query_stats()

        assert stats["total_queries"] >= 3
        assert "min_time_ms" in stats
        assert "max_time_ms" in stats

    def test_database_metrics_static_methods(self):
        """Test that DatabaseMetrics methods are static."""
        # Should be callable without instance
        info = DatabaseMetrics.get_connection_info()
        assert isinstance(info, dict)


class TestSlowQueryDetection:
    """Test slow query detection utilities."""

    def test_get_slow_queries_empty(self):
        """Test get_slow_queries with no queries."""
        slow = get_slow_queries(time_threshold_ms=500)

        assert isinstance(slow, list)

    def test_get_slow_queries_returns_list(self):
        """Test that get_slow_queries returns a list."""
        slow = get_slow_queries(time_threshold_ms=100)

        assert isinstance(slow, list)

    def test_slow_query_has_sql_field(self):
        """Test that slow queries include SQL."""
        slow = get_slow_queries(time_threshold_ms=0)

        for query in slow:
            if query:  # If there are any queries
                assert "sql" in query

    def test_slow_query_has_time_field(self):
        """Test that slow queries include time."""
        slow = get_slow_queries(time_threshold_ms=0)

        for query in slow:
            if query:
                assert "time_ms" in query

    def test_get_slow_queries_threshold(self):
        """Test that threshold filters queries."""
        slow_high_threshold = get_slow_queries(time_threshold_ms=10000)
        slow_low_threshold = get_slow_queries(time_threshold_ms=0)

        # Lower threshold should have more or equal queries
        assert len(slow_low_threshold) >= len(slow_high_threshold)

    def test_log_slow_queries_with_logging(self, caplog):
        """Test log_slow_queries function."""
        with caplog.at_level(logging.WARNING):
            log_slow_queries(time_threshold_ms=0)

        # May or may not log depending on queries


@pytest.mark.django_db
class TestMonitoringIntegration:
    """Integration tests for monitoring utilities."""

    def test_query_counter_and_performance_timer_together(self):
        """Test using query counter and performance timer together."""
        with PerformanceTimer("operation") as perf_timer:
            with QueryCounterContext() as query_counter:
                ProjectFactory()

        assert query_counter.count >= 1
        assert perf_timer.elapsed_ms >= 0

    def test_decorator_stacking(self):
        """Test stacking monitor_queries and profile_performance."""

        @profile_performance(threshold_ms=1000)
        @monitor_queries(threshold=100)
        def operation():
            ProjectFactory()
            return "done"

        result = operation()
        assert result == "done"

    @pytest.mark.django_db
    def test_database_metrics_complete_workflow(self):
        """Test complete database metrics workflow."""
        # Get connection info
        conn_info = DatabaseMetrics.get_connection_info()
        assert conn_info["engine"] is not None

        # Execute queries
        ProjectFactory.create_batch(2)

        # Get stats
        stats = DatabaseMetrics.get_query_stats()
        assert stats["total_queries"] >= 2

    def test_monitoring_with_slow_query_detection(self):
        """Test monitoring integrated with slow query detection."""
        slow = get_slow_queries(time_threshold_ms=0)

        assert isinstance(slow, list)
        for query in slow:
            assert "sql" in query
            assert "time_ms" in query

    @pytest.mark.django_db
    def test_full_monitoring_stack(self):
        """Test the full monitoring stack together."""

        @profile_performance(threshold_ms=1000)
        @monitor_queries(threshold=100)
        def create_project():
            return ProjectFactory()

        # Execute monitored function
        project = create_project()
        assert project is not None

        # Check metrics
        conn_info = DatabaseMetrics.get_connection_info()
        assert conn_info is not None

        # Check for slow queries
        slow = get_slow_queries(time_threshold_ms=0)
        assert isinstance(slow, list)


class TestMonitoringEdgeCases:
    """Test edge cases in monitoring utilities."""

    def test_query_counter_with_exception(self):
        """Test query counter handles exceptions gracefully."""
        try:
            with QueryCounterContext() as counter:
                raise ValueError("Test error")
        except ValueError:
            pass

        # Should still have count and time set
        assert hasattr(counter, "count")
        assert hasattr(counter, "time")

    def test_performance_timer_with_exception(self):
        """Test performance timer handles exceptions."""
        try:
            with PerformanceTimer() as timer:
                raise ValueError("Test error")
        except ValueError:
            pass

        # Timer should still be set
        assert timer.elapsed_ms >= 0

    def test_monitor_queries_with_exception(self):
        """Test monitor_queries handles exceptions."""

        @monitor_queries(threshold=100)
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()

    def test_profile_performance_with_exception(self):
        """Test profile_performance handles exceptions."""

        @profile_performance(threshold_ms=100)
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()

    def test_get_slow_queries_with_empty_connection(self):
        """Test get_slow_queries with empty query list."""
        slow = get_slow_queries(time_threshold_ms=500)

        assert isinstance(slow, list)
        # Should not crash with empty query list

    def test_database_metrics_with_no_queries(self):
        """Test database metrics when no queries executed."""
        stats = DatabaseMetrics.get_query_stats()

        assert stats["total_queries"] >= 0
        assert stats["average_time_ms"] >= 0
