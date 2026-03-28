# Testing Patterns & Examples for Expense Tracker

## 1. Signal Testing Pattern

### Example: Activity Signals (apps/activity/signals.py)

The `signals.py` file contains 274 lines of Django signal handlers that log all model changes. Currently has ZERO tests.

#### What Needs Testing:

```python
# Example from activity/signals.py

@receiver(post_save, sender=Transaction)
def log_transaction(sender, instance, created, update_fields=None, **kwargs):
    """Log transaction creation or update."""
    if created:
        action = ActivityLog.ActionType.CREATE
        description = f"Created transaction '{instance.description}' for {instance.amount} {instance.currency}"
    else:
        action = ActivityLog.ActionType.UPDATE
        description = f"Updated transaction '{instance.description}'"

    ActivityLog.objects.create(
        user=instance.created_by,
        project=instance.project,
        action=action,
        content_type="transaction",
        object_id=instance.id,
        description=description,
        metadata={
            "transaction_type": instance.transaction_type,
            "amount": str(instance.amount),
            "currency": instance.currency,
        },
    )
```

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

The `tasks.py` file has Celery tasks for sending budget alerts and calculating spent amounts. Currently has only 15 tests for 110 lines.

#### What Needs Testing:

```python
@shared_task
def check_budget_alerts():
    """Check all active budgets and send alerts if spending exceeds threshold."""
    budgets = Budget.objects.filter(alert_enabled=True).select_related(
        "project", "category", "created_by"
    )

    for budget in budgets:
        today = timezone.now().date()
        if today < budget.start_date or today > budget.end_date:
            continue

        spent = _calculate_spent(budget)

        if budget.amount > 0:
            percentage_used = (spent / budget.amount) * 100
        else:
            percentage_used = 0

        if percentage_used >= budget.alert_threshold:
            send_budget_alert.delay(
                budget_id=str(budget.id),
                spent=float(spent),
                allocated=float(budget.amount),
                percentage_used=float(percentage_used),
            )
```

#### Test Pattern (test_tasks.py - EXPAND):

```python
import pytest
from unittest.mock import patch, MagicMock
from django.utils import timezone
from datetime import timedelta, date
from apps.budgets.models import Budget
from apps.budgets.tasks import check_budget_alerts, send_budget_alert, _calculate_spent
from apps.transactions.models import Transaction

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
        # Should not be called for future budgets
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
    
    # Create transactions exceeding threshold
    for i in range(9):
        Transaction.objects.create(
            project=project,
            created_by=user,
            amount=100.00,
            currency="USD",
            transaction_type="expense",
            date=timezone.now().date()
        )
    
    with patch('apps.budgets.tasks.send_budget_alert.delay') as mock_send:
        check_budget_alerts()
        mock_send.assert_called_once()
        
        call_args = mock_send.call_args[1]
        assert call_args['percentage_used'] >= 80.0

@pytest.mark.django_db
def test_calculate_spent_by_category(project, user):
    """Test that _calculate_spent correctly filters by category."""
    category = Category.objects.create(name="Food")
    other_category = Category.objects.create(name="Transport")
    
    budget = Budget.objects.create(
        project=project,
        created_by=user,
        amount=500.00,
        category=category,
        start_date=timezone.now().date() - timedelta(days=5),
        end_date=timezone.now().date() + timedelta(days=5)
    )
    
    # Create transactions in multiple categories
    Transaction.objects.create(
        project=project,
        created_by=user,
        amount=100.00,
        category=category,
        transaction_type="expense"
    )
    
    Transaction.objects.create(
        project=project,
        created_by=user,
        amount=200.00,
        category=other_category,
        transaction_type="expense"
    )
    
    spent = _calculate_spent(budget)
    # Should only count Food category
    assert spent == Decimal("100.00")

@pytest.mark.django_db
def test_send_budget_alert_email(project, user):
    """Test that budget alert email is sent correctly."""
    budget = Budget.objects.create(
        project=project,
        created_by=user,
        amount=1000.00,
        start_date=timezone.now().date()
    )
    
    with patch('apps.budgets.tasks.send_mail') as mock_send:
        send_budget_alert(
            budget_id=str(budget.id),
            spent=900.00,
            allocated=1000.00,
            percentage_used=90.0
        )
        
        mock_send.assert_called_once()
        call_args = mock_send.call_args
        
        # Verify email details
        assert call_args[1]['subject'] == f"Budget Alert: {project.name} - All Categories"
        assert user.email in call_args[1]['recipient_list']
        assert "90.0%" in call_args[1]['message']
        assert "$900.00" in call_args[1]['message']
```

