from uuid import uuid4

from django.conf import settings
from django.db import models

from apps.projects.models import Project


class Category(models.Model):
    class CategoryType(models.TextChoices):
        INCOME = "income", "Income"
        EXPENSE = "expense", "Expense"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=CategoryType.choices)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default="#6B7280")
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="categories",
        null=True,
        blank=True,
    )
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"
        indexes = [
            models.Index(fields=["project", "category_type"]),
            models.Index(fields=["is_default"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.category_type})"


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        INCOME = "income", "Income"
        EXPENSE = "expense", "Expense"

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Cash"
        CARD = "card", "Card"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        MOBILE_PAYMENT = "mobile_payment", "Mobile Payment"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="transactions"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_transactions",
    )
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    description = models.CharField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    date = models.DateField()
    payment_method = models.CharField(
        max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH
    )
    reference_number = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list, blank=True)
    is_recurring = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["project", "date"]),
            models.Index(fields=["project", "transaction_type"]),
            models.Index(fields=["project", "category"]),
            models.Index(fields=["created_by"]),
        ]

    def __str__(self):
        return f"{self.transaction_type} — {self.amount} {self.currency} ({self.date})"
