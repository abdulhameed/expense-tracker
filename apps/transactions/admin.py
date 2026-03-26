from django.contrib import admin

from .models import Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "category_type", "project", "is_default", "created_at"]
    list_filter = ["category_type", "is_default"]
    search_fields = ["name"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "date",
        "transaction_type",
        "amount",
        "currency",
        "project",
        "category",
        "created_by",
    ]
    list_filter = ["transaction_type", "payment_method", "is_recurring"]
    search_fields = ["description", "reference_number"]
    date_hierarchy = "date"
