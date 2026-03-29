# Seed Data Generation Guide

This guide explains how to generate comprehensive test data for the Expense Tracker application.

## Overview

The seed data system creates realistic, extensive test data including:
- **Users** - Multiple test accounts with various settings
- **Projects** - Personal, Business, and Team projects
- **Categories** - Both default and project-specific expense/income categories
- **Transactions** - Historical transactions spread across multiple months
- **Budgets** - Various budget periods with alert thresholds
- **Documents** - Receipts, invoices, and contracts attached to transactions
- **Project Members** - Team collaboration with different roles
- **Invitations** - Pending and accepted project invitations

## Quick Start

### Using the Django Management Command

The simplest way to generate seed data:

```bash
# Generate medium volume data (default)
python manage.py seed_database

# Clear existing data and generate light volume
python manage.py seed_database --clear --volume light

# Generate heavy volume data
python manage.py seed_database --volume heavy

# Clear existing data and generate medium volume
python manage.py seed_database --clear --volume medium
```

### Using the Standalone Script

For more control or running outside Django management:

```bash
# Generate medium volume data
python seed_data.py

# Clear and generate light volume
python seed_data.py --clear --volume light

# Generate heavy volume data
python seed_data.py --volume heavy

# Clear and generate heavy volume
python seed_data.py --clear --volume heavy
```

## Data Volumes

The seed data generator supports three data volume levels:

### Light Volume
- **Users**: 5
- **Projects**: 10 (2 per user)
- **Transactions**: 900 (15 per project over 6 months)
- **Categories**: 29
- **Budgets**: 20
- **Documents**: 270
- **Project Members**: 3
- **Invitations**: 3

**Use for**: Quick testing, CI/CD pipelines, local development

### Medium Volume (Default)
- **Users**: 15
- **Projects**: 30 (2 per user)
- **Transactions**: 3,600 (20 per project over 6 months)
- **Categories**: 59
- **Budgets**: 90
- **Documents**: 1,440
- **Project Members**: 18
- **Invitations**: 18

**Use for**: Feature testing, integration testing, realistic scenarios

### Heavy Volume
- **Users**: 50
- **Projects**: 150 (3 per user)
- **Transactions**: 7,500+ (25 per project over 6 months)
- **Categories**: 150+
- **Budgets**: 200+
- **Documents**: 3,750+
- **Project Members**: 150+
- **Invitations**: 150+

**Use for**: Performance testing, load testing, stress testing

## Test User Accounts

All generated users follow this pattern:

```
Email: user{N}@testexp.com
Password: Str0ngPass!
```

Examples:
- `user1@testexp.com`
- `user2@testexp.com`
- `user3@testexp.com`
- ... up to user{N}

### User Properties

- **70% Verified**: Have email verification completed
- **30% Unverified**: New accounts awaiting email verification
- **Various Timezones**: UTC, America/New_York, Europe/London, Asia/Tokyo
- **Various Currencies**: USD, EUR, GBP, JPY

## Data Characteristics

### Projects

Three types of projects:
1. **Personal** - Single user projects
2. **Business** - May have multiple members
3. **Team** - Collaborative projects with multiple roles

Projects may be:
- Active or archived
- Have budgets (business and team projects)
- Have specific currency settings
- Contain multiple members with different roles

### Transactions

Transactions are created with realistic characteristics:

- **Spread across 6 months** - Historical data for reporting
- **Mixed types** - 75% expenses, 25% income
- **Payment methods**:
  - Cash
  - Card
  - Bank Transfer
  - Mobile Payment
- **Categories** - Both default and project-specific
- **Tags** - "seed", "test" for easy identification
- **Reference numbers** - For real-world scenario testing

### Budgets

Multiple budget periods to test different scenarios:

- **Weekly** - 7-day budgets
- **Monthly** - 30-day budgets (most common)
- **Quarterly** - 90-day budgets
- **Yearly** - 365-day budgets

Alert thresholds vary (70%, 80%, 90%) to test different alert scenarios.

### Categories

**Default Categories (available to all projects)**:

Expenses:
- Groceries
- Transport
- Utilities
- Entertainment
- Dining Out
- Shopping
- Healthcare
- Insurance
- Rent/Mortgage
- Gym

Income:
- Salary
- Freelance
- Investment
- Bonus

**Project-specific Categories**: Some projects have custom categories based on their needs.

### Documents

Document types included:
- **Receipt** - Most common (50%)
- **Invoice** - For business transactions (30%)
- **Contract** - For formal agreements (10%)
- **Other** - Miscellaneous (10%)

Files are simulated (not actual files) for testing purposes.

### Team Members and Invitations

For team projects:

**Roles**:
- Owner - Full permissions
- Admin - Most permissions except member management
- Member - Can create/edit transactions
- Viewer - Read-only access

**Invitations**:
- Some pending (7 days to expire)
- Some accepted (already joined)
- Some expired (example of expired invitations)

## Testing Scenarios

The seed data supports testing of:

### ✓ Multi-User Collaboration
- Multiple users sharing team projects
- Different roles and permissions
- Invitation workflows

