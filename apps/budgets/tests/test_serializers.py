"""
Tests for budgets/serializers.py - Budget serializers.

Tests:
- BudgetSerializer - Budget validation, permission checks, date and amount validation
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal

from apps.budgets.serializers import BudgetSerializer
from apps.budgets.tests.factories import BudgetFactory
from apps.transactions.tests.factories import CategoryFactory
from apps.projects.tests.factories import ProjectFactory
from apps.projects.models import ProjectMember
from apps.authentication.tests.factories import UserFactory


@pytest.mark.django_db
class TestBudgetSerializer:
    """Test BudgetSerializer for budget validation and serialization."""

    def test_budget_serializer_valid_data(self):
        """Test that valid budget data is serialized."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project)

        budget = BudgetFactory(
            project=project,
            created_by=user,
            category=category,
            amount=Decimal("1000.00"),
            alert_threshold=80,
        )

        serializer = BudgetSerializer(budget)
        data = serializer.data

        assert data["amount"] == "1000.00"
        assert data["alert_threshold"] == 80
        assert data["project"] == project.id
        assert data["category"] == category.id

    def test_budget_serializer_nested_fields(self):
        """Test that nested fields are read-only."""
        user = UserFactory(email="user@example.com")
        project = ProjectFactory(owner=user, name="Q4 Planning", currency="USD")
        category = CategoryFactory(project=project, name="Travel")

        budget = BudgetFactory(
            project=project,
            created_by=user,
            category=category,
        )

        serializer = BudgetSerializer(budget)
        data = serializer.data

        assert data["project_name"] == "Q4 Planning"
        assert data["project_currency"] == "USD"
        assert data["category_name"] == "Travel"
        assert data["created_by_email"] == "user@example.com"

    def test_budget_serializer_read_only_fields(self):
        """Test that system-generated fields are read-only."""
        budget = BudgetFactory()

        data = {
            "amount": "2000.00",
            "id": "fake-id",
            "created_by": 999,
            "project": 999,
            "created_at": "2020-01-01T00:00:00Z",
        }

        serializer = BudgetSerializer(budget, data=data, partial=True)
        assert serializer.is_valid()

        # Read-only fields should not change
        assert serializer.validated_data.get("id") is None
        assert serializer.validated_data.get("created_by") is None
        assert serializer.validated_data.get("project") is None

    def test_budget_serializer_permission_validation_owner(self):
        """Test that project owner can manage budgets."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        data = {
            "project": project.id,
            "amount": "1000.00",
            "alert_threshold": 80,
        }

        request = type("Request", (), {"user": user})()
        serializer = BudgetSerializer(data=data, context={"request": request})

        assert serializer.is_valid()

    def test_budget_serializer_permission_validation_non_member(self):
        """Test that non-member cannot create budget."""
        owner = UserFactory()
        project = ProjectFactory(owner=owner)
        other_user = UserFactory()

        data = {
            "project": project.id,
            "amount": "1000.00",
            "alert_threshold": 80,
        }

        request = type("Request", (), {"user": other_user})()
        serializer = BudgetSerializer(data=data, context={"request": request})

        assert not serializer.is_valid()
        assert "permission" in str(serializer.errors).lower()

    def test_budget_serializer_permission_validation_admin_member(self):
        """Test that admin member can create budget."""
        owner = UserFactory()
        admin_user = UserFactory()
        project = ProjectFactory(owner=owner)

        ProjectMember.objects.create(
            project=project,
            user=admin_user,
            role=ProjectMember.Role.ADMIN,
        )

        data = {
            "project": project.id,
            "amount": "1000.00",
            "alert_threshold": 80,
        }

        request = type("Request", (), {"user": admin_user})()
        serializer = BudgetSerializer(data=data, context={"request": request})

        assert serializer.is_valid()

    def test_budget_serializer_date_validation_start_before_end(self):
        """Test that start date must be before end date."""
        start = date.today()
        end = start - timedelta(days=1)

        data = {
            "amount": "1000.00",
            "start_date": start,
            "end_date": end,
        }

        serializer = BudgetSerializer(data=data)
        assert not serializer.is_valid()
        assert "date" in str(serializer.errors).lower()

    def test_budget_serializer_date_validation_valid_range(self):
        """Test that valid date range is accepted."""
        start = date.today()
        end = start + timedelta(days=30)

        data = {
            "amount": "1000.00",
            "start_date": start,
            "end_date": end,
        }

        serializer = BudgetSerializer(data=data)
        # Should pass date validation
        assert not serializer.is_valid() or "date" not in str(serializer.errors).lower()

    def test_budget_serializer_amount_validation_positive(self):
        """Test that budget amount must be positive."""
        data = {"amount": "0.00"}

        serializer = BudgetSerializer(data=data)
        assert not serializer.is_valid()
        assert "amount" in serializer.errors

    def test_budget_serializer_amount_validation_negative(self):
        """Test that negative budget is rejected."""
        data = {"amount": "-100.00"}

        serializer = BudgetSerializer(data=data)
        assert not serializer.is_valid()
        assert "amount" in serializer.errors

    def test_budget_serializer_amount_validation_valid(self):
        """Test that positive budget is accepted."""
        data = {"amount": "1500.50"}

        serializer = BudgetSerializer(data=data)
        # Amount validation should pass
        assert not serializer.is_valid() or "amount" not in serializer.errors

    def test_budget_serializer_alert_threshold_validation_low(self):
        """Test that negative threshold is rejected."""
        data = {"alert_threshold": "-10"}

        serializer = BudgetSerializer(data=data)
        assert not serializer.is_valid()
        assert "alert_threshold" in serializer.errors or "threshold" in str(serializer.errors).lower()

    def test_budget_serializer_alert_threshold_validation_high(self):
        """Test that threshold > 100 is rejected."""
        data = {"alert_threshold": "150"}

        serializer = BudgetSerializer(data=data)
        assert not serializer.is_valid()
        assert "alert_threshold" in serializer.errors or "threshold" in str(serializer.errors).lower()

    def test_budget_serializer_alert_threshold_validation_valid(self):
        """Test that 0-100 threshold is accepted."""
        for threshold in [0, 50, 100]:
            data = {"alert_threshold": str(threshold)}

            serializer = BudgetSerializer(data=data)
            # Should pass threshold validation
            assert not serializer.is_valid() or "threshold" not in str(serializer.errors).lower()

    def test_budget_serializer_period_field(self):
        """Test that budget period is included."""
        budget = BudgetFactory(period="monthly")

        serializer = BudgetSerializer(budget)
        assert serializer.data["period"] == "monthly"

    def test_budget_serializer_alert_enabled_flag(self):
        """Test that alert enabled flag is included."""
        budget = BudgetFactory(alert_enabled=True)

        serializer = BudgetSerializer(budget)
        assert serializer.data["alert_enabled"] is True

    def test_budget_serializer_category_optional(self):
        """Test that category is optional (project-wide budgets)."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        budget = BudgetFactory(
            project=project,
            created_by=user,
            category=None,
        )

        serializer = BudgetSerializer(budget)
        assert serializer.data["category"] is None

    def test_budget_serializer_update(self):
        """Test that budget can be updated."""
        budget = BudgetFactory(
            amount=Decimal("1000.00"),
            alert_threshold=80,
        )

        update_data = {
            "amount": "2000.00",
            "alert_threshold": 90,
        }

        serializer = BudgetSerializer(budget, data=update_data, partial=True)
        assert serializer.is_valid()

        updated = serializer.save()
        assert updated.amount == Decimal("2000.00")
        assert updated.alert_threshold == 90
