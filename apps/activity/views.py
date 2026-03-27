from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound, PermissionDenied

from apps.projects.permissions import get_project_and_membership
from .models import ActivityLog
from .serializers import ActivityLogSerializer


class ProjectActivityLogView(generics.ListAPIView):
    """
    List all activity logs for a project.

    Only project members can view activity logs.
    """

    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ["created_at", "action", "content_type"]
    filterset_fields = ["action", "content_type", "user"]
    search_fields = ["description", "user__email", "user__first_name", "user__last_name"]

    def get_queryset(self):
        project_id = self.kwargs.get("project_id")
        if not project_id:
            return ActivityLog.objects.none()

        # Verify user is member of project
        try:
            project, membership = get_project_and_membership(project_id, self.request.user)
        except (NotFound, PermissionDenied):
            return ActivityLog.objects.none()

        return ActivityLog.objects.filter(project=project).select_related("user").order_by("-created_at")


class UserActivityLogView(generics.ListAPIView):
    """
    List all activity logs for the current user across all projects.
    """

    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ["created_at", "action", "content_type"]
    filterset_fields = ["action", "content_type", "project"]
    search_fields = ["description", "project__name"]

    def get_queryset(self):
        """Get activities by the current user."""
        return ActivityLog.objects.filter(user=self.request.user).select_related(
            "user", "project"
        ).order_by("-created_at")


class ObjectActivityLogView(generics.ListAPIView):
    """
    List activity log for a specific object (e.g., a transaction, budget, etc).
    """

    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get activities for a specific object."""
        project_id = self.kwargs.get("project_id")
        object_id = self.kwargs.get("object_id")
        content_type = self.kwargs.get("content_type", "")

        if not all([project_id, object_id]):
            return ActivityLog.objects.none()

        # Verify user is member of project
        try:
            project, membership = get_project_and_membership(project_id, self.request.user)
        except (NotFound, PermissionDenied):
            return ActivityLog.objects.none()

        return ActivityLog.objects.filter(
            project=project,
            object_id=object_id,
            content_type=content_type,
        ).select_related("user").order_by("-created_at")
