from uuid import uuid4

from django.conf import settings
from django.db import models

from apps.projects.models import Project
from apps.transactions.models import Category


class Budget(models.Model):
    """Budget model for tracking spending limits across projects and categories."""

    class Period(models.TextChoices):
        """Budget period choices."""

        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        YEARLY = "yearly", "Yearly"
        CUSTOM = "custom", "Custom"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="budgets"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="budgets",
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    period = models.CharField(
        max_length=20, choices=Period.choices, default=Period.MONTHLY
    )
    start_date = models.DateField()
    end_date = models.DateField()
    alert_threshold = models.IntegerField(default=80)  # Percentage (0-100)
    alert_enabled = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_budgets",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project", "start_date"]),
            models.Index(fields=["project", "category"]),
            models.Index(fields=["alert_enabled"]),
        ]

    def __str__(self):
        category_name = self.category.name if self.category else "All Categories"
        return f"{self.project.name} - {category_name} ({self.amount} {self.project.currency})"
