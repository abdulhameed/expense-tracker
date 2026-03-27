from django.contrib import admin

from .models import Budget


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "project",
        "category",
        "amount",
        "period",
        "start_date",
        "end_date",
        "alert_threshold",
        "alert_enabled",
        "created_at",
    ]
    list_filter = ["period", "alert_enabled", "created_at"]
    search_fields = ["project__name", "category__name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "id",
                    "project",
                    "category",
                    "amount",
                )
            },
        ),
        (
            "Period & Dates",
            {
                "fields": (
                    "period",
                    "start_date",
                    "end_date",
                )
            },
        ),
        (
            "Alerts",
            {
                "fields": (
                    "alert_enabled",
                    "alert_threshold",
                )
            },
        ),
        (
            "Metadata",
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
