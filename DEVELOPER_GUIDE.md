# Expense Tracker Developer Guide

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 15+
- Redis
- Docker (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd expense-tracker
   ```

2. **Create virtual environment**
   ```bash
   python3.10 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/development.txt
   ```

4. **Create `.env` file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/api/v1/`

### API Documentation

Access the interactive API documentation:
- **Swagger UI**: http://localhost:8000/api/v1/docs/
- **ReDoc**: http://localhost:8000/api/v1/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/v1/schema/

---

## Project Structure

```
expense-tracker/
├── config/                 # Django configuration
│   ├── settings/
│   │   ├── base.py        # Base settings
│   │   ├── development.py # Dev settings
│   │   └── production.py  # Prod settings
│   ├── urls.py            # URL routing
│   ├── wsgi.py           # WSGI app
│   └── celery.py         # Celery config
│
├── apps/                   # Django apps
│   ├── authentication/    # User auth & JWT
│   ├── projects/          # Project management
│   ├── transactions/      # Income/expenses
│   ├── budgets/          # Budget tracking
│   ├── documents/        # File management
│   ├── reports/          # Analytics & reports
│   ├── activity/         # Activity logging
│   └── schema.py         # OpenAPI customization
│
├── requirements/          # Dependencies
│   ├── base.txt         # Core dependencies
│   ├── development.txt  # Dev dependencies
│   └── production.txt   # Prod dependencies
│
├── API_DOCUMENTATION.md   # API reference
├── DEVELOPER_GUIDE.md    # This file
├── manage.py            # Django CLI
└── conftest.py          # Pytest configuration
```

---

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest apps/transactions/tests/test_api.py

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test class
pytest apps/transactions/tests/test_api.py::TestTransactionListView

# Run with verbose output
pytest -v
```

### Database

```bash
# Create new migration
python manage.py makemigrations app_name

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Revert to specific migration
python manage.py migrate app_name 0001
```

### Running Celery

```bash
# Run Celery worker
celery -A config worker -l info

# Run Celery beat (scheduler)
celery -A config beat -l info

# Run both together
celery -A config worker -B -l info
```

### Redis

```bash
# Start Redis (Docker)
docker run -d -p 6379:6379 redis

# Test Redis connection
redis-cli ping
```

### Docker Development

```bash
# Build images
docker-compose build

# Start services
docker-compose up

# Run migrations in Docker
docker-compose run web python manage.py migrate

# Create superuser in Docker
docker-compose run web python manage.py createsuperuser
```

---

## API Development

### Adding New Endpoint

1. **Create model** in `apps/yourapp/models.py`
2. **Create serializer** in `apps/yourapp/serializers.py`
3. **Create view** in `apps/yourapp/views.py`
4. **Add URL route** in `apps/yourapp/urls.py`
5. **Write tests** in `apps/yourapp/tests/test_api.py`
6. **Add docstring** to view for documentation

### Example: Creating a New Endpoint

```python
# models.py
from django.db import models
from django.conf import settings

class MyModel(models.Model):
    """My model description."""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100)
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


# serializers.py
from rest_framework import serializers
from .models import MyModel

class MyModelSerializer(serializers.ModelSerializer):
    """Serializer for MyModel."""

    class Meta:
        model = MyModel
        fields = ["id", "name", "project", "created_at"]
        read_only_fields = ["id", "created_at"]


# views.py
from rest_framework import generics, permissions
from .models import MyModel
from .serializers import MyModelSerializer

class MyModelListCreateView(generics.ListCreateAPIView):
    """
    List and create MyModel instances.

    - GET: Retrieve paginated list of models
    - POST: Create new model
    """

    serializer_class = MyModelSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["project"]
    search_fields = ["name"]
    ordering_fields = ["created_at", "name"]

    def get_queryset(self):
        """Return models accessible to user."""
        return MyModel.objects.filter(
            project__members__user=self.request.user
        )


# urls.py
from django.urls import path
from .views import MyModelListCreateView

urlpatterns = [
    path("mymodels/", MyModelListCreateView.as_view(), name="mymodel-list"),
]
```

### Permission System

All endpoints should check user permissions:

```python
from apps.projects.permissions import get_project_and_membership, require_owner_or_admin

try:
    project, membership = get_project_and_membership(project_id, request.user)
except (NotFound, PermissionDenied):
    raise  # Let DRF handle the error

# Check if admin/owner
require_owner_or_admin(membership)
```

### Adding Documentation

Each view should have clear docstrings:

```python
class MyView(APIView):
    """
    Brief description of what this view does.

    Detailed explanation of functionality, supported operations, etc.

    - GET: Retrieve data
    - POST: Create new item
    - PATCH: Update item
    - DELETE: Delete item

    Query Parameters:
        - page: Page number (default: 1)
        - search: Search query

    Authentication:
        - Required: JWT Bearer token
        - Roles: Any authenticated user

    Example:
        GET /api/v1/endpoint/?page=1
        Authorization: Bearer {token}
    """
    pass
