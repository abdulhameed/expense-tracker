"""
Activity Log models for tracking all changes and actions in the system.
"""
from uuid import uuid4

from django.conf import settings
from django.db import models


class ActivityLog(models.Model):
    """
    Log of all activities/changes in the system.
    Tracks who did what, when, to which model.
    """

    class ActionType(models.TextChoices):
        """Types of actions that can be logged."""

        CREATE = "create", "Created"
        UPDATE = "update", "Updated"
        DELETE = "delete", "Deleted"
        VIEW = "view", "Viewed"
        EXPORT = "export", "Exported"
        IMPORT = "import", "Imported"
        SHARE = "share", "Shared"
        INVITE = "invite", "Invited"
        ACCEPT = "accept", "Accepted"
        DECLINE = "decline", "Declined"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    # User who performed the action
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="activities",
    )

    # Project context (most activities are project-related)
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="activities",
        null=True,
        blank=True,
    )

    # Type of action
    action = models.CharField(max_length=20, choices=ActionType.choices)

    # What model was affected
    content_type = models.CharField(max_length=100)  # e.g., "transaction", "budget", "document"

    # ID of the affected object
    object_id = models.UUIDField()

    # Human-readable description
    description = models.TextField()

    # Changes made (for update operations)
    # Stored as JSON: {"field_name": {"old": value, "new": value}}
    changes = models.JSONField(default=dict, blank=True)

    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)

    # IP address of the request
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    # User agent
    user_agent = models.TextField(blank=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project", "created_at"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["action"]),
        ]

    def __str__(self):
        return f"{self.get_action_display()} {self.content_type} by {self.user}"