---

## 3. Middleware Testing Pattern

### Example: Security Middleware (apps/security/middleware.py)

The `middleware.py` has 3 middleware classes with 130 lines. Currently has ZERO tests.

#### Test Pattern (test_middleware.py - NEW):

```python
import pytest
from django.test import RequestFactory
from django.http import HttpResponse
from apps.security.middleware import (
    SecurityHeadersMiddleware,
    IPWhitelistMiddleware,
    RateLimitHeadersMiddleware
)

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
    
    def test_adds_x_content_type_options(self, rf, get_response):
        """Test X-Content-Type-Options header."""
        middleware = SecurityHeadersMiddleware(get_response)
        request = rf.get('/')
        response = middleware(request)
        
        assert response['X-Content-Type-Options'] == 'nosniff'
    
    def test_adds_x_frame_options(self, rf, get_response):
        """Test X-Frame-Options (clickjacking protection)."""
        middleware = SecurityHeadersMiddleware(get_response)
        request = rf.get('/')
        response = middleware(request)
        
        assert response['X-Frame-Options'] == 'DENY'

class TestIPWhitelistMiddleware:
    @pytest.mark.django_db
    def test_allows_whitelisted_ip(self, rf, monkeypatch):
        """Test that whitelisted IPs are allowed."""
        monkeypatch.setattr(
            'django.conf.settings',
            type('Settings', (), {'ALLOWED_IPS': ['127.0.0.1']})()
        )
        
        def get_response(request):
            return HttpResponse("OK")
        
        middleware = IPWhitelistMiddleware(get_response)
        request = rf.get('/')
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        response = middleware(request)
        assert response.status_code == 200
    
    @pytest.mark.django_db
    def test_blocks_non_whitelisted_ip(self, rf, monkeypatch):
        """Test that non-whitelisted IPs are blocked."""
        monkeypatch.setattr(
            'django.conf.settings',
            type('Settings', (), {'ALLOWED_IPS': ['127.0.0.1']})()
        )
        
        def get_response(request):
            return HttpResponse("OK")
        
        middleware = IPWhitelistMiddleware(get_response)
        request = rf.get('/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        response = middleware(request)
        assert response.status_code == 403
    
    def test_parses_x_forwarded_for_header(self, rf):
        """Test that X-Forwarded-For header is parsed correctly."""
        def get_response(request):
            return HttpResponse("OK")
        
        middleware = IPWhitelistMiddleware(get_response)
        request = rf.get('/')
        request.META['HTTP_X_FORWARDED_FOR'] = '192.168.1.1, 10.0.0.1'
        
        ip = middleware.get_client_ip(request)
        assert ip == '192.168.1.1'
```

---

## 4. Validator Testing Pattern

### Example: Security Validators (apps/security/validators.py)

The `validators.py` has 10 custom validator functions. Currently has ZERO tests.

#### Test Pattern (test_validators.py - NEW):