```

---

## Testing

### Test Structure

```python
import pytest
from rest_framework.test import APIClient
from rest_framework import status

@pytest.fixture
def auth_client(user):
    """Authenticated API client."""
    client = APIClient()
    client.force_authenticate(user=user)
    return client

@pytest.mark.django_db
class TestMyEndpoint:
    """Test MyEndpoint."""

    def test_list_items(self, auth_client):
        """Test listing items."""
        response = auth_client.get("/api/v1/items/")
        assert response.status_code == status.HTTP_200_OK

    def test_create_item(self, auth_client):
        """Test creating item."""
        data = {"name": "Test Item"}
        response = auth_client.post("/api/v1/items/", data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_permission_denied(self, client):
        """Test that unauthenticated users get 401."""
        response = client.get("/api/v1/items/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

### Running Tests

```bash
# All tests
pytest

# Specific file
pytest apps/myapp/tests/test_api.py

# Specific class
pytest apps/myapp/tests/test_api.py::TestMyEndpoint

# Specific method
pytest apps/myapp/tests/test_api.py::TestMyEndpoint::test_list_items

# With coverage
pytest --cov=apps --cov-report=html

# Verbose output
pytest -v

# Show print statements
pytest -s
```

---

## Logging

### Configuration

Logging is configured in `config/settings/base.py`. The system logs to console in development and to files in production.

### Using Logger

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: Confirmation that things work as expected
- **WARNING**: Warning that something might go wrong
- **ERROR**: Error condition (something failed)
- **CRITICAL**: Critical error (system failure)

---

## Deployment

### Environment Variables

Create a `.env` file with:

```env
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=expense_tracker
DB_USER=postgres
DB_PASSWORD=strong_password
DB_HOST=db.example.com
DB_PORT=5432

# Redis
REDIS_URL=redis://redis.example.com:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-password
DEFAULT_FROM_EMAIL=noreply@expensetracker.com

# AWS S3 (for file uploads)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=us-east-1
```

### Running in Production

```bash
# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Start Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4

# Run Celery in background
celery -A config worker -l info &
celery -A config beat -l info &
```

### Using Docker

```bash
# Build production image
docker build -f Dockerfile -t expense-tracker:latest .

# Run container
docker run -p 8000:8000 --env-file .env expense-tracker:latest

# Using Docker Compose
docker-compose -f docker-compose.yml up -d
```

---

## Common Tasks

### Create Superuser

```bash
python manage.py createsuperuser
```

### Reset Database

```bash
# Delete all data (development only)
python manage.py flush

# Or manually drop database and recreate
# dropdb expense_tracker
# createdb expense_tracker
# python manage.py migrate
```

### Generate API Schema

```bash
# Generate OpenAPI schema
python manage.py spectacular --file schema.yml

# Pretty print
python manage.py spectacular --file schema.yml --format yaml
```

### Seed Database

```bash
# Create test data
python manage.py seed_data
```

---

## Performance Optimization

### Database Queries

Use `select_related()` and `prefetch_related()` to reduce queries:

```python
# Bad: N+1 queries
for item in items:
    print(item.user.name)

# Good: Single query
items = items.select_related('user')
for item in items:
    print(item.user.name)

# For reverse relations
items = items.prefetch_related('comments')
```

### Caching

Use Django's cache framework:

```python
from django.core.cache import cache

# Set cache
cache.set('key', value, 3600)  # 1 hour

# Get cache
value = cache.get('key')

# Delete cache
cache.delete('key')

# Clear all cache
cache.clear()
```

### Database Indexing

Add indexes to frequently queried fields:

```python
class MyModel(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['created_at', 'name']),
        ]
```

---

## Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check PostgreSQL is running
psql -U postgres

# Check connection string in .env
# Verify DB credentials
```

**Redis Connection Error**
```bash
# Check Redis is running
redis-cli ping

# Should return: PONG
```

**Static Files Not Showing**
```bash
# Collect static files
python manage.py collectstatic --noinput
```

**Tests Failing**
```bash
# Check database is set up
pytest

# With verbose output
pytest -v

# Check coverage
pytest --cov=apps
```

---

## Useful Commands

```bash
# Django shell
python manage.py shell

# Check for security issues
python manage.py check --deploy

# Show database queries during request
python manage.py shell_plus  # Requires django-extensions

# Run specific app migrations
python manage.py migrate app_name

# Create empty migration
python manage.py makemigrations --empty app_name --name migration_name

# Format code
black .

# Check code style
flake8 apps

# Type checking
mypy apps
```

---

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [pytest Documentation](https://docs.pytest.org/)

---

## Support

For development questions, check the API documentation or contact the development team.
