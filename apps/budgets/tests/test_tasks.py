from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.utils import timezone

from apps.authentication.tests.factories import UserFactory
from apps.budgets.models import Budget
from apps.budgets.tasks import check_budget_alerts, send_budget_alert, _calculate_spent
from apps.projects.tests.factories import ProjectFactory
from apps.transactions.tests.factories import CategoryFactory, TransactionFactory

from .factories import BudgetFactory


@pytest.mark.django_db
class TestCalculateSpent:
    """Test the _calculate_spent helper function."""

    def test_calculate_spent_no_transactions(self):
        """Test calculation with no transactions."""
        budget = BudgetFactory()
        spent = _calculate_spent(budget)
        assert spent == Decimal("0.00")

    def test_calculate_spent_project_wide_budget(self):
        """Test calculation for project-wide budget."""
        start = timezone.now().date()
        end = start + timedelta(days=30)

        budget = BudgetFactory(
            category=None,  # Project-wide budget
            start_date=start,
            end_date=end,
        )

        # Create transactions
        TransactionFactory(
            project=budget.project,
            amount=Decimal("100.00"),
            date=start,
            transaction_type="expense",
        )
        TransactionFactory(
            project=budget.project,
            amount=Decimal("200.00"),
            date=start + timedelta(days=10),
            transaction_type="expense",
        )

        spent = _calculate_spent(budget)
        assert spent == Decimal("300.00")

    def test_calculate_spent_category_budget(self):
        """Test calculation for category-specific budget."""
        start = timezone.now().date()
        end = start + timedelta(days=30)

        category = CategoryFactory()
        budget = BudgetFactory(
            category=category,
            start_date=start,
            end_date=end,
        )

        # Create transactions in and out of category
        TransactionFactory(
            project=budget.project,
            category=category,
            amount=Decimal("150.00"),
            date=start,
            transaction_type="expense",
        )

        other_category = CategoryFactory(project=budget.project)
        TransactionFactory(
            project=budget.project,
            category=other_category,
            amount=Decimal("100.00"),
            date=start,
            transaction_type="expense",
        )

        spent = _calculate_spent(budget)
        assert spent == Decimal("150.00")  # Only the category-specific transaction

    def test_calculate_spent_ignores_income(self):
        """Test that income transactions are ignored."""
        start = timezone.now().date()
        end = start + timedelta(days=30)

        budget = BudgetFactory(start_date=start, end_date=end)

        # Create income and expense transactions
        TransactionFactory(
            project=budget.project,
            amount=Decimal("500.00"),
            date=start,
            transaction_type="income",
        )
        TransactionFactory(
            project=budget.project,
            amount=Decimal("200.00"),
            date=start,
            transaction_type="expense",
        )

        spent = _calculate_spent(budget)
        assert spent == Decimal("200.00")  # Only expenses

    def test_calculate_spent_respects_date_range(self):
        """Test that only transactions within date range are counted."""
        start = timezone.now().date()
        end = start + timedelta(days=30)

        budget = BudgetFactory(start_date=start, end_date=end)

        # Transaction within range
        TransactionFactory(
            project=budget.project,
            amount=Decimal("100.00"),
            date=start + timedelta(days=15),
            transaction_type="expense",
        )

        # Transaction before range
        TransactionFactory(
            project=budget.project,
            amount=Decimal("200.00"),
            date=start - timedelta(days=1),
            transaction_type="expense",
        )

        # Transaction after range
        TransactionFactory(
            project=budget.project,
            amount=Decimal("300.00"),
            date=end + timedelta(days=1),
            transaction_type="expense",
        )

        spent = _calculate_spent(budget)
        assert spent == Decimal("100.00")  # Only the transaction within range


