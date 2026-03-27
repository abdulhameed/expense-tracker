from datetime import timedelta, date
from decimal import Decimal

import pytest
from django.utils import timezone

from apps.authentication.tests.factories import UserFactory, VerifiedUserFactory
from apps.projects.tests.factories import ProjectFactory
from apps.transactions.tests.factories import CategoryFactory, TransactionFactory
from apps.budgets.tests.factories import BudgetFactory

from apps.reports.utils import ReportCalculator


@pytest.mark.django_db
class TestReportCalculatorSummary:
    """Test summary report calculations."""

    def test_summary_empty_project(self):
        """Test summary with no transactions."""
        project = ProjectFactory()
        summary = ReportCalculator.get_summary(project)

        assert summary["total_income"] == Decimal("0.00")
        assert summary["total_expenses"] == Decimal("0.00")
        assert summary["net"] == Decimal("0.00")
        assert summary["transaction_count"] == 0

    def test_summary_with_expenses(self):
        """Test summary with only expenses."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        start = timezone.now().date() - timedelta(days=15)
        end = timezone.now().date()

        TransactionFactory(
            project=project,
            amount=Decimal("100.00"),
            transaction_type="expense",
            date=start,
            created_by=user,
        )
        TransactionFactory(
            project=project,
            amount=Decimal("200.00"),
            transaction_type="expense",
            date=start + timedelta(days=5),
            created_by=user,
        )

        summary = ReportCalculator.get_summary(project, start, end)

        assert summary["total_income"] == Decimal("0.00")
        assert summary["total_expenses"] == Decimal("300.00")
        assert summary["net"] == Decimal("-300.00")
        assert summary["transaction_count"] == 2

    def test_summary_with_income_and_expenses(self):
        """Test summary with both income and expenses."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        start = timezone.now().date() - timedelta(days=15)
        end = timezone.now().date()

        TransactionFactory(
            project=project,
            amount=Decimal("500.00"),
            transaction_type="income",
            date=start,
            created_by=user,
        )
        TransactionFactory(
            project=project,
            amount=Decimal("200.00"),
            transaction_type="expense",
            date=start + timedelta(days=5),
            created_by=user,
        )

        summary = ReportCalculator.get_summary(project, start, end)

        assert summary["total_income"] == Decimal("500.00")
        assert summary["total_expenses"] == Decimal("200.00")
        assert summary["net"] == Decimal("300.00")

    def test_summary_respects_date_range(self):
        """Test that only transactions in date range are counted."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        start = timezone.now().date()
        end = start + timedelta(days=10)

        # Transaction within range
        TransactionFactory(
            project=project,
            amount=Decimal("100.00"),
            transaction_type="expense",
            date=start,
            created_by=user,
        )

        # Transaction before range
        TransactionFactory(
            project=project,
            amount=Decimal("200.00"),
            transaction_type="expense",
            date=start - timedelta(days=1),
            created_by=user,
        )

        # Transaction after range
        TransactionFactory(
            project=project,
            amount=Decimal("300.00"),
            transaction_type="expense",
            date=end + timedelta(days=1),
            created_by=user,
        )

        summary = ReportCalculator.get_summary(project, start, end)

        assert summary["total_expenses"] == Decimal("100.00")
        assert summary["transaction_count"] == 1

    def test_summary_default_date_range(self):
        """Test that default date range is 30 days."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        # Create transaction within last 30 days
        TransactionFactory(
            project=project,
            amount=Decimal("100.00"),
            transaction_type="expense",
            date=timezone.now().date() - timedelta(days=15),
            created_by=user,
        )

        # Create transaction older than 30 days
        TransactionFactory(
            project=project,
            amount=Decimal("200.00"),
            transaction_type="expense",
            date=timezone.now().date() - timedelta(days=40),
            created_by=user,
        )

        summary = ReportCalculator.get_summary(project)

        assert summary["total_expenses"] == Decimal("100.00")


