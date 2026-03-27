"""
Utilities for generating financial reports and analytics.
"""
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Q

from apps.transactions.models import Transaction


class ReportCalculator:
    """Helper class for calculating various financial reports."""

    @staticmethod
    def get_summary(project, start_date=None, end_date=None):
        """
        Calculate financial summary for a project.

        Returns:
            dict with total_income, total_expenses, net, transaction_count
        """
        if not start_date:
            start_date = timezone.now().date() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now().date()

        transactions = Transaction.objects.filter(
            project=project,
            date__gte=start_date,
            date__lte=end_date,
        )

        income = (
            transactions.filter(transaction_type="income").aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        expenses = (
            transactions.filter(transaction_type="expense").aggregate(
                total=Sum("amount")
            )["total"]
            or Decimal("0.00")
        )

        net = income - expenses

        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "total_income": income,
            "total_expenses": expenses,
            "net": net,
            "transaction_count": transactions.count(),
        }

    @staticmethod
    def get_category_breakdown(project, start_date=None, end_date=None):
        """
        Get breakdown of spending by category.

        Returns:
            list of dicts with category name, amount, percentage, count
        """
        if not start_date:
            start_date = timezone.now().date() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now().date()

        # Get total expenses for percentage calculation
        total_expenses = (
            Transaction.objects.filter(
                project=project,
                transaction_type="expense",
                date__gte=start_date,
                date__lte=end_date,
            ).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        # Group by category
        category_data = (
            Transaction.objects.filter(
                project=project,
                transaction_type="expense",
                date__gte=start_date,
                date__lte=end_date,
            )
            .values("category__id", "category__name")
            .annotate(amount=Sum("amount"), count=Sum(1))
            .order_by("-amount")
        )

        breakdown = []
        for item in category_data:
            amount = item["amount"] or Decimal("0.00")
            percentage = (
                (amount / total_expenses * 100) if total_expenses > 0 else 0
            )

            breakdown.append({
                "category_id": str(item["category__id"]),
                "category": item["category__name"],
                "amount": amount,
                "percentage": float(percentage),
                "count": item["count"],
            })

        return breakdown

    @staticmethod
    def get_trends(project, start_date=None, end_date=None, granularity="day"):
        """
        Get spending trends over time.

        Args:
            granularity: 'day', 'week', or 'month'

        Returns:
            list of dicts with date/period, income, expenses, net
        """
        if not start_date:
            start_date = timezone.now().date() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now().date()

        transactions = Transaction.objects.filter(
            project=project,
            date__gte=start_date,
            date__lte=end_date,
        )

        # Group by date (day-level granularity)
        daily_data = {}
        for txn in transactions:
            date_key = txn.date.isoformat()
            if date_key not in daily_data:
                daily_data[date_key] = {
                    "date": date_key,
                    "income": Decimal("0.00"),
                    "expenses": Decimal("0.00"),
                }

            if txn.transaction_type == "income":
                daily_data[date_key]["income"] += txn.amount
            else:
                daily_data[date_key]["expenses"] += txn.amount

        # Calculate net for each day
        for data in daily_data.values():
            data["net"] = data["income"] - data["expenses"]

        # Sort by date
        trends = sorted(daily_data.values(), key=lambda x: x["date"])

        return trends

    @staticmethod
    def get_period_comparison(project, current_period_days=30):
        """
        Compare current period with previous period.

        Returns:
            dict with current and previous period stats and % changes
        """
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=current_period_days)

        previous_end = start_date - timedelta(days=1)
        previous_start = previous_end - timedelta(days=current_period_days)

        current = ReportCalculator.get_summary(
            project, start_date, end_date
        )
        previous = ReportCalculator.get_summary(
            project, previous_start, previous_end
        )

        # Calculate percentage changes
        def calc_change(current_val, previous_val):
            if previous_val == 0:
                return 0 if current_val == 0 else 100
            return float(((current_val - previous_val) / previous_val) * 100)

        return {
            "current_period": current,
            "previous_period": previous,
            "changes": {
                "income_change_pct": calc_change(
                    current["total_income"], previous["total_income"]
                ),
                "expense_change_pct": calc_change(
                    current["total_expenses"], previous["total_expenses"]
                ),
                "net_change_pct": calc_change(
                    current["net"], previous["net"]
                ),
            },
        }

    @staticmethod
    def get_monthly_report(project, year=None, month=None):
        """
        Get detailed report for a specific month.

        Returns:
            dict with summary, category breakdown, daily trends, and budget status
        """
        if not year:
            year = timezone.now().year
        if not month:
            month = timezone.now().month

        from datetime import date as date_class
        from calendar import monthrange

        # Calculate month boundaries
        days_in_month = monthrange(year, month)[1]
        start_date = date_class(year, month, 1)
        end_date = date_class(year, month, days_in_month)

        summary = ReportCalculator.get_summary(project, start_date, end_date)
        breakdown = ReportCalculator.get_category_breakdown(
            project, start_date, end_date
        )
        trends = ReportCalculator.get_trends(
            project, start_date, end_date, granularity="day"
        )

        # Get budget status if budgets exist
        from apps.budgets.models import Budget
        from apps.budgets.views import BudgetStatusView

        budgets = Budget.objects.filter(
            project=project,
            start_date__lte=end_date,
            end_date__gte=start_date,
        )

        budget_status = []
        budget_view = BudgetStatusView()
        for budget in budgets:
            spent = budget_view._calculate_spent(budget)
            percentage_used = (spent / budget.amount * 100) if budget.amount > 0 else 0
            budget_status.append({
                "budget_id": str(budget.id),
                "category": budget.category.name if budget.category else "All Categories",
                "allocated": float(budget.amount),
                "spent": float(spent),
                "remaining": float(budget.amount - spent),
                "percentage_used": float(percentage_used),
            })

        return {
            "year": year,
            "month": month,
            "summary": summary,
            "by_category": breakdown,
            "daily_trends": trends,
            "budget_status": budget_status,
        }

    @staticmethod
    def get_comparison_report(project, start_date1, end_date1, start_date2, end_date2):
        """
        Compare two arbitrary date ranges.

        Returns:
            dict comparing two periods side by side
        """
        period1 = ReportCalculator.get_summary(project, start_date1, end_date1)
        period2 = ReportCalculator.get_summary(project, start_date2, end_date2)

        breakdown1 = ReportCalculator.get_category_breakdown(
            project, start_date1, end_date1
        )
        breakdown2 = ReportCalculator.get_category_breakdown(
            project, start_date2, end_date2
        )

        return {
            "period_1": {
                "start": start_date1.isoformat(),
                "end": end_date1.isoformat(),
                "summary": period1,
                "by_category": breakdown1,
            },
            "period_2": {
                "start": start_date2.isoformat(),
                "end": end_date2.isoformat(),
                "summary": period2,
                "by_category": breakdown2,
            },
        }