@pytest.mark.django_db
class TestSendBudgetAlert:
    """Test the send_budget_alert Celery task."""

    @patch("apps.budgets.tasks.send_mail")
    def test_send_alert_to_creator(self, mock_send_mail):
        """Test that alert is sent to budget creator."""
        user = UserFactory(first_name="John", email="john@example.com")
        project = ProjectFactory(owner=user)
        budget = BudgetFactory(project=project, created_by=user)

        send_budget_alert(
            budget_id=str(budget.id),
            spent=500.0,
            allocated=1000.0,
            percentage_used=50.0,
        )

        mock_send_mail.assert_called_once()
        call_args = mock_send_mail.call_args

        assert "john@example.com" in call_args[1]["recipient_list"]
        assert "Budget Alert" in call_args[1]["subject"]
        assert "50.0" in call_args[1]["message"]

    @patch("apps.budgets.tasks.send_mail")
    def test_send_alert_to_multiple_recipients(self, mock_send_mail):
        """Test that alert is sent to both creator and project owner."""
        owner = UserFactory(email="owner@example.com")
        creator = UserFactory(email="creator@example.com")
        project = ProjectFactory(owner=owner)
        budget = BudgetFactory(project=project, created_by=creator)

        send_budget_alert(
            budget_id=str(budget.id),
            spent=800.0,
            allocated=1000.0,
            percentage_used=80.0,
        )

        mock_send_mail.assert_called_once()
        call_args = mock_send_mail.call_args

        recipients = call_args[1]["recipient_list"]
        assert "owner@example.com" in recipients
        assert "creator@example.com" in recipients

    @patch("apps.budgets.tasks.send_mail")
    def test_send_alert_includes_category_name(self, mock_send_mail):
        """Test that alert includes category name in subject and message."""
        user = UserFactory(email="user@example.com")
        project = ProjectFactory(owner=user)
        category = CategoryFactory(name="Travel")
        budget = BudgetFactory(
            project=project,
            category=category,
            created_by=user,
        )

        send_budget_alert(
            budget_id=str(budget.id),
            spent=400.0,
            allocated=500.0,
            percentage_used=80.0,
        )

        mock_send_mail.assert_called_once()
        call_args = mock_send_mail.call_args

        assert "Travel" in call_args[1]["subject"]
        assert "Travel" in call_args[1]["message"]

    @patch("apps.budgets.tasks.send_mail")
    def test_send_alert_with_nonexistent_budget(self, mock_send_mail):
        """Test that function handles nonexistent budget gracefully."""
        import uuid

        send_budget_alert(
            budget_id=str(uuid.uuid4()),
            spent=100.0,
            allocated=1000.0,
            percentage_used=10.0,
        )

        mock_send_mail.assert_not_called()


