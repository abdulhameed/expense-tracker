import logging
from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Invitation, Project, ProjectMember
from .permissions import get_project_and_membership, require_owner_or_admin
from .serializers import (
    InvitationSerializer,
    InviteMemberSerializer,
    ProjectMemberSerializer,
    ProjectSerializer,
)
from .tasks import send_invitation_email

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------


class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["project_type", "is_active", "is_archived"]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "name"]

    def get_queryset(self):
        return (
            Project.objects.filter(members__user=self.request.user)
            .prefetch_related("members")
            .distinct()
        )

    @transaction.atomic
    def perform_create(self, serializer):
        project = serializer.save(owner=self.request.user)
        ProjectMember.objects.create(
            project=project,
            user=self.request.user,
            role=ProjectMember.Role.OWNER,
        )


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Project.objects.all()
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_object(self):
        project = super().get_object()  # handles 404
        try:
            self._membership = ProjectMember.objects.get(project=project, user=self.request.user)
        except ProjectMember.DoesNotExist:
            raise PermissionDenied("You are not a member of this project.")

        if self.request.method in ("PATCH", "DELETE"):
            require_owner_or_admin(self._membership)

        return project


class ProjectArchiveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        project, membership = get_project_and_membership(pk, request.user)
        require_owner_or_admin(membership)

        project.is_archived = True
        project.is_active = False
        project.save(update_fields=["is_archived", "is_active", "updated_at"])
        return Response(ProjectSerializer(project).data)


class ProjectStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        project, _ = get_project_and_membership(pk, request.user)
        return Response(
            {
                "project_id": str(project.id),
                "member_count": project.members.count(),
                "is_archived": project.is_archived,
                "is_active": project.is_active,
            }
        )


# ---------------------------------------------------------------------------
# Project Members
# ---------------------------------------------------------------------------


class ProjectMemberListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        project, _ = get_project_and_membership(pk, request.user)
        members = project.members.select_related("user").all()
        return Response(ProjectMemberSerializer(members, many=True).data)


class ProjectMemberDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _get_objects(self, pk, member_id, user):
        project, requester = get_project_and_membership(pk, user)
        try:
            target = ProjectMember.objects.select_related("user").get(pk=member_id, project=project)
        except ProjectMember.DoesNotExist:
            raise NotFound("Member not found.")
        return project, requester, target

    def patch(self, request, pk, member_id):
        _, requester, target = self._get_objects(pk, member_id, request.user)
        require_owner_or_admin(requester)

        if target.role == ProjectMember.Role.OWNER:
            return Response(
                {"detail": "Cannot change the owner's role."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ProjectMemberSerializer(target, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk, member_id):
        _, requester, target = self._get_objects(pk, member_id, request.user)
        require_owner_or_admin(requester)

        if target.role == ProjectMember.Role.OWNER:
            return Response(
                {"detail": "Cannot remove the project owner."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        target.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LeaveProjectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        _, membership = get_project_and_membership(pk, request.user)

        if membership.role == ProjectMember.Role.OWNER:
            return Response(
                {"detail": "Project owner cannot leave. Transfer ownership first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        membership.delete()
        return Response({"detail": "Successfully left the project."})


# ---------------------------------------------------------------------------
# Invitations
# ---------------------------------------------------------------------------


class InviteMemberView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        project, membership = get_project_and_membership(pk, request.user)

        can_invite = (
            membership.role in [ProjectMember.Role.OWNER, ProjectMember.Role.ADMIN]
            or membership.can_invite_members
        )
        if not can_invite:
            raise PermissionDenied("You do not have permission to invite members.")

        serializer = InviteMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        role = serializer.validated_data["role"]

        # Block if already a member
        from apps.authentication.models import User

        try:
            invitee = User.objects.get(email=email)
            if ProjectMember.objects.filter(project=project, user=invitee).exists():
                return Response(
                    {"detail": "This user is already a member of the project."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except User.DoesNotExist:
            pass

        # Expire any existing pending invitation
        Invitation.objects.filter(
            project=project, email=email, status=Invitation.Status.PENDING
        ).update(status=Invitation.Status.EXPIRED)

        invitation = Invitation.objects.create(
            project=project,
            email=email,
            role=role,
            invited_by=request.user,
            expires_at=timezone.now() + timedelta(days=7),
        )

        send_invitation_email.delay(str(invitation.id))
        logger.info("Invitation sent to %s for project %s", email, project.name)

        return Response(InvitationSerializer(invitation).data, status=status.HTTP_201_CREATED)


class InvitationListView(generics.ListAPIView):
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Invitation.objects.filter(
            email=self.request.user.email,
            status=Invitation.Status.PENDING,
        ).select_related("project", "invited_by")


class AcceptInvitationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, token):
        try:
            invitation = Invitation.objects.select_related("project", "invited_by").get(
                token=token,
                email=request.user.email,
                status=Invitation.Status.PENDING,
            )
        except Invitation.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired invitation."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if invitation.is_expired:
            invitation.status = Invitation.Status.EXPIRED
            invitation.save(update_fields=["status"])
            return Response(
                {"detail": "This invitation has expired."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if ProjectMember.objects.filter(project=invitation.project, user=request.user).exists():
            invitation.status = Invitation.Status.ACCEPTED
            invitation.save(update_fields=["status"])
            return Response(
                {"detail": "You are already a member of this project."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            ProjectMember.objects.create(
                project=invitation.project,
                user=request.user,
                role=invitation.role,
                invited_by=invitation.invited_by,
            )
            invitation.status = Invitation.Status.ACCEPTED
            invitation.accepted_at = timezone.now()
            invitation.save(update_fields=["status", "accepted_at"])

        return Response({"detail": "Invitation accepted. You are now a project member."})


class DeclineInvitationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, token):
        try:
            invitation = Invitation.objects.get(
                token=token,
                email=request.user.email,
                status=Invitation.Status.PENDING,
            )
        except Invitation.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired invitation."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation.status = Invitation.Status.DECLINED
        invitation.save(update_fields=["status"])
        return Response({"detail": "Invitation declined."})
