from celery import shared_task
from decimal import Decimal
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from apps.transactions.models import Transaction
from .models import Budget


@shared_task
def check_budget_alerts():
    """
    Check all active budgets and send alerts if spending exceeds threshold.
    This task is meant to be run periodically via Celery Beat (e.g., daily).
    """
    # Get all budgets with alerts enabled
    budgets = Budget.objects.filter(alert_enabled=True).select_related(
        "project", "category", "created_by"
    )

    for budget in budgets:
        # Check if we're within the budget period
        today = timezone.now().date()
        if today < budget.start_date or today > budget.end_date:
            continue

        # Calculate spent amount
        spent = _calculate_spent(budget)

        # Check if alert threshold is exceeded
        if budget.amount > 0:
            percentage_used = (spent / budget.amount) * 100
        else:
            percentage_used = 0

        if percentage_used >= budget.alert_threshold:
            # Send alert email to budget creator and project owner
            send_budget_alert.delay(
                budget_id=str(budget.id),
                spent=float(spent),
                allocated=float(budget.amount),
                percentage_used=float(percentage_used),
            )


@shared_task
def send_budget_alert(budget_id, spent, allocated, percentage_used):
    """
    Send an email alert when budget threshold is exceeded.
    """
    try:
        budget = Budget.objects.select_related("project", "category", "created_by").get(
            id=budget_id
        )
    except Budget.DoesNotExist:
        return

    # Prepare email details
    category_name = budget.category.name if budget.category else "All Categories"
    project_name = budget.project.name
    subject = f"Budget Alert: {project_name} - {category_name}"

    message = (
        f"Hi {budget.created_by.first_name or budget.created_by.email},\n\n"
        f"You have reached {percentage_used:.1f}% of your budget for "
        f"{category_name} in {project_name}.\n\n"
        f"Budget Details:\n"
        f"  Allocated: ${allocated:,.2f}\n"
        f"  Spent: ${spent:,.2f}\n"
        f"  Remaining: ${allocated - spent:,.2f}\n"
        f"  Alert Threshold: {budget.alert_threshold}%\n\n"
        f"Please review your spending and make adjustments if needed.\n\n"
        f"Best regards,\n"
        f"Expense Tracker Team"
    )

    recipients = [budget.created_by.email]

    # Also notify project owner if they're not the budget creator
    if budget.project.owner != budget.created_by:
        recipients.append(budget.project.owner.email)

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipients,
        fail_silently=True,
    )


def _calculate_spent(budget):
    """
    Calculate the amount spent within a budget's period.
    """
    filter_kwargs = {
        "project": budget.project,
        "transaction_type": "expense",
        "date__gte": budget.start_date,
        "date__lte": budget.end_date,
    }

    # If budget has a category, filter by category
    if budget.category:
        filter_kwargs["category"] = budget.category

    transactions = Transaction.objects.filter(**filter_kwargs)
    spent = sum(t.amount for t in transactions) or Decimal("0.00")
    return spent