@pytest.mark.django_db
class TestReportCalculatorCategoryBreakdown:
    """Test category breakdown calculations."""

    def test_breakdown_empty(self):
        """Test breakdown with no transactions."""
        project = ProjectFactory()
        breakdown = ReportCalculator.get_category_breakdown(project)

        assert len(breakdown) == 0

    def test_breakdown_single_category(self):
        """Test breakdown with single category."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project)

        start = timezone.now().date() - timedelta(days=15)
        end = timezone.now().date()

        TransactionFactory(
            project=project,
            category=category,
            amount=Decimal("100.00"),
            transaction_type="expense",
            date=start,
            created_by=user,
        )

        breakdown = ReportCalculator.get_category_breakdown(project, start, end)

        assert len(breakdown) == 1
        assert breakdown[0]["category"] == category.name
        assert breakdown[0]["amount"] == Decimal("100.00")
        assert breakdown[0]["percentage"] == 100.0

    def test_breakdown_multiple_categories(self):
        """Test breakdown with multiple categories."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        cat1 = CategoryFactory(project=project, name="Food")
        cat2 = CategoryFactory(project=project, name="Transport")

        start = timezone.now().date() - timedelta(days=15)
        end = timezone.now().date()

        TransactionFactory(
            project=project,
            category=cat1,
            amount=Decimal("300.00"),
            transaction_type="expense",
            date=start,
            created_by=user,
        )
        TransactionFactory(
            project=project,
            category=cat2,
            amount=Decimal("200.00"),
            transaction_type="expense",
            date=start,
            created_by=user,
        )

        breakdown = ReportCalculator.get_category_breakdown(project, start, end)

        assert len(breakdown) == 2
        assert breakdown[0]["amount"] == Decimal("300.00")  # Higher amount first
        assert breakdown[0]["percentage"] == 60.0
        assert breakdown[1]["percentage"] == 40.0

    def test_breakdown_ignores_income(self):
        """Test that income transactions are excluded."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project)

        start = timezone.now().date() - timedelta(days=15)
        end = timezone.now().date()

        TransactionFactory(
            project=project,
            category=category,
            amount=Decimal("500.00"),
            transaction_type="income",
            date=start,
            created_by=user,
        )
        TransactionFactory(
            project=project,
            category=category,
            amount=Decimal("100.00"),
            transaction_type="expense",
            date=start,
            created_by=user,
        )

        breakdown = ReportCalculator.get_category_breakdown(project, start, end)

        assert len(breakdown) == 1
        assert breakdown[0]["amount"] == Decimal("100.00")


@pytest.mark.django_db
class TestReportCalculatorTrends:
    """Test trend analysis."""

    def test_trends_empty(self):
        """Test trends with no transactions."""
        project = ProjectFactory()
        trends = ReportCalculator.get_trends(project)

        assert len(trends) == 0

    def test_trends_single_day(self):
        """Test trends with single day of transactions."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        date = timezone.now().date()

        TransactionFactory(
            project=project,
            amount=Decimal("100.00"),
            transaction_type="income",
            date=date,
            created_by=user,
        )
        TransactionFactory(
            project=project,
            amount=Decimal("50.00"),
            transaction_type="expense",
            date=date,
            created_by=user,
        )

        trends = ReportCalculator.get_trends(project, date, date)

        assert len(trends) == 1
        assert trends[0]["date"] == date.isoformat()
        assert trends[0]["income"] == Decimal("100.00")
        assert trends[0]["expenses"] == Decimal("50.00")
        assert trends[0]["net"] == Decimal("50.00")

    def test_trends_multiple_days(self):
        """Test trends across multiple days."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        start = timezone.now().date()

        TransactionFactory(
            project=project,
            amount=Decimal("100.00"),
            transaction_type="expense",
            date=start,
            created_by=user,
        )
        TransactionFactory(
            project=project,
            amount=Decimal("200.00"),
            transaction_type="expense",
            date=start + timedelta(days=1),
            created_by=user,
        )

        trends = ReportCalculator.get_trends(project, start, start + timedelta(days=1))

        assert len(trends) == 2
        assert trends[0]["expenses"] == Decimal("100.00")
        assert trends[1]["expenses"] == Decimal("200.00")

    def test_trends_ordered_by_date(self):
        """Test that trends are ordered chronologically."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        start = timezone.now().date()

        # Create in reverse order
        TransactionFactory(
            project=project,
            amount=Decimal("300.00"),
            transaction_type="expense",
            date=start + timedelta(days=2),
            created_by=user,
        )
        TransactionFactory(
            project=project,
            amount=Decimal("100.00"),
            transaction_type="expense",
            date=start,
            created_by=user,
        )
        TransactionFactory(
            project=project,
            amount=Decimal("200.00"),
            transaction_type="expense",
            date=start + timedelta(days=1),
            created_by=user,
        )

        trends = ReportCalculator.get_trends(
            project, start, start + timedelta(days=2)
        )

        # Should be ordered by date
        assert trends[0]["date"] == start.isoformat()
        assert trends[1]["date"] == (start + timedelta(days=1)).isoformat()
        assert trends[2]["date"] == (start + timedelta(days=2)).isoformat()


