# Testing Patterns & Examples for Expense Tracker

## 1. Signal Testing Pattern

### Example: Activity Signals (apps/activity/signals.py)

The `signals.py` file contains 274 lines of Django signal handlers that log all model changes. Currently has ZERO tests.

#### Test Pattern (test_signals.py - NEW):

```python
import pytest
from django.db.models.signals import post_save
from apps.transactions.models import Transaction
from apps.activity.models import ActivityLog

@pytest.mark.django_db
def test_log_transaction_create(user, project):
    """Test that transaction creation is logged."""
    # Create a transaction
    transaction = Transaction.objects.create(
        project=project,
        created_by=user,
        description="Test transaction",
        amount=100.00,
        currency="USD",
        transaction_type="expense"
    )

    # Verify activity log was created
    log = ActivityLog.objects.get(object_id=transaction.id)
    assert log.action == ActivityLog.ActionType.CREATE
    assert log.content_type == "transaction"
    assert log.user == user
    assert "100.00" in log.description

@pytest.mark.django_db
def test_log_transaction_update(user, project, transaction):
    """Test that transaction updates are logged."""
    # Update the transaction
    transaction.description = "Updated description"
    transaction.save()

    # Verify update was logged
    logs = ActivityLog.objects.filter(object_id=transaction.id)
    assert logs.count() == 2  # Create + update

    update_log = logs.latest('created_at')
    assert update_log.action == ActivityLog.ActionType.UPDATE
```

---

## 2. Celery Task Testing Pattern

### Example: Budget Tasks (apps/budgets/tasks.py)

```python
import pytest
from unittest.mock import patch, MagicMock
from django.utils import timezone
from datetime import timedelta
from apps.budgets.models import Budget
from apps.budgets.tasks import check_budget_alerts

@pytest.mark.django_db
def test_check_budget_alerts_skips_inactive_budgets(project, user):
    """Test that inactive budget periods are skipped."""
    future_start = timezone.now().date() + timedelta(days=10)
    future_end = timezone.now().date() + timedelta(days=20)

    budget = Budget.objects.create(
        project=project,
        created_by=user,
        amount=1000.00,
        start_date=future_start,
        end_date=future_end,
        alert_enabled=True,
        alert_threshold=80
    )

    with patch('apps.budgets.tasks.send_budget_alert.delay') as mock_send:
        check_budget_alerts()
        mock_send.assert_not_called()

@pytest.mark.django_db
def test_check_budget_alerts_triggers_when_threshold_exceeded(project, user):
    """Test that alert is sent when spending exceeds threshold."""
    start = timezone.now().date() - timedelta(days=10)
    end = timezone.now().date() + timedelta(days=10)

    budget = Budget.objects.create(
        project=project,
        created_by=user,
        amount=1000.00,
        start_date=start,
        end_date=end,
        alert_enabled=True,
        alert_threshold=80
    )

    with patch('apps.budgets.tasks.send_budget_alert.delay') as mock_send:
        check_budget_alerts()
        mock_send.assert_called_once()
```

---

## 3. Middleware Testing Pattern

### Example: Security Middleware (apps/security/middleware.py)

```python
import pytest
from django.test import RequestFactory
from django.http import HttpResponse
from apps.security.middleware import SecurityHeadersMiddleware

@pytest.fixture
def rf():
    return RequestFactory()

@pytest.fixture
def get_response():
    def _get_response(request):
        return HttpResponse("OK")
    return _get_response

class TestSecurityHeadersMiddleware:
    def test_adds_content_security_policy(self, rf, get_response):
        """Test that CSP header is added."""
        middleware = SecurityHeadersMiddleware(get_response)
        request = rf.get('/')
        response = middleware(request)

        assert 'Content-Security-Policy' in response
        assert "default-src 'self'" in response['Content-Security-Policy']

    def test_adds_x_frame_options(self, rf, get_response):
        """Test X-Frame-Options (clickjacking protection)."""
        middleware = SecurityHeadersMiddleware(get_response)
        request = rf.get('/')
        response = middleware(request)

        assert response['X-Frame-Options'] == 'DENY'
```

---

## 4. Validator Testing Pattern

### Example: Security Validators (apps/security/validators.py)

```python
import pytest
from django.core.exceptions import ValidationError
from apps.security.validators import validate_password_complexity

class TestPasswordComplexity:
    def test_requires_uppercase(self):
        """Test password must contain uppercase."""
        with pytest.raises(ValidationError):
            validate_password_complexity("password123")

    def test_accepts_valid_password(self):
        """Test valid password passes."""
        validate_password_complexity("ValidPassword123")
```

---

## 5. Utils Testing Pattern

### Example: Caching Utilities (apps/utils/caching.py)

```python
import pytest
from django.core.cache import cache
from django.test.utils import override_settings
from apps.utils.caching import cache_result

@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
})
class TestCacheDecorator:
    @pytest.mark.django_db
    def test_cache_result_caches_result(self):
        """Test that decorated function result is cached."""
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

        # Second call (should use cache)
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Not incremented
```

---

## 6. Health Check Testing Pattern

### Example: Health Checks (apps/health/views.py)

```python
import pytest
from rest_framework.test import APIClient
from django.urls import reverse

@pytest.fixture
def client():
    return APIClient()

class TestHealthChecks:
    def test_database_health_check(self, client):
        """Test database connectivity check."""
        response = client.get(reverse('health:db-check'))
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'

    def test_overall_health_check(self, client):
        """Test overall system health."""
        response = client.get(reverse('health:overall'))
        assert response.status_code == 200
        data = response.json()
        assert 'database' in data
        assert 'cache' in data
```

---

## Summary: Testing Patterns to Use

1. **Signals**: Import signal, create object, verify log created
2. **Tasks**: Mock external calls (email, delays), verify inputs/outputs
3. **Middleware**: Use RequestFactory, verify headers/responses
4. **Validators**: Test both valid and invalid inputs
5. **Utils**: Test decorators, cache behavior, performance metrics
6. **Health Checks**: Use APIClient, verify endpoints and response structure

All tests should:
- Use `@pytest.mark.django_db` when needed
- Mock external services (email, Celery delays)
- Test both success and failure cases
- Include edge cases
- Be isolated and repeatable