@pytest.mark.django_db
class TestCheckBudgetAlerts:
    """Test the check_budget_alerts Celery task."""

    @patch("apps.budgets.tasks.send_budget_alert.delay")
    def test_check_alerts_above_threshold(self, mock_send_alert):
        """Test that alerts are sent for budgets above threshold."""
        start = timezone.now().date()
        end = start + timedelta(days=30)

        user = UserFactory()
        project = ProjectFactory(owner=user)

        budget = BudgetFactory(
            project=project,
            amount=Decimal("1000.00"),
            start_date=start,
            end_date=end,
            alert_threshold=80,
            alert_enabled=True,
            created_by=user,
        )

        # Create transactions to exceed threshold
        TransactionFactory(
            project=project,
            amount=Decimal("850.00"),
            date=start,
            transaction_type="expense",
        )

        check_budget_alerts()

        mock_send_alert.assert_called_once()
        call_args = mock_send_alert.call_args
        assert str(budget.id) == call_args[1]["budget_id"]
        assert call_args[1]["percentage_used"] >= 80.0

    @patch("apps.budgets.tasks.send_budget_alert.delay")
    def test_check_alerts_below_threshold(self, mock_send_alert):
        """Test that no alerts are sent for budgets below threshold."""
        start = timezone.now().date()
        end = start + timedelta(days=30)

        user = UserFactory()
        project = ProjectFactory(owner=user)

        budget = BudgetFactory(
            project=project,
            amount=Decimal("1000.00"),
            start_date=start,
            end_date=end,
            alert_threshold=80,
            alert_enabled=True,
            created_by=user,
        )

        # Create transactions below threshold
        TransactionFactory(
            project=project,
            amount=Decimal("500.00"),
            date=start,
            transaction_type="expense",
        )

        check_budget_alerts()

        mock_send_alert.assert_not_called()

    @patch("apps.budgets.tasks.send_budget_alert.delay")
    def test_check_alerts_disabled(self, mock_send_alert):
        """Test that disabled alerts are not checked."""
        start = timezone.now().date()
        end = start + timedelta(days=30)

        user = UserFactory()
        project = ProjectFactory(owner=user)

        budget = BudgetFactory(
            project=project,
            amount=Decimal("1000.00"),
            start_date=start,
            end_date=end,
            alert_threshold=80,
            alert_enabled=False,  # Disabled
            created_by=user,
        )

        # Create transactions above threshold
        TransactionFactory(
            project=project,
            amount=Decimal("850.00"),
            date=start,
            transaction_type="expense",
        )

        check_budget_alerts()

        mock_send_alert.assert_not_called()

    @patch("apps.budgets.tasks.send_budget_alert.delay")
    def test_check_alerts_outside_date_range(self, mock_send_alert):
        """Test that budgets outside their date range are skipped."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        start = timezone.now().date() + timedelta(days=10)
        end = start + timedelta(days=30)

        budget = BudgetFactory(
            project=project,
            amount=Decimal("1000.00"),
            start_date=start,
            end_date=end,
            alert_enabled=True,
            created_by=user,
        )

        check_budget_alerts()

        mock_send_alert.assert_not_called()

    @patch("apps.budgets.tasks.send_budget_alert.delay")
    def test_check_multiple_budgets(self, mock_send_alert):
        """Test checking multiple budgets at once."""
        start = timezone.now().date()
        end = start + timedelta(days=30)

        user = UserFactory()
        project = ProjectFactory(owner=user)

        # Budget above threshold
        budget1 = BudgetFactory(
            project=project,
            amount=Decimal("1000.00"),
            start_date=start,
            end_date=end,
            alert_threshold=80,
            alert_enabled=True,
            created_by=user,
        )

        # Budget below threshold
        budget2 = BudgetFactory(
            project=project,
            amount=Decimal("1000.00"),
            start_date=start,
            end_date=end,
            alert_threshold=80,
            alert_enabled=True,
            created_by=user,
        )

        # Create transactions
        TransactionFactory(
            project=project,
            amount=Decimal("900.00"),
            date=start,
            transaction_type="expense",
        )
        TransactionFactory(
            project=project,
            amount=Decimal("200.00"),
            date=start + timedelta(days=1),
            transaction_type="expense",
        )

        check_budget_alerts()

        # Only one alert should be sent (for budget1 which is 90% spent)
        assert mock_send_alert.call_count == 1

    @patch("apps.budgets.tasks.send_budget_alert.delay")
    def test_check_alerts_with_category_filter(self, mock_send_alert):
        """Test that category budgets only count category transactions."""
        start = timezone.now().date()
        end = start + timedelta(days=30)

        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project)

        budget = BudgetFactory(
            project=project,
            category=category,
            amount=Decimal("500.00"),
            start_date=start,
            end_date=end,
            alert_threshold=80,
            alert_enabled=True,
            created_by=user,
        )

        # Create transactions in and out of category
        TransactionFactory(
            project=project,
            category=category,
            amount=Decimal("450.00"),
            date=start,
            transaction_type="expense",
        )

        other_category = CategoryFactory(project=project)
        TransactionFactory(
            project=project,
            category=other_category,
            amount=Decimal("1000.00"),
            date=start,
            transaction_type="expense",
        )

        check_budget_alerts()

        # Should trigger alert for category budget (90% spent)
        mock_send_alert.assert_called_once()
