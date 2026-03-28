# Performance Optimization Guide

## Overview

This guide covers performance optimization strategies and best practices for the Expense Tracker API.

## Table of Contents

1. [Database Optimization](#database-optimization)
2. [Caching Strategies](#caching-strategies)
3. [Query Optimization](#query-optimization)
4. [API Performance](#api-performance)
5. [Monitoring & Profiling](#monitoring--profiling)
6. [Production Deployment](#production-deployment)

---

## Database Optimization

### Connection Pooling

The application uses connection pooling to reuse database connections:

```python
# settings/base.py
DATABASES = {
    "default": {
        "CONN_MAX_AGE": 600,  # Reuse connections for 10 minutes
        "OPTIONS": {
            "connect_timeout": 10,
            "options": "-c statement_timeout=30000",  # 30s timeout
        },
    }
}
```

### Query Optimization

#### Use select_related() for Foreign Keys

```python
# ❌ Bad - N+1 queries
transactions = Transaction.objects.all()
for transaction in transactions:
    print(transaction.category.name)  # Extra query per transaction

# ✅ Good - Single query
transactions = Transaction.objects.select_related('category', 'created_by')
for transaction in transactions:
    print(transaction.category.name)  # No extra queries
```

#### Use prefetch_related() for Reverse Relations

```python
# ❌ Bad - Multiple queries for related objects
projects = Project.objects.all()
for project in projects:
    transactions = project.transactions.all()  # Extra query per project

# ✅ Good - Single query with prefetch
projects = Project.objects.prefetch_related('transactions')
for project in projects:
    transactions = project.transactions.all()  # No extra queries
```

#### Use only() and defer() to Limit Fields

```python
# ❌ Bad - Fetches all fields
users = User.objects.all()

# ✅ Good - Fetch only needed fields
users = User.objects.only('id', 'email', 'first_name')

# ✅ Good - Defer large fields
transactions = Transaction.objects.defer('notes', 'description')
```

### Database Indexing

Ensure frequently queried fields have indexes:

```python
class Transaction(models.Model):
    # ...
    class Meta:
        indexes = [
            # Index for filtering by project and date
            models.Index(fields=['project', 'date']),
            # Index for filtering by project and category
            models.Index(fields=['project', 'category']),
            # Index for filtering by created_by
            models.Index(fields=['created_by']),
        ]
```

### Batch Operations

Use bulk operations for large inserts/updates:

```python
# ❌ Bad - Multiple database calls
for data in large_dataset:
    Transaction.objects.create(**data)

# ✅ Good - Single batch insert
transactions = [Transaction(**data) for data in large_dataset]
Transaction.objects.bulk_create(transactions, batch_size=1000)

# ✅ Good - Batch update
Transaction.objects.filter(amount__gt=1000).update(flagged=True)
```

---

## Caching Strategies

### Using the Cache Decorator

```python
from apps.utils import cache_result

@cache_result(timeout=3600, key_prefix="expensive_calculation")
def calculate_summary(project_id, start_date, end_date):
    """Results will be cached for 1 hour."""
    # Expensive calculation
    return summary_data
```

### Caching API View Results

```python
from apps.utils import CacheMixin
from rest_framework import generics

class ProjectSummaryView(CacheMixin, generics.RetrieveAPIView):
    """View with automatic caching."""

    cache_timeout = 3600  # Cache for 1 hour
    cache_key_prefix = "project_summary"

    def get(self, request, *args, **kwargs):
        # Automatically caches response
        return super().get(request, *args, **kwargs)
```

### Manual Cache Management

```python
from django.core.cache import cache
from apps.utils import make_cache_key

# Set cache
cache_key = make_cache_key("report:monthly", project_id=123, month=3, year=2026)
cache.set(cache_key, report_data, timeout=3600)

# Get from cache
cached_report = cache.get(cache_key)

# Invalidate cache
cache.delete(cache_key)

# Clear all cache
cache.clear()
```

### Cache Invalidation

Invalidate cache when data changes:

```python
from apps.utils import invalidate_cache

def create_transaction(project_id, **kwargs):
    transaction = Transaction.objects.create(**kwargs)

    # Invalidate relevant caches
    invalidate_cache("report:monthly", project_id=project_id)
    invalidate_cache("project_summary", project_id=project_id)

    return transaction
```

### Cache Warming

Pre-populate cache for frequently accessed data:

```python
def warm_cache_for_project(project_id):
    """Warm cache with frequently accessed data."""
    from apps.utils import cache_result

    # Pre-calculate and cache
    summary = calculate_summary(project_id)
    breakdown = get_category_breakdown(project_id)
    trends = get_trends(project_id)

    # Cache results
    cache.set(f"summary:{project_id}", summary, 3600)
    cache.set(f"breakdown:{project_id}", breakdown, 3600)
    cache.set(f"trends:{project_id}", trends, 3600)
```

---

## Query Optimization

### Monitoring Queries

Use the QueryCounterContext to identify N+1 queries:

```python
from apps.utils import QueryCounterContext

with QueryCounterContext() as counter:
    # Your code here
    expensive_operation()

print(f"Executed {counter.count} queries in {counter.time:.2f}ms")
```

### Profiling Performance

Use the PerformanceTimer for detailed timing:

```python
from apps.utils import PerformanceTimer

with PerformanceTimer("operation_name", threshold_ms=500):
    # Your code here
    expensive_operation()

# Logs warning if execution exceeds threshold
```

### Monitoring Decorator

Use decorator for automatic query monitoring:

```python
from apps.utils import monitor_queries

@monitor_queries(threshold=10)
def fetch_user_projects(user):
    """Logs warning if more than 10 queries executed."""
    return Project.objects.filter(owner=user).prefetch_related('members')
```

---

## API Performance

### Pagination Best Practices

```python
# Always paginate large result sets
class ProjectListView(generics.ListAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    pagination_class = PageNumberPagination
    page_size = 50  # Reasonable default
```

### Response Serialization

```python
# ❌ Bad - Includes unnecessary fields
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'  # Includes all fields

# ✅ Good - Only needed fields
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'id', 'amount', 'date', 'category', 'description'
        ]
```

### Eager Loading in ViewSets

```python
class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        """Optimize queries for the view."""
        queryset = Transaction.objects.select_related(
            'category', 'created_by', 'project'
        ).prefetch_related('documents')

        # Filter by project if provided
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        return queryset
```

### Response Compression

Add compression middleware to settings:

```python
# settings/production.py
MIDDLEWARE += [
    'django.middleware.gzip.GZipMiddleware',  # Compress responses
]
```

---

## Monitoring & Profiling

### Get Query Statistics

```python
from apps.utils import DatabaseMetrics

# In development/testing
metrics = DatabaseMetrics.get_query_stats()
print(f"Total queries: {metrics['total_queries']}")
print(f"Total time: {metrics['total_time_ms']}ms")
print(f"Average time: {metrics['average_time_ms']:.2f}ms")
```

### Identify Slow Queries

```python
from apps.utils import get_slow_queries, log_slow_queries

# Find slow queries (>500ms)
slow_queries = get_slow_queries(time_threshold_ms=500)

# Log all slow queries
log_slow_queries(time_threshold_ms=500)
```

### Performance Profiling Decorator

```python
from apps.utils import profile_performance

@profile_performance(threshold_ms=1000)
def slow_operation():
    """Logs warning if execution exceeds 1 second."""
    # Your code here
    pass
```

---

## Production Deployment

### Database Configuration

```python
# settings/production.py
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        # ... connection info ...
        "CONN_MAX_AGE": 600,  # Connection pooling
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}
```

### Gunicorn Configuration

```bash
# Run with multiple workers
gunicorn config.wsgi:application \
    --workers 4 \
    --worker-class sync \
    --bind 0.0.0.0:8000 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
```

### Redis Configuration

```python
# settings/production.py
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://redis-server:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
            },
        },
        "KEY_PREFIX": "expense_tracker",
        "TIMEOUT": 3600,  # Default 1 hour
    }
}
```

### Celery Configuration

```python
# settings/production.py
CELERY_BROKER_URL = "redis://redis-server:6379/1"
CELERY_RESULT_BACKEND = "redis://redis-server:6379/1"
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Don't prefetch many tasks
CELERY_WORKER_CONCURRENCY = 4  # Number of concurrent tasks
```

---

## Performance Checklist

### Before Production

- [ ] Database indexes created for frequently queried fields
- [ ] select_related() and prefetch_related() used appropriately
- [ ] API endpoints are paginated
- [ ] Caching is configured and working
- [ ] Slow queries have been identified and optimized
- [ ] Response serializers only include necessary fields
- [ ] Gunicorn is configured with appropriate worker count
- [ ] Redis is running and configured
- [ ] Connection pooling is enabled
- [ ] Query monitoring is in place

### Monitoring

- [ ] Database query metrics tracked
- [ ] API response times monitored
- [ ] Cache hit/miss rates tracked
- [ ] Slow query logs reviewed regularly
- [ ] Error rates monitored
- [ ] Resource utilization (CPU, memory, disk) monitored

### Optimization

- [ ] Regular query analysis performed
- [ ] Cache strategies evaluated and adjusted
- [ ] Database indices optimized
- [ ] Bulk operations used for large data imports
- [ ] Pagination limits adjusted based on usage
- [ ] Response serializers refined

---

## Tools & Resources

### Django ORM Optimization

```python
from django.db.models import Prefetch, Q, Count, Sum

# Complex prefetch
prefetch = Prefetch(
    'transactions',
    queryset=Transaction.objects.filter(
        transaction_type='expense'
    ).select_related('category')
)
projects = Project.objects.prefetch_related(prefetch)

# Aggregation
summary = Transaction.objects.aggregate(
    total_income=Sum('amount', filter=Q(transaction_type='income')),
    total_expense=Sum('amount', filter=Q(transaction_type='expense')),
    count=Count('id'),
)
```

### Useful Commands

```bash
# Enable query logging
python manage.py shell
>>> from django.conf import settings
>>> settings.DEBUG = True
>>> from django.db import connection
>>> # Run your code
>>> print(connection.queries)

# Check query plans (PostgreSQL)
EXPLAIN ANALYZE SELECT * FROM transactions WHERE project_id = '...';

# Monitor cache hit/miss
redis-cli INFO stats
```

### External Tools

- **django-debug-toolbar**: Visual debugging and query analysis
- **django-extensions**: Enhanced Django shell with query logging
- **py-spy**: Python profiler for performance bottlenecks
- **locust**: Load testing for API performance
- **pgBadger**: PostgreSQL log analyzer

---

## Benchmarking

### Example Performance Targets

- **API response time**: < 200ms for 95th percentile
- **Database query**: < 50ms per query average
- **Cache hit rate**: > 80% for frequently accessed endpoints
- **Concurrent users**: 100+ with normal performance
- **Max memory per worker**: < 256MB

### Load Testing

```python
# Simple performance test with pytest
@pytest.mark.benchmark
def test_list_transactions_performance(benchmark, auth_client):
    """Benchmark transaction list endpoint."""
    result = benchmark(
        auth_client.get,
        '/api/v1/transactions/'
    )
    assert result.status_code == 200
```

---

## Continuous Optimization

1. **Monitor continuously** - Track metrics in production
2. **Identify bottlenecks** - Use profiling and monitoring
3. **Optimize incrementally** - Make targeted improvements
4. **Test thoroughly** - Verify improvements don't break features
5. **Document changes** - Keep optimization notes for team

---

## Support

For performance issues or optimization questions, check:
- Django documentation
- Database-specific guides (PostgreSQL docs)
- DRF optimization guide
- Redis documentation