```python
import pytest
from django.core.exceptions import ValidationError
from apps.security.validators import (
    validate_password_complexity,
    validate_email_domain,
    validate_no_special_chars,
    validate_unique_chars
)

class TestPasswordComplexity:
    def test_requires_uppercase(self):
        """Test password must contain uppercase."""
        with pytest.raises(ValidationError):
            validate_password_complexity("password123")
    
    def test_requires_lowercase(self):
        """Test password must contain lowercase."""
        with pytest.raises(ValidationError):
            validate_password_complexity("PASSWORD123")
    
    def test_requires_digit(self):
        """Test password must contain digit."""
        with pytest.raises(ValidationError):
            validate_password_complexity("Password")
    
    def test_requires_minimum_length(self):
        """Test password minimum length."""
        with pytest.raises(ValidationError):
            validate_password_complexity("Pwd1")
    
    def test_accepts_valid_password(self):
        """Test valid password passes."""
        # Should not raise
        validate_password_complexity("ValidPassword123")

class TestEmailDomainValidation:
    def test_blocks_suspicious_domains(self):
        """Test that suspicious email domains are blocked."""
        suspicious_domains = [
            "test@tempmail.com",
            "user@guerrillamail.com",
            "admin@mailinator.com"
        ]
        
        for email in suspicious_domains:
            with pytest.raises(ValidationError):
                validate_email_domain(email)
    
    def test_allows_legitimate_domains(self):
        """Test that legitimate domains are allowed."""
        valid_emails = [
            "user@gmail.com",
            "admin@company.com",
            "test@example.com"
        ]
        
        for email in valid_emails:
            # Should not raise
            validate_email_domain(email)
```

---

## 5. Utils Testing Pattern

### Example: Caching Utilities (apps/utils/caching.py)

The `caching.py` has cache decorators and utilities. Currently has ZERO tests.

#### Test Pattern (test_caching.py - NEW):

```python
import pytest
from django.core.cache import cache
from django.test.utils import override_settings
from apps.utils.caching import cache_result, invalidate_cache

@pytest.fixture
def clear_cache():
    cache.clear()
    yield
    cache.clear()

@override_settings(CACHES={
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
})
class TestCacheDecorator:
    @pytest.mark.django_db
    def test_cache_result_caches_result(self, clear_cache):
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
    
    @pytest.mark.django_db
    def test_cache_different_args(self, clear_cache):
        """Test that different arguments create different cache entries."""
        call_count = 0
        
        @cache_result(timeout=300)
        def compute(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        compute(5)
        compute(10)
        
        assert call_count == 2  # Different args, different cache
    
    @pytest.mark.django_db
    def test_cache_expiration(self, clear_cache):
        """Test that cache respects timeout."""
        call_count = 0
        
        @cache_result(timeout=0.1)  # 100ms
        def quick_expire(x):
            nonlocal call_count
            call_count += 1
            return x
        
        import time
        quick_expire(5)
        time.sleep(0.15)
        quick_expire(5)
        
        assert call_count == 2  # Cache expired

@pytest.mark.django_db
def test_invalidate_cache_clears_entries(clear_cache):
    """Test that cache invalidation works."""
    cache.set('test_key', 'test_value')
    assert cache.get('test_key') == 'test_value'
    
    invalidate_cache('test_key')
    assert cache.get('test_key') is None
```

---

## 6. Health Check Testing Pattern

### Example: Health Checks (apps/health/views.py)

The `views.py` has 12 health check methods. Currently has ZERO tests.

#### Test Pattern (test_api.py - NEW):

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
    
    def test_cache_health_check(self, client):
        """Test cache connectivity check."""
        response = client.get(reverse('health:cache-check'))
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'response_time_ms' in data
    
    def test_overall_health_check(self, client):
        """Test overall system health."""
        response = client.get(reverse('health:overall'))
        assert response.status_code == 200
        data = response.json()
        assert 'database' in data
        assert 'cache' in data
        assert 'timestamp' in data
    
    def test_health_check_includes_version(self, client):
        """Test that health check includes version info."""
        response = client.get(reverse('health:overall'))
        assert response.status_code == 200
        assert 'version' in response.json()
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

