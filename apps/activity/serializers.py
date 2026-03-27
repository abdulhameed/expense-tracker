from rest_framework import serializers

from .models import ActivityLog


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for ActivityLog model."""

    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_name = serializers.SerializerMethodField(read_only=True)
    action_display = serializers.CharField(source="get_action_display", read_only=True)

    class Meta:
        model = ActivityLog
        fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "project",
            "action",
            "action_display",
            "content_type",
            "object_id",
            "description",
            "changes",
            "metadata",
            "ip_address",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "user_email",
            "user_name",
            "project",
            "action",
            "content_type",
            "object_id",
            "description",
            "changes",
            "metadata",
            "ip_address",
            "created_at",
        ]

    def get_user_name(self, obj):
        """Get full name or email of user."""
        if obj.user:
            if obj.user.first_name and obj.user.last_name:
                return f"{obj.user.first_name} {obj.user.last_name}"
            return obj.user.email
        return None
