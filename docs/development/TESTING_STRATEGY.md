# Testing Strategy & Best Practices

## Overview

This document outlines the comprehensive testing strategy for the Expense Tracker API, covering unit tests, integration tests, end-to-end tests, performance tests, and security tests.

## Table of Contents

1. [Testing Pyramid](#testing-pyramid)
2. [Test Environment Setup](#test-environment-setup)
3. [Unit Tests](#unit-tests)
4. [Integration Tests](#integration-tests)
5. [End-to-End Tests](#end-to-end-tests)
6. [Performance Tests](#performance-tests)
7. [Security Tests](#security-tests)
8. [Test Coverage](#test-coverage)
9. [Continuous Testing](#continuous-testing)
10. [Test Data Management](#test-data-management)

---

## Testing Pyramid

### Distribution

```
        /\
       /  \        E2E Tests (10%)
      /    \       - Full workflow testing
     /------\      - User journey validation
    /        \
   /          \    Integration Tests (30%)
  /            \   - API endpoint testing
 /              \  - Database interactions
/________________\ - Service integration

Unit Tests (60%)
- Model logic
- Serializer validation
- Utility functions
- Business logic
```

### Testing Goals

- **Unit Tests**: Fast feedback (< 100ms per test)
- **Integration Tests**: Moderate speed (< 1s per test)
- **E2E Tests**: Slow but comprehensive (< 30s per test)
- **Coverage Target**: 80% code coverage minimum

---

## Test Environment Setup

### Dependencies

```bash
pip install pytest pytest-django pytest-cov pytest-factoryboy
pip install factory-boy faker
pip install pytest-xdist  # Parallel execution
pip install pytest-benchmark  # Performance testing
```

### Configuration

```python
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.testing
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --disable-warnings
    --cov=apps
    --cov-report=html
    --cov-report=xml
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow tests
    security: Security tests
```

### Test Database

```python
# settings/testing.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # In-memory for speed
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Disable migrations for speed
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()
```

---

## Unit Tests

### Model Tests

```python
# apps/projects/tests/test_models.py
import pytest
from django.contrib.auth import get_user_model
from apps.projects.models import Project

User = get_user_model()

@pytest.mark.django_db
class TestProjectModel:
    """Test Project model."""

    def test_project_creation(self):
        """Test creating a project."""
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPassword123!'
        )
        project = Project.objects.create(
            name='Test Project',
            owner=user
        )
        assert project.name == 'Test Project'
        assert project.owner == user

    def test_project_str(self):
        """Test project string representation."""
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPassword123!'
        )
        project = Project.objects.create(
            name='Test Project',
            owner=user
        )
        assert str(project) == 'Test Project'

    def test_project_slug_generation(self):
        """Test project slug is generated correctly."""
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPassword123!'
        )
        project = Project.objects.create(
            name='My Test Project',
            owner=user
        )
        assert project.slug == 'my-test-project'

    def test_project_unique_slug(self):
        """Test project slug is unique."""
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPassword123!'
        )
        project1 = Project.objects.create(
            name='Test Project',
            owner=user
        )
        project2 = Project.objects.create(
            name='Test Project',
            owner=user
        )
        assert project1.slug != project2.slug
```

### Serializer Tests

```python
# apps/projects/tests/test_serializers.py
import pytest
from apps.projects.serializers import ProjectSerializer

@pytest.mark.django_db
class TestProjectSerializer:
    """Test ProjectSerializer."""

    def test_valid_serializer(self, user, project):
        """Test serializing valid project."""
        serializer = ProjectSerializer(project)
        assert serializer.data['name'] == project.name
        assert serializer.data['id'] == str(project.id)

    def test_missing_required_field(self):
        """Test serializer with missing required field."""
        data = {}
        serializer = ProjectSerializer(data=data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors

    def test_invalid_email(self):
        """Test serializer with invalid email."""
        data = {
            'name': 'Test',
            'owner_email': 'invalid-email'
        }
        serializer = ProjectSerializer(data=data)
        assert not serializer.is_valid()
```

### Utility Tests

```python
# apps/utils/tests/test_validators.py
import pytest
from django.core.exceptions import ValidationError
from apps.security.validators import (
    validate_secure_password,
    validate_no_sql_injection,
    SafeFieldValidator
)

class TestPasswordValidation:
    """Test password validation."""

    def test_weak_password(self):
        """Test weak password is rejected."""
        with pytest.raises(ValidationError):
            validate_secure_password('weak')

    def test_strong_password(self):
        """Test strong password is accepted."""
        validate_secure_password('StrongPass123!')

    def test_password_without_uppercase(self):
        """Test password without uppercase is rejected."""
        with pytest.raises(ValidationError):
            validate_secure_password('lowercase123!')

class TestSQLInjectionPrevention:
    """Test SQL injection prevention."""

    def test_sql_injection_detected(self):
        """Test SQL injection pattern is detected."""
        with pytest.raises(ValidationError):
            validate_no_sql_injection("'; DROP TABLE users;--")

    def test_normal_input_accepted(self):
        """Test normal input is accepted."""
        validate_no_sql_injection('Normal user input')
```

---

## Integration Tests

### API Endpoint Tests

```python
# apps/projects/tests/test_api.py
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestProjectAPI:
    """Test Project API endpoints."""

    @pytest.fixture
    def api_client(self):
        """Provide API client."""
        return APIClient()

    @pytest.fixture
    def user(self):
        """Create test user."""
        return User.objects.create_user(
            email='test@example.com',
            password='TestPassword123!'
        )

    def test_list_projects_requires_authentication(self, api_client):
        """Test list projects requires authentication."""
        response = api_client.get('/api/v1/projects/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_projects_authenticated(self, api_client, user):
        """Test list projects when authenticated."""
        api_client.force_authenticate(user=user)
        response = api_client.get('/api/v1/projects/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['results'] == []

    def test_create_project(self, api_client, user):
        """Test creating a project."""
        api_client.force_authenticate(user=user)
        data = {'name': 'New Project'}
        response = api_client.post('/api/v1/projects/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == 'New Project'

    def test_create_project_invalid_data(self, api_client, user):
        """Test creating project with invalid data."""
        api_client.force_authenticate(user=user)
        data = {}  # Missing required field
        response = api_client.post('/api/v1/projects/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data

    def test_project_permissions(self, api_client, user):
        """Test user can only access their projects."""
        other_user = User.objects.create_user(
            email='other@example.com',
            password='OtherPass123!'
        )
        project = Project.objects.create(
            name='Other Project',
            owner=other_user
        )

        api_client.force_authenticate(user=user)
        response = api_client.get(f'/api/v1/projects/{project.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
```

### Database Transaction Tests

```python
@pytest.mark.django_db
def test_transaction_rollback(user):
    """Test transaction rollback on error."""
    from django.db import transaction

    with pytest.raises(Exception):
        with transaction.atomic():
            Project.objects.create(name='Test', owner=user)
            raise Exception('Rollback test')

    # Project should not exist
    assert not Project.objects.filter(name='Test').exists()
```

---

## End-to-End Tests

### User Journey Tests

```python
# apps/tests/test_e2e_workflows.py
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.e2e
@pytest.mark.django_db
class TestUserJourneys:
    """Test complete user workflows."""

    @pytest.fixture
    def client(self):
        return APIClient()

    def test_user_registration_to_budget_tracking(self, client):
        """Test complete workflow from registration to budget tracking."""
        # 1. User registration
        register_data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!'
        }
        response = client.post('/api/v1/auth/register/', register_data)
        assert response.status_code == 201

        # 2. User login
        login_data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!'
        }
        response = client.post('/api/v1/auth/login/', login_data)
        assert response.status_code == 200
        token = response.data['access']

        # 3. Create project
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        project_data = {'name': 'Home Budget'}
        response = client.post('/api/v1/projects/', project_data)
        assert response.status_code == 201
        project_id = response.data['id']

        # 4. Create budget
        budget_data = {
            'name': 'Monthly Groceries',
            'amount': 500.00,
            'project': project_id,
            'period': 'monthly'
        }
        response = client.post('/api/v1/budgets/', budget_data)
        assert response.status_code == 201

        # 5. Create transaction
        transaction_data = {
            'amount': 50.00,
            'category': 'groceries',
            'project': project_id
        }
        response = client.post('/api/v1/transactions/', transaction_data)
        assert response.status_code == 201

        # 6. Check budget status
        response = client.get(f'/api/v1/budgets/{response.data["id"]}/status/')
        assert response.status_code == 200
        assert response.data['spent'] == 50.00
```

### Multi-User Scenarios

```python
@pytest.mark.e2e
@pytest.mark.django_db
def test_project_collaboration(client):
    """Test multiple users collaborating on a project."""
    # Create two users
    user1 = User.objects.create_user(
        email='user1@example.com',
        password='Pass1234!'
    )
    user2 = User.objects.create_user(
        email='user2@example.com',
        password='Pass1234!'
    )

    # User1 creates project
    client.force_authenticate(user=user1)
    project_data = {'name': 'Team Project'}
    response = client.post('/api/v1/projects/', project_data)
    project_id = response.data['id']

    # User1 invites User2
    invite_data = {'email': 'user2@example.com'}
    response = client.post(f'/api/v1/projects/{project_id}/invite/', invite_data)
    assert response.status_code == 201

    # User2 accepts invitation
    client.force_authenticate(user=user2)
    response = client.get(f'/api/v1/projects/{project_id}/')
    assert response.status_code == 200

    # Both users can add transactions
    transaction_data = {'amount': 100.00, 'project': project_id}
    response = client.post('/api/v1/transactions/', transaction_data)
    assert response.status_code == 201
```

---

## Performance Tests

### Load Testing with Locust

```python
# tests/load_test.py
from locust import HttpUser, task, between
import random

class ExpenseTrackerUser(HttpUser):
    """Simulate user behavior."""

    wait_time = between(1, 5)

    def on_start(self):
        """Login on start."""
        response = self.client.post('/api/v1/auth/login/', {
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        })
        self.token = response.json()['access']
        self.headers = {'Authorization': f'Bearer {self.token}'}

    @task(5)
    def list_projects(self):
        """List projects."""
        self.client.get('/api/v1/projects/', headers=self.headers)

    @task(3)
    def list_transactions(self):
        """List transactions."""
        self.client.get('/api/v1/transactions/', headers=self.headers)

    @task(2)
    def create_transaction(self):
        """Create transaction."""
        data = {
            'amount': random.uniform(10, 500),
            'category': 'groceries',
            'description': 'Test transaction'
        }
        self.client.post('/api/v1/transactions/', json=data, headers=self.headers)

    @task(1)
    def generate_report(self):
        """Generate report."""
        self.client.get('/api/v1/reports/summary/', headers=self.headers)
```

### Benchmark Tests

```python
@pytest.mark.benchmark
@pytest.mark.django_db
def test_list_projects_performance(benchmark, user):
    """Benchmark project listing."""
    from apps.projects.models import Project

    # Create test data
    for i in range(100):
        Project.objects.create(name=f'Project {i}', owner=user)

    def list_projects():
        return Project.objects.filter(owner=user).values_list('id', 'name')

    result = benchmark(list_projects)
    assert len(result) == 100
```

---

## Security Tests

### Authentication Tests

```python
@pytest.mark.security
@pytest.mark.django_db
class TestAuthenticationSecurity:
    """Test authentication security."""

    def test_password_not_returned(self, user):
        """Test password is never returned in responses."""
        serializer = UserSerializer(user)
        assert 'password' not in serializer.data

    def test_sql_injection_in_login(self, client):
        """Test SQL injection prevention in login."""
        data = {
            'email': "'; DROP TABLE users;--",
            'password': "password"
        }
        response = client.post('/api/v1/auth/login/', data)
        # Should not execute SQL, just fail auth
        assert response.status_code == 401

    def test_brute_force_protection(self, client, user):
        """Test account lockout after failed attempts."""
        for i in range(6):
            data = {
                'email': user.email,
                'password': 'WrongPassword'
            }
            response = client.post('/api/v1/auth/login/', data)

        # 6th attempt should be locked
        assert response.status_code == 429  # Too Many Requests
```

### Input Validation Tests

```python
@pytest.mark.security
@pytest.mark.django_db
def test_xss_prevention(client, user):
    """Test XSS prevention."""
    client.force_authenticate(user=user)

    malicious_input = '<script>alert("xss")</script>'
    data = {
        'description': malicious_input
    }
    response = client.post('/api/v1/transactions/', data)

    # Should either sanitize or reject
    if response.status_code == 201:
        # Check it was sanitized
        saved = Transaction.objects.get(id=response.data['id'])
        assert '<script>' not in saved.description
```

### Permission Tests

```python
@pytest.mark.security
@pytest.mark.django_db
def test_object_level_permissions(client, user, other_user):
    """Test users can't access other users' objects."""
    client.force_authenticate(user=other_user)

    project = Project.objects.create(name='Private', owner=user)
    response = client.get(f'/api/v1/projects/{project.id}/')

    assert response.status_code == 404
```

---

## Test Coverage

### Coverage Report

```bash
# Run tests with coverage
pytest --cov=apps --cov-report=html --cov-report=term-missing

# View HTML report
open htmlcov/index.html
```

### Coverage Goals

```
apps/authentication/   85%  ✓
apps/projects/         82%  ✓
apps/transactions/     88%  ✓
apps/documents/        75%  ⚠
apps/budgets/          90%  ✓
apps/reports/          85%  ✓
apps/activity/         80%  ✓
apps/security/         88%  ✓
apps/health/           95%  ✓
apps/utils/            92%  ✓
---
Overall:               85%  ✓
```

---

## Continuous Testing

### GitHub Actions Integration

```yaml
# .github/workflows/tests.yml
- name: Run tests
  run: pytest --cov --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

### Pre-commit Hooks

```bash
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest
        entry: pytest
        language: system
        types: [python]
        pass_filenames: false
        always_run: true
```

---

## Test Data Management

### Fixtures

```python
# conftest.py
import pytest
from django.contrib.auth import get_user_model
from factory import fuzzy

User = get_user_model()

@pytest.fixture
def user():
    """Create test user."""
    return User.objects.create_user(
        email='test@example.com',
        password='TestPassword123!'
    )

@pytest.fixture
def api_client():
    """Provide API client."""
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, user):
    """Provide authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client
```

### Factory Boy

```python
# apps/projects/tests/factories.py
import factory
from apps.projects.models import Project
from django.contrib.auth import get_user_model

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'user{n}@example.com')
    first_name = factory.Faker('first_name')

class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    name = factory.Faker('name')
    owner = factory.SubFactory(UserFactory)
```

---

## Running Tests

### All Tests
```bash
pytest
```

### Specific Test File
```bash
pytest apps/projects/tests/test_models.py
```

### Specific Test Class
```bash
pytest apps/projects/tests/test_models.py::TestProjectModel
```

### Specific Test Function
```bash
pytest apps/projects/tests/test_models.py::TestProjectModel::test_project_creation
```

### By Marker
```bash
pytest -m unit
pytest -m integration
pytest -m e2e
pytest -m security
```

### Parallel Execution
```bash
pytest -n auto
```

### Verbose Output
```bash
pytest -v
```

### Show Print Statements
```bash
pytest -s
```

---

## Test Best Practices

### DO ✓
- Write focused, single-responsibility tests
- Use descriptive test names
- Test edge cases and error conditions
- Use fixtures for setup/teardown
- Mock external dependencies
- Test behavior, not implementation
- Keep tests independent
- Use clear assertions

### DON'T ✗
- Create interdependent tests
- Test multiple features in one test
- Use hardcoded test data
- Sleep/wait in tests
- Test implementation details
- Ignore failing tests
- Write overly complex tests
- Test code that's already tested

---

## Continuous Improvement

### Test Metrics to Track

- Code coverage (target: 80%+)
- Test execution time (target: < 5 minutes)
- Flaky tests (target: 0)
- Test pass rate (target: 100%)
- New bug detection rate

### Regular Reviews

- Monthly: Review test coverage gaps
- Quarterly: Refactor slow tests
- Bi-annual: Update testing tools

---

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-django Documentation](https://pytest-django.readthedocs.io/)
- [Factory Boy Documentation](https://factoryboy.readthedocs.io/)
- [Locust Documentation](https://locust.io/)
- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)

