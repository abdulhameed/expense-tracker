from django.contrib import admin

from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    """Admin interface for ActivityLog."""

    list_display = [
        "id",
        "action",
        "content_type",
        "user",
        "project",
        "description",
        "created_at",
    ]
    list_filter = [
        "action",
        "content_type",
        "created_at",
        "project",
    ]
    search_fields = [
        "description",
        "user__email",
        "project__name",
        "content_type",
    ]
    readonly_fields = [
        "id",
        "created_at",
        "user",
        "project",
        "action",
        "content_type",
        "object_id",
        "description",
        "changes",
        "metadata",
        "ip_address",
        "user_agent",
    ]
    fieldsets = (
        (
            "Activity Information",
            {
                "fields": (
                    "id",
                    "action",
                    "content_type",
                    "object_id",
                    "description",
                )
            },
        ),
        (
            "Context",
            {
                "fields": (
                    "user",
                    "project",
                )
            },
        ),
        (
            "Changes & Metadata",
            {
                "fields": (
                    "changes",
                    "metadata",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Request Information",
            {
                "fields": (
                    "ip_address",
                    "user_agent",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamp",
            {
                "fields": ("created_at",)
            },
        ),
    )

    def has_add_permission(self, request):
        """Prevent manual creation of activity logs."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of activity logs."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent modification of activity logs."""
        return False
