import uuid
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.budgets.models import Budget

from .factories import BudgetFactory, BudgetWithCategoryFactory


@pytest.mark.django_db
class TestBudgetModel:
    """Test Budget model functionality."""

    def test_create_budget(self):
        """Test creating a basic budget."""
        budget = BudgetFactory()
        assert budget.pk is not None
        assert budget.project is not None
        assert budget.amount > 0

    def test_uuid_primary_key(self):
        """Test that Budget uses UUID primary key."""
        budget = BudgetFactory()
        assert isinstance(budget.pk, uuid.UUID)

    def test_str_representation(self):
        """Test string representation of budget."""
        budget = BudgetFactory()
        budget_str = str(budget)
        assert budget.project.name in budget_str
        assert str(budget.amount) in budget_str

    def test_str_representation_with_category(self):
        """Test string representation with a category."""
        budget = BudgetWithCategoryFactory()
        budget_str = str(budget)
        assert budget.category.name in budget_str
        assert budget.project.name in budget_str

    def test_default_values(self):
        """Test default values for budget."""
        budget = BudgetFactory()
        assert budget.period == Budget.Period.MONTHLY
        assert budget.alert_threshold == 80
        assert budget.alert_enabled is True
        assert budget.category is None

    def test_timestamps(self):
        """Test created_at and updated_at timestamps."""
        budget = BudgetFactory()
        assert budget.created_at is not None
        assert budget.updated_at is not None

    def test_project_relationship(self):
        """Test project foreign key relationship."""
        budget = BudgetFactory()
        assert budget.project is not None
        assert budget in budget.project.budgets.all()

    def test_category_relationship_optional(self):
        """Test that category is optional."""
        budget = BudgetFactory(category=None)
        assert budget.category is None

    def test_category_relationship(self):
        """Test category foreign key relationship."""
        budget = BudgetWithCategoryFactory()
        assert budget.category is not None
        assert budget in budget.category.budgets.all()

    def test_created_by_relationship(self):
        """Test created_by user relationship."""
        budget = BudgetFactory()
        assert budget.created_by is not None
        assert budget in budget.created_by.created_budgets.all()

    def test_period_choices(self):
        """Test all period choices are valid."""
        for period in Budget.Period:
            budget = BudgetFactory(period=period)
            assert budget.period == period.value

    def test_different_currencies(self):
        """Test budgets with different project currencies."""
        from apps.projects.tests.factories import ProjectFactory

        project_usd = ProjectFactory(currency="USD")
        project_eur = ProjectFactory(currency="EUR")

        budget_usd = BudgetFactory(project=project_usd)
        budget_eur = BudgetFactory(project=project_eur)

        assert budget_usd.project.currency == "USD"
        assert budget_eur.project.currency == "EUR"

    def test_alert_threshold_range(self):
        """Test alert threshold can be set to various values."""
        for threshold in [0, 25, 50, 75, 80, 100]:
            budget = BudgetFactory(alert_threshold=threshold)
            assert budget.alert_threshold == threshold

    def test_alert_enabled_toggle(self):
        """Test alert_enabled flag can be toggled."""
        budget_enabled = BudgetFactory(alert_enabled=True)
        budget_disabled = BudgetFactory(alert_enabled=False)

        assert budget_enabled.alert_enabled is True
        assert budget_disabled.alert_enabled is False

    def test_date_range(self):
        """Test start_date and end_date are properly stored."""
        start = timezone.now().date()
        end = start + timedelta(days=30)

        budget = BudgetFactory(start_date=start, end_date=end)
        assert budget.start_date == start
        assert budget.end_date == end

    def test_cascade_delete_with_project(self):
        """Test that deleting a project cascades to delete budgets."""
        budget = BudgetFactory()
        project_id = budget.project.id
        budget.project.delete()

        assert not Budget.objects.filter(project_id=project_id).exists()

    def test_cascade_delete_with_category(self):
        """Test that deleting a category cascades to delete budgets."""
        budget = BudgetWithCategoryFactory()
        category_id = budget.category.id
        budget.category.delete()

        assert not Budget.objects.filter(category_id=category_id).exists()

    def test_set_null_on_created_by_delete(self):
        """Test that deleting a user sets created_by to NULL."""
        budget = BudgetFactory()
        user = budget.created_by
        user.delete()

        budget.refresh_from_db()
        assert budget.created_by is None

    def test_budget_ordering(self):
        """Test that budgets are ordered by created_at descending."""
        budget1 = BudgetFactory()
        budget2 = BudgetFactory()
        budget3 = BudgetFactory()

        project = budget1.project
        budgets = list(Budget.objects.filter(project=project))

        # Should be ordered by -created_at (most recent first)
        assert budgets[0].created_at >= budgets[1].created_at

    def test_model_indexing(self):
        """Test that model has proper indexes defined."""
        assert Budget._meta.indexes

        index_fields = set()
        for index in Budget._meta.indexes:
            index_fields.add(tuple(index.fields))

        # Check expected indexes exist
        assert ("project", "start_date") in index_fields
        assert ("project", "category") in index_fields
        assert ("alert_enabled",) in index_fields

    def test_amount_decimal_precision(self):
        """Test that amount field maintains proper decimal precision."""
        from decimal import Decimal

        budget = BudgetFactory(amount=Decimal("1234.56"))
        assert budget.amount == Decimal("1234.56")

    def test_yearly_budget_period(self):
        """Test creating a yearly budget."""
        start = timezone.now().date()
        end = start + timedelta(days=365)

        budget = BudgetFactory(
            period=Budget.Period.YEARLY,
            start_date=start,
            end_date=end
        )

        assert budget.period == Budget.Period.YEARLY

    def test_custom_budget_period(self):
        """Test creating a custom period budget."""
        start = timezone.now().date()
        end = start + timedelta(days=45)

        budget = BudgetFactory(
            period=Budget.Period.CUSTOM,
            start_date=start,
            end_date=end
        )

        assert budget.period == Budget.Period.CUSTOM
