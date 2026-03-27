# Contributing to Expense Tracker API

Thank you for your interest in contributing to the Expense Tracker API! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and professional. Harassment or discrimination of any kind will not be tolerated.

## Ways to Contribute

### 1. Report Bugs
- Check [existing issues](../../issues) first
- Create detailed bug report with:
  - Environment info (OS, Python version, Django version)
  - Steps to reproduce
  - Expected behavior
  - Actual behavior
  - Error messages/logs

### 2. Suggest Features
- Check [existing discussions](../../discussions)
- Describe the feature and its use case
- Explain why it would be useful
- Provide examples if applicable

### 3. Submit Code
- Fix bugs
- Implement features
- Improve documentation
- Add tests
- Optimize performance

### 4. Improve Documentation
- Fix typos
- Improve clarity
- Add examples
- Translate to other languages

## Development Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- Redis 6+
- Git

### Local Development

```bash
# Fork repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/expense-tracker.git
cd expense-tracker

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/expense-tracker.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements/development.txt

# Create .env file
cp .env.example .env

# Update .env with your local settings
# DATABASE_URL=postgresql://user:password@localhost:5432/test_db
# REDIS_URL=redis://localhost:6379/0

# Run migrations
python manage.py migrate

# Create test user
python manage.py createsuperuser

# Start development server
python manage.py runserver

# In another terminal, start Celery
celery -A config worker -l info

# In another terminal, start Celery Beat
celery -A config beat -l info
```

## Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/your-bug-name

# Or for documentation
git checkout -b docs/your-doc-name
```

### 2. Follow Coding Standards

#### PEP 8 & Black
```bash
# Format code with Black
black apps/

# Check style with flake8
flake8 apps/

# Auto-fix common issues
black --line-length 100 apps/
```

#### Type Hints
```python
# Good - include type hints
def get_user(user_id: int) -> User:
    return User.objects.get(id=user_id)

# Bad - missing type hints
def get_user(user_id):
    return User.objects.get(id=user_id)
```

#### Docstrings
```python
# Good - clear docstring
def calculate_budget_status(budget: Budget) -> str:
    """
    Calculate current budget status.

    Args:
        budget: Budget instance to check

    Returns:
        Status string: 'on_track', 'warning', or 'exceeded'

    Raises:
        ValueError: If budget amount is invalid
    """
    pass

# Bad - no docstring
def calculate_budget_status(budget):
    pass
```

### 3. Write Tests (TDD)

**Test-Driven Development**: Write tests BEFORE implementing features

```bash
# Create test file
touch apps/your_app/tests/test_your_feature.py
```

```python
# tests/test_your_feature.py
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestYourFeature:
    """Test your feature."""

    def test_basic_functionality(self):
        """Test basic feature functionality."""
        # Arrange
        user = User.objects.create_user(
            email='test@example.com',
            password='TestPass123!'
        )

        # Act
        result = your_function(user)

        # Assert
        assert result is not None
```

```bash
# Run your tests
pytest apps/your_app/tests/test_your_feature.py -v

# Run with coverage
pytest --cov=apps/your_app tests/
```

### 4. Implement Feature

```python
# apps/your_app/models.py
from django.db import models

class YourModel(models.Model):
    """Your model description."""
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Your Model"
        verbose_name_plural = "Your Models"

    def __str__(self) -> str:
        return self.name
```

### 5. Run Full Test Suite

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=apps --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m security
```

### 6. Commit Changes

```bash
# Stage changes
git add .

# Commit with clear message
git commit -m "Add your feature description

- Detailed description of changes
- Another point if needed
- Reference issue: Fixes #123"

# Common commit types:
# feat: New feature
# fix: Bug fix
# docs: Documentation
# style: Code style (no logic change)
# refactor: Code refactoring
# perf: Performance improvement
# test: Test addition/modification
# chore: Maintenance tasks
```

### 7. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 8. Create Pull Request

