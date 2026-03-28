"""
Tests for budgets/tasks.py - Celery task tests for budget alerts.

Tests:
- check_budget_alerts - Check all active budgets and trigger alerts
- send_budget_alert - Send email alerts when budget threshold exceeded
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.utils import timezone

from apps.budgets.tasks import check_budget_alerts, send_budget_alert
from apps.budgets.tests.factories import BudgetFactory
from apps.transactions.tests.factories import TransactionFactory, CategoryFactory
from apps.projects.tests.factories import ProjectFactory
from apps.authentication.tests.factories import UserFactory


@pytest.mark.django_db
class TestCheckBudgetAlerts:
    """Test check_budget_alerts task."""

    def test_check_budget_alerts_skips_inactive_budgets(self):
        """Test that budgets outside their period are skipped."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        # Future budget
        future_start = timezone.now().date() + timedelta(days=10)
        future_end = future_start + timedelta(days=30)

        budget = BudgetFactory(
            project=project,
            created_by=user,
            amount=Decimal("1000.00"),
            start_date=future_start,
            end_date=future_end,
            alert_enabled=True,
            alert_threshold=80,
        )

        with patch("apps.budgets.tasks.send_budget_alert.delay") as mock_send:
            check_budget_alerts()
            mock_send.assert_not_called()

    def test_check_budget_alerts_skips_disabled_alerts(self):
        """Test that budgets with alerts disabled are skipped."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        start = timezone.now().date() - timedelta(days=10)
        end = timezone.now().date() + timedelta(days=20)

        budget = BudgetFactory(
            project=project,
            created_by=user,
            amount=Decimal("1000.00"),
            start_date=start,
            end_date=end,
            alert_enabled=False,  # Alerts disabled
            alert_threshold=80,
        )

        with patch("apps.budgets.tasks.send_budget_alert.delay") as mock_send:
            check_budget_alerts()
            mock_send.assert_not_called()

    def test_check_budget_alerts_handles_zero_budget(self):
        """Test that zero budget is handled gracefully."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        start = timezone.now().date() - timedelta(days=5)
        end = timezone.now().date() + timedelta(days=5)

        budget = BudgetFactory(
            project=project,
            created_by=user,
            amount=Decimal("0.00"),
            start_date=start,
            end_date=end,
            alert_enabled=True,
        )

        with patch("apps.budgets.tasks.send_budget_alert.delay") as mock_send:
            check_budget_alerts()


@pytest.mark.django_db
class TestSendBudgetAlert:
    """Test send_budget_alert task."""

    def test_send_budget_alert_valid_budget(self):
        """Test that alert is sent for valid budget."""
        user = UserFactory(first_name="John", email="john@example.com")
        project = ProjectFactory(owner=user, name="Q4 Planning")
        category = CategoryFactory(project=project, name="Travel")

        budget = BudgetFactory(
            project=project,
            created_by=user,
            category=category,
        )

        with patch("apps.budgets.tasks.send_mail") as mock_mail:
            send_budget_alert(
                budget_id=str(budget.id),
                spent=800.0,
                allocated=1000.0,
                percentage_used=80.0,
            )

            mock_mail.assert_called_once()

    def test_send_budget_alert_email_content(self):
        """Test that alert email contains required information."""
        user = UserFactory(first_name="Jane", email="jane@example.com")
        project = ProjectFactory(name="Team Budget")
        category = CategoryFactory(name="Food")

        budget = BudgetFactory(
            project=project,
            created_by=user,
            category=category,
        )

        with patch("apps.budgets.tasks.send_mail") as mock_mail:
            send_budget_alert(
                budget_id=str(budget.id),
                spent=750.0,
                allocated=1000.0,
                percentage_used=75.0,
            )

            mock_mail.assert_called_once()

    def test_send_budget_alert_nonexistent_budget(self):
        """Test that task handles nonexistent budget gracefully."""
        with patch("apps.budgets.tasks.send_mail") as mock_mail:
            send_budget_alert(
                budget_id="nonexistent-id",
                spent=100.0,
                allocated=1000.0,
                percentage_used=10.0,
            )

            mock_mail.assert_not_called()

    def test_send_budget_alert_project_wide_budget(self):
        """Test alert for project-wide budget (no category)."""
        user = UserFactory(email="user@example.com")
        project = ProjectFactory(name="All Expenses")

        budget = BudgetFactory(
            project=project,
            created_by=user,
            category=None,
        )

        with patch("apps.budgets.tasks.send_mail") as mock_mail:
            send_budget_alert(
                budget_id=str(budget.id),
                spent=500.0,
                allocated=1000.0,
                percentage_used=50.0,
            )

            mock_mail.assert_called_once()

    def test_send_budget_alert_high_percentage(self):
        """Test alert for very high budget usage."""
        user = UserFactory(email="user@example.com")
        project = ProjectFactory()

        budget = BudgetFactory(
            project=project,
            created_by=user,
        )

        with patch("apps.budgets.tasks.send_mail") as mock_mail:
            send_budget_alert(
                budget_id=str(budget.id),
                spent=950.0,
                allocated=1000.0,
                percentage_used=95.0,
            )

            mock_mail.assert_called_once()