### ✓ Transaction Variety
- Different transaction types (income/expense)
- Various amounts
- Multiple payment methods
- Different categories

### ✓ Budget Tracking
- Budgets at various completion levels
- Alert threshold testing
- Multiple budget periods
- Category-specific budgets

### ✓ Historical Data and Reporting
- Transactions across 6 months
- Testing date filters and ranges
- Period-based analytics
- Trend analysis

## Command Options

### Django Management Command

```bash
python manage.py seed_database [OPTIONS]

Options:
  --clear              Clear all existing data before seeding
  --volume {light,medium,heavy}  Data volume (default: medium)
  -h, --help          Show help message
```

### Standalone Script

```bash
python seed_data.py [OPTIONS]

Options:
  --clear              Clear all existing data before seeding
  --volume {light,medium,heavy}  Data volume (default: medium)
  -h, --help          Show help message
```

## Smart Data Handling

The seed system is **smart about existing data**:

- **Reuses existing users**: If users with the same email already exist, they are reused instead of creating duplicates
- **Adds more data**: Each run adds new projects, transactions, budgets, and documents
- **No conflicts**: You can run the command multiple times without errors
- **Optional cleanup**: Use `--clear` only when you need a completely fresh database

### Without --clear Flag
Running the seed command multiple times will **accumulate data**:
```bash
python manage.py seed_database --volume light    # Creates initial data
python manage.py seed_database --volume heavy    # Adds more data on top
# Result: You'll have data from both runs combined
```

### With --clear Flag
Starting fresh with a clean database:
```bash
python manage.py seed_database --clear --volume heavy
# Result: Database is wiped and repopulated with clean data
```

## Examples

### Scenario 1: Initial Development Setup
```bash
python manage.py seed_database --clear --volume medium
```
Creates fresh test data for feature development.

### Scenario 2: Performance Testing
```bash
python seed_data.py --clear --volume heavy
```
Generates large dataset to test application performance.

### Scenario 3: Add More Test Data
```bash
python manage.py seed_database --volume light
```
Keeps existing data and adds more test records.

### Scenario 4: CI/CD Pipeline
```bash
python manage.py seed_database --clear --volume light
```
Quick setup for automated testing.

## Troubleshooting

### Issue: "Model doesn't declare an explicit app_label"
**Solution**: Ensure Django settings are properly configured in your environment:
```bash
export DJANGO_SETTINGS_MODULE=config.settings.development
python seed_data.py
```

### Issue: Database connection errors
**Solution**: Ensure your database is running and migrations are up to date:
```bash
python manage.py migrate
python manage.py seed_database --clear --volume light
```

### Issue: Want completely fresh data
**Solution**: The system intelligently reuses existing users, so running multiple times will accumulate data. To reset:
```bash
python manage.py seed_database --clear --volume medium
# This clears everything and creates fresh data
```

### Issue: Existing user emails (legacy)
**Solution**: The system now automatically handles existing users by reusing them. You no longer need to worry about duplicate user emails - just run the command!
```bash
python manage.py seed_database --volume heavy  # Safe to run anytime
```

## Performance Notes

- **Light Volume**: ~5-10 seconds
- **Medium Volume**: ~15-30 seconds
- **Heavy Volume**: ~60-120 seconds

Performance depends on:
- Database speed
- Disk I/O performance
- System resources

## Best Practices

1. **For a completely fresh database, use --clear**
   ```bash
   python manage.py seed_database --clear --volume medium
   ```

2. **To add more data without losing existing data**
   ```bash
   python manage.py seed_database --volume light
   # Safe to run multiple times without errors
   ```

3. **Start with light volume for development**
   ```bash
   python manage.py seed_database --clear --volume light
   ```

4. **Gradually build up data as needed**
   ```bash
   python manage.py seed_database --volume light    # Initial setup
   python manage.py seed_database --volume medium   # Add more data
   python manage.py seed_database --volume heavy    # Add even more data
   # You can safely run these in sequence
   ```

5. **Use heavy volume for performance testing**
   ```bash
   python manage.py seed_database --clear --volume heavy
   ```

6. **Verify data after generation**
   ```bash
   python manage.py shell
   >>> from apps.authentication.models import User
   >>> User.objects.count()  # Should show user count
   ```

## Integration with Tests

The seed data uses the same factories as your test suite, ensuring consistency:

```python
from apps.authentication.tests.factories import UserFactory
from apps.transactions.tests.factories import TransactionFactory

# Your tests can use the same factories
user = UserFactory(email="test@example.com")
transaction = TransactionFactory(created_by=user)
```

## Customization

To modify the seed data generation, edit the respective files:

- **Django Command**: `apps/health/management/commands/seed_database.py`
- **Standalone Script**: `seed_data.py`

Or modify individual factories:
- `apps/authentication/tests/factories.py`
- `apps/projects/tests/factories.py`
- `apps/transactions/tests/factories.py`
- `apps/budgets/tests/factories.py`
- `apps/documents/tests/factories.py`

## Support

For issues or improvements, check the following:
1. Database is running and accessible
2. Django migrations are up to date: `python manage.py migrate`
3. All dependencies are installed: `pip install -r requirements.txt`
4. Virtual environment is activated