@pytest.mark.django_db
class TestReportCalculatorPeriodComparison:
    """Test period comparison."""

    def test_period_comparison_no_transactions(self):
        """Test period comparison with no transactions."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        comparison = ReportCalculator.get_period_comparison(project, 30)

        assert "current_period" in comparison
        assert "previous_period" in comparison
        assert "changes" in comparison
        assert comparison["current_period"]["total_expenses"] == Decimal("0.00")

    def test_period_comparison_with_data(self):
        """Test period comparison with transactions."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        # Create transactions in current period
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=29)

        TransactionFactory(
            project=project,
            amount=Decimal("500.00"),
            transaction_type="income",
            date=end_date - timedelta(days=10),
            created_by=user,
        )
        TransactionFactory(
            project=project,
            amount=Decimal("200.00"),
            transaction_type="expense",
            date=end_date - timedelta(days=10),
            created_by=user,
        )

        # Create transactions in previous period
        prev_start = start_date - timedelta(days=30)
        prev_end = start_date - timedelta(days=1)

        TransactionFactory(
            project=project,
            amount=Decimal("300.00"),
            transaction_type="income",
            date=prev_start + timedelta(days=10),
            created_by=user,
        )
        TransactionFactory(
            project=project,
            amount=Decimal("100.00"),
            transaction_type="expense",
            date=prev_start + timedelta(days=10),
            created_by=user,
        )

        comparison = ReportCalculator.get_period_comparison(project, 30)

        assert "changes" in comparison
        # Income increased from 300 to 500 (+66.7%)
        assert comparison["changes"]["income_change_pct"] > 0
        # Expenses increased from 100 to 200 (+100%)
        assert comparison["changes"]["expense_change_pct"] > 0


@pytest.mark.django_db
class TestReportCalculatorMonthlyReport:
    """Test monthly report generation."""

    def test_monthly_report_current_month(self):
        """Test monthly report for current month."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        # Create transaction this month
        today = timezone.now().date()
        TransactionFactory(
            project=project,
            amount=Decimal("100.00"),
            transaction_type="expense",
            date=today,
            created_by=user,
        )

        report = ReportCalculator.get_monthly_report(project)

        assert report["year"] == today.year
        assert report["month"] == today.month
        assert "summary" in report
        assert "by_category" in report
        assert "daily_trends" in report
        assert "budget_status" in report
        assert report["summary"]["total_expenses"] == Decimal("100.00")

    def test_monthly_report_specific_month(self):
        """Test monthly report for specific month."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        # Create transaction in January 2026
        TransactionFactory(
            project=project,
            amount=Decimal("150.00"),
            transaction_type="expense",
            date=date(2026, 1, 15),
            created_by=user,
        )

        report = ReportCalculator.get_monthly_report(project, 2026, 1)

        assert report["year"] == 2026
        assert report["month"] == 1
        assert report["summary"]["total_expenses"] == Decimal("150.00")

    def test_monthly_report_includes_budget_status(self):
        """Test that monthly report includes budget status."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        # Create budget for current month
        today = timezone.now().date()
        month_start = date(today.year, today.month, 1)
        if today.month == 12:
            month_end = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(today.year, today.month + 1, 1) - timedelta(days=1)

        budget = BudgetFactory(
            project=project,
            amount=Decimal("1000.00"),
            start_date=month_start,
            end_date=month_end,
            created_by=user,
        )

        report = ReportCalculator.get_monthly_report(project, today.year, today.month)

        assert len(report["budget_status"]) > 0
        assert report["budget_status"][0]["budget_id"] == str(budget.id)


@pytest.mark.django_db
class TestReportCalculatorComparisonReport:
    """Test arbitrary period comparison."""

    def test_comparison_report(self):
        """Test comparison of two arbitrary periods."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        start1 = date(2026, 1, 1)
        end1 = date(2026, 1, 31)
        start2 = date(2026, 2, 1)
        end2 = date(2026, 2, 28)

        # Period 1 transactions
        TransactionFactory(
            project=project,
            amount=Decimal("500.00"),
            transaction_type="income",
            date=start1 + timedelta(days=5),
            created_by=user,
        )
        TransactionFactory(
            project=project,
            amount=Decimal("200.00"),
            transaction_type="expense",
            date=start1 + timedelta(days=5),
            created_by=user,
        )

        # Period 2 transactions
        TransactionFactory(
            project=project,
            amount=Decimal("600.00"),
            transaction_type="income",
            date=start2 + timedelta(days=5),
            created_by=user,
        )
        TransactionFactory(
            project=project,
            amount=Decimal("300.00"),
            transaction_type="expense",
            date=start2 + timedelta(days=5),
            created_by=user,
        )

        report = ReportCalculator.get_comparison_report(
            project, start1, end1, start2, end2
        )

        assert "period_1" in report
        assert "period_2" in report
        assert report["period_1"]["summary"]["total_income"] == Decimal("500.00")
        assert report["period_2"]["summary"]["total_income"] == Decimal("600.00")