**On GitHub**:
1. Go to your fork
2. Click "New Pull Request"
3. Select your branch
4. Fill in PR template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #123

## How Has This Been Tested?
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests pass locally
- [ ] Changes generate no new warnings

## Screenshots (if applicable)
```

## Pull Request Guidelines

### Requirements
- ✅ All tests pass (`pytest`)
- ✅ Code coverage maintained (min 80%)
- ✅ Code style passes (`black`, `flake8`)
- ✅ Docstrings included
- ✅ Documentation updated
- ✅ No merge conflicts

### Review Process

1. **Automated Checks**
   - Tests run via GitHub Actions
   - Coverage reported
   - Linting checked

2. **Code Review**
   - Team reviews code
   - Feedback provided
   - Changes requested if needed

3. **Approval & Merge**
   - Approved by maintainers
   - Merged to main branch
   - Closes related issues

## Testing Requirements

### Unit Tests
- Test business logic
- Test validators
- Test serializers
- Target: 80%+ coverage

### Integration Tests
- Test API endpoints
- Test database interactions
- Test permissions
- Test error handling

### Security Tests
- SQL injection prevention
- XSS prevention
- Authentication
- Authorization

### Performance Tests
- Response times
- Load capacity
- Memory usage

```bash
# Run all tests with coverage
pytest --cov=apps --cov-report=term-missing --cov-report=html

# View coverage
open htmlcov/index.html
```

## Documentation Standards

### Code Comments
```python
# Good - explains WHY, not WHAT
# Use list instead of set because we need to maintain order
items = list(set_items)

# Bad - explains WHAT (already clear from code)
# Convert items to list
items = list(set_items)
```

### Docstring Format
```python
def your_function(arg1: int, arg2: str) -> dict:
    """
    Brief one-line description.

    Longer description if needed. Explain the purpose,
    behavior, and any important details.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: Description of error condition

    Example:
        >>> result = your_function(1, "test")
        >>> print(result)
    """
    pass
```

### API Documentation
Update relevant documentation files:
- [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- [API_ENDPOINTS_VALIDATION.md](API_ENDPOINTS_VALIDATION.md)
- Swagger docstrings in views

## Git Workflow

### Keep Fork Updated
```bash
# Fetch upstream changes
git fetch upstream

# Rebase your branch
git rebase upstream/main

# Force push to your fork (use carefully!)
git push origin your-branch -f
```

### Squash Commits (if requested)
```bash
# Interactive rebase
git rebase -i upstream/main

# Mark commits to squash with 's'
# Save and close editor

git push origin your-branch -f
```

## Issue Labels

| Label | Meaning |
|-------|---------|
| `bug` | Something is broken |
| `feature` | New feature request |
| `enhancement` | Improvement to existing feature |
| `documentation` | Documentation improvement |
| `good first issue` | Good for new contributors |
| `help wanted` | Need assistance |
| `question` | Question or clarification |
| `security` | Security-related |
| `performance` | Performance issue/improvement |

## Communication

### How to Ask Questions
- Use [GitHub Discussions](../../discussions)
- Be specific and provide context
- Include error messages or examples

### How to Report Security Issues
- **DO NOT** create public GitHub issue
- Email security@expensetracker.com
- Include details and reproduction steps
- Allow time for patch before disclosure

## Recognition

Contributors will be:
- Added to [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Mentioned in release notes
- Recognized in project README

## Questions?

- Check existing documentation
- Search [GitHub Issues](../../issues)
- Post in [GitHub Discussions](../../discussions)
- Email: dev@expensetracker.com

## Resources

- [Developer Guide](DEVELOPER_GUIDE.md)
- [Testing Strategy](TESTING_STRATEGY.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Django Documentation](https://docs.djangoproject.com/)
- [DRF Documentation](https://www.django-rest-framework.org/)
- [pytest Documentation](https://docs.pytest.org/)

---

**Thank you for contributing!** 🎉

Your efforts help make the Expense Tracker API better for everyone.
