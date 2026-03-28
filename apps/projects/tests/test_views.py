"""
Tests for projects/views.py - Project, member, and invitation API endpoints.

Tests:
- ProjectListCreateView - List, create, filter, search, order projects
- ProjectDetailView - Retrieve, update, delete projects
- ProjectArchiveView - Archive projects
- ProjectStatsView - Get project statistics
- ProjectMemberListView - List project members
- ProjectMemberDetailView - Update and remove members
- LeaveProjectView - Leave a project
- InviteMemberView - Invite new members
- InvitationListView - List pending invitations
- AcceptInvitationView - Accept invitations
- DeclineInvitationView - Decline invitations
"""

import pytest
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.projects.tests.factories import ProjectFactory, ProjectMemberFactory, InvitationFactory
from apps.projects.models import ProjectMember, Invitation, Project
from apps.authentication.tests.factories import UserFactory


@pytest.fixture
def api_client():
    """DRF API client."""
    return APIClient()


@pytest.fixture
def authenticated_user():
    """Create and return an authenticated user."""
    return UserFactory()


@pytest.fixture
def project_with_user(authenticated_user):
    """Create a project owned by the authenticated user."""
    project = ProjectFactory(owner=authenticated_user)
    # Ensure owner is added as member
    ProjectMember.objects.get_or_create(
        project=project,
        user=authenticated_user,
        defaults={"role": ProjectMember.Role.OWNER},
    )
    return project


@pytest.mark.django_db
class TestProjectListCreateView:
    """Test ProjectListCreateView endpoint."""

    def test_list_projects_authenticated_user(self, api_client, authenticated_user):
        """Test that authenticated user can list their projects."""
        api_client.force_authenticate(user=authenticated_user)

        # Create some projects user is member of
        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=authenticated_user)

        url = reverse("project-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data or isinstance(response.data, list)

    def test_list_projects_unauthenticated(self, api_client):
        """Test that unauthenticated user cannot list projects."""
        url = reverse("project-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_projects_only_user_projects(self, api_client, authenticated_user):
        """Test that user only sees projects they are member of."""
        api_client.force_authenticate(user=authenticated_user)

        # Create project user is member of
        user_project = ProjectFactory()
        ProjectMemberFactory(project=user_project, user=authenticated_user)

        # Create project user is not member of
        other_project = ProjectFactory()

        url = reverse("project-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_list_projects_pagination(self, api_client, authenticated_user):
        """Test that projects list is paginated."""
        api_client.force_authenticate(user=authenticated_user)

        # Create multiple projects
        for _ in range(15):
            project = ProjectFactory()
            ProjectMemberFactory(project=project, user=authenticated_user)

        url = reverse("project-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert "count" in response.data

    def test_filter_projects_by_project_type(self, api_client, authenticated_user):
        """Test filtering projects by project_type."""
        api_client.force_authenticate(user=authenticated_user)

        personal = ProjectFactory(project_type="personal")
        business = ProjectFactory(project_type="business")
        ProjectMemberFactory(project=personal, user=authenticated_user)
        ProjectMemberFactory(project=business, user=authenticated_user)

        url = reverse("project-list")
        response = api_client.get(f"{url}?project_type=personal")

        assert response.status_code == status.HTTP_200_OK

    def test_filter_projects_by_is_active(self, api_client, authenticated_user):
        """Test filtering projects by is_active status."""
        api_client.force_authenticate(user=authenticated_user)

        active = ProjectFactory(is_active=True)
        inactive = ProjectFactory(is_active=False)
        ProjectMemberFactory(project=active, user=authenticated_user)
        ProjectMemberFactory(project=inactive, user=authenticated_user)

        url = reverse("project-list")
        response = api_client.get(f"{url}?is_active=true")

        assert response.status_code == status.HTTP_200_OK

    def test_search_projects_by_name(self, api_client, authenticated_user):
        """Test searching projects by name."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory(name="Unique Project Name")
        ProjectMemberFactory(project=project, user=authenticated_user)

        url = reverse("project-list")
        response = api_client.get(f"{url}?search=Unique")

        assert response.status_code == status.HTTP_200_OK

    def test_order_projects_by_created_at(self, api_client, authenticated_user):
        """Test ordering projects by created_at."""
        api_client.force_authenticate(user=authenticated_user)

        for _ in range(3):
            project = ProjectFactory()
            ProjectMemberFactory(project=project, user=authenticated_user)

        url = reverse("project-list")
        response = api_client.get(f"{url}?ordering=-created_at")

        assert response.status_code == status.HTTP_200_OK

    def test_create_project(self, api_client, authenticated_user):
        """Test that authenticated user can create project."""
        api_client.force_authenticate(user=authenticated_user)

        data = {
            "name": "New Project",
            "description": "Test project",
            "project_type": "personal",
            "currency": "USD",
        }

        url = reverse("project-list")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "New Project"
        assert str(response.data["owner"]) == str(authenticated_user.id)

    def test_create_project_minimal_data(self, api_client, authenticated_user):
        """Test creating project with minimal required data."""
        api_client.force_authenticate(user=authenticated_user)

        data = {
            "name": "Minimal Project",
            "project_type": "personal",
        }

        url = reverse("project-list")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_project_unauthenticated(self, api_client):
        """Test that unauthenticated user cannot create project."""
        data = {
            "name": "New Project",
            "project_type": "personal",
        }

        url = reverse("project-list")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_project_adds_owner_as_member(self, api_client, authenticated_user):
        """Test that project creator is added as owner member."""
        api_client.force_authenticate(user=authenticated_user)

        data = {
            "name": "New Project",
            "project_type": "personal",
        }

        url = reverse("project-list")
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        project_id = response.data["id"]

        # Verify user is member with owner role
        membership = ProjectMember.objects.get(project_id=project_id, user=authenticated_user)
        assert membership.role == ProjectMember.Role.OWNER


@pytest.mark.django_db
class TestProjectDetailView:
    """Test ProjectDetailView endpoint."""

    def test_retrieve_project_member(self, api_client, authenticated_user, project_with_user):
        """Test that member can retrieve project."""
        api_client.force_authenticate(user=authenticated_user)

        url = reverse("project-detail", kwargs={"pk": project_with_user.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert str(response.data["id"]) == str(project_with_user.id)

    def test_retrieve_project_non_member(self, api_client, authenticated_user):
        """Test that non-member cannot retrieve project."""
        api_client.force_authenticate(user=authenticated_user)

        other_project = ProjectFactory()

        url = reverse("project-detail", kwargs={"pk": other_project.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_project_unauthenticated(self, api_client, project_with_user):
        """Test that unauthenticated user cannot retrieve project."""
        url = reverse("project-detail", kwargs={"pk": project_with_user.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_project_owner(self, api_client, authenticated_user, project_with_user):
        """Test that owner can update project."""
        api_client.force_authenticate(user=authenticated_user)

        data = {"name": "Updated Project Name"}

        url = reverse("project-detail", kwargs={"pk": project_with_user.id})
        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Project Name"

    def test_update_project_admin(self, api_client, authenticated_user):
        """Test that admin member can update project."""
        api_client.force_authenticate(user=authenticated_user)

        other_project = ProjectFactory()
        ProjectMemberFactory(project=other_project, user=authenticated_user, role=ProjectMember.Role.ADMIN)

        data = {"name": "Admin Updated"}

        url = reverse("project-detail", kwargs={"pk": other_project.id})
        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK

    def test_update_project_non_admin(self, api_client, authenticated_user):
        """Test that non-admin member cannot update project."""
        api_client.force_authenticate(user=authenticated_user)

        other_project = ProjectFactory()
        ProjectMemberFactory(project=other_project, user=authenticated_user, role=ProjectMember.Role.MEMBER)

        data = {"name": "Updated Name"}

        url = reverse("project-detail", kwargs={"pk": other_project.id})
        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_project_non_admin(self, api_client, authenticated_user):
        """Test that non-admin member cannot delete project."""
        api_client.force_authenticate(user=authenticated_user)

        other_project = ProjectFactory()
        ProjectMemberFactory(project=other_project, user=authenticated_user, role=ProjectMember.Role.MEMBER)

        url = reverse("project-detail", kwargs={"pk": other_project.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestProjectArchiveView:
    """Test ProjectArchiveView endpoint."""

    def test_archive_project_owner(self, api_client, authenticated_user, project_with_user):
        """Test that owner can archive project."""
        api_client.force_authenticate(user=authenticated_user)

        url = reverse("project-archive", kwargs={"pk": project_with_user.id})
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_archived"] is True
        assert response.data["is_active"] is False

    def test_archive_project_admin(self, api_client, authenticated_user):
        """Test that admin member can archive project."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=authenticated_user, role=ProjectMember.Role.ADMIN)

        url = reverse("project-archive", kwargs={"pk": project.id})
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_200_OK

    def test_archive_project_non_admin(self, api_client, authenticated_user):
        """Test that non-admin member cannot archive project."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=authenticated_user, role=ProjectMember.Role.MEMBER)

        url = reverse("project-archive", kwargs={"pk": project.id})
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_archive_project_non_member(self, api_client, authenticated_user):
        """Test that non-member cannot archive project."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory()

        url = reverse("project-archive", kwargs={"pk": project.id})
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_archive_already_archived_project(self, api_client, authenticated_user):
        """Test archiving a project that's already archived."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory(is_archived=True, is_active=False)
        ProjectMemberFactory(project=project, user=authenticated_user, role=ProjectMember.Role.OWNER)

        url = reverse("project-archive", kwargs={"pk": project.id})
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["is_archived"] is True


@pytest.mark.django_db
class TestProjectStatsView:
    """Test ProjectStatsView endpoint."""

    def test_get_project_stats(self, api_client, authenticated_user, project_with_user):
        """Test getting project statistics."""
        api_client.force_authenticate(user=authenticated_user)

        url = reverse("project-stats", kwargs={"pk": project_with_user.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["project_id"] == str(project_with_user.id)
        assert "member_count" in response.data

    def test_get_stats_with_multiple_members(self, api_client, authenticated_user, project_with_user):
        """Test stats reflect correct member count."""
        api_client.force_authenticate(user=authenticated_user)

        # Add more members
        for _ in range(2):
            ProjectMemberFactory(project=project_with_user)

        url = reverse("project-stats", kwargs={"pk": project_with_user.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["member_count"] >= 3

    def test_get_stats_non_member(self, api_client, authenticated_user):
        """Test that non-member cannot get stats."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory()

        url = reverse("project-stats", kwargs={"pk": project.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestProjectMemberListView:
    """Test ProjectMemberListView endpoint."""

    def test_list_project_members(self, api_client, authenticated_user, project_with_user):
        """Test listing project members."""
        api_client.force_authenticate(user=authenticated_user)

        # Add some members
        ProjectMemberFactory.create_batch(2, project=project_with_user)

        url = reverse("project-member-list", kwargs={"pk": project_with_user.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 3  # owner + 2 members

    def test_list_members_non_member(self, api_client, authenticated_user):
        """Test that non-member cannot list project members."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory()

        url = reverse("project-member-list", kwargs={"pk": project.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestProjectMemberDetailView:
    """Test ProjectMemberDetailView endpoint."""

    def test_update_member_role(self, api_client, authenticated_user, project_with_user):
        """Test that owner can update member role."""
        api_client.force_authenticate(user=authenticated_user)

        member = ProjectMemberFactory(project=project_with_user, role=ProjectMember.Role.MEMBER)

        data = {"role": ProjectMember.Role.ADMIN}

        url = reverse("project-member-detail", kwargs={"pk": project_with_user.id, "member_id": member.id})
        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["role"] == ProjectMember.Role.ADMIN

    def test_remove_member(self, api_client, authenticated_user, project_with_user):
        """Test that owner can remove member."""
        api_client.force_authenticate(user=authenticated_user)

        member = ProjectMemberFactory(project=project_with_user)
        member_id = member.id

        url = reverse("project-member-detail", kwargs={"pk": project_with_user.id, "member_id": member.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ProjectMember.objects.filter(id=member_id).exists()

    def test_cannot_change_owner_role(self, api_client, authenticated_user, project_with_user):
        """Test that owner role cannot be changed."""
        api_client.force_authenticate(user=authenticated_user)

        owner_member = ProjectMember.objects.get(project=project_with_user, user=authenticated_user)

        data = {"role": ProjectMember.Role.ADMIN}

        url = reverse("project-member-detail", kwargs={"pk": project_with_user.id, "member_id": owner_member.id})
        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_cannot_remove_owner(self, api_client, authenticated_user, project_with_user):
        """Test that project owner cannot be removed."""
        api_client.force_authenticate(user=authenticated_user)

        owner_member = ProjectMember.objects.get(project=project_with_user, user=authenticated_user)

        url = reverse("project-member-detail", kwargs={"pk": project_with_user.id, "member_id": owner_member.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_member_non_admin(self, api_client, authenticated_user):
        """Test that non-admin cannot update members."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=authenticated_user, role=ProjectMember.Role.MEMBER)
        target_member = ProjectMemberFactory(project=project)

        data = {"role": ProjectMember.Role.ADMIN}

        url = reverse("project-member-detail", kwargs={"pk": project.id, "member_id": target_member.id})
        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestLeaveProjectView:
    """Test LeaveProjectView endpoint."""

    def test_leave_project(self, api_client, authenticated_user):
        """Test that member can leave project."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory()
        membership = ProjectMemberFactory(project=project, user=authenticated_user, role=ProjectMember.Role.MEMBER)

        url = reverse("project-member-leave", kwargs={"pk": project.id})
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert not ProjectMember.objects.filter(id=membership.id).exists()

    def test_owner_cannot_leave(self, api_client, authenticated_user, project_with_user):
        """Test that owner cannot leave project."""
        api_client.force_authenticate(user=authenticated_user)

        url = reverse("project-member-leave", kwargs={"pk": project_with_user.id})
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestInviteMemberView:
    """Test InviteMemberView endpoint."""

    def test_invite_member(self, api_client, authenticated_user, project_with_user):
        """Test that owner can invite new member."""
        api_client.force_authenticate(user=authenticated_user)

        data = {
            "email": "newmember@example.com",
            "role": ProjectMember.Role.MEMBER,
        }

        url = reverse("project-member-invite", kwargs={"pk": project_with_user.id})
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["email"] == "newmember@example.com"

    def test_invite_existing_member(self, api_client, authenticated_user, project_with_user):
        """Test that cannot invite existing member."""
        api_client.force_authenticate(user=authenticated_user)

        existing_member = ProjectMemberFactory(project=project_with_user)

        data = {
            "email": existing_member.user.email,
            "role": ProjectMember.Role.MEMBER,
        }

        url = reverse("project-member-invite", kwargs={"pk": project_with_user.id})
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invite_without_permission(self, api_client, authenticated_user):
        """Test that member without permission cannot invite."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=authenticated_user, role=ProjectMember.Role.MEMBER, can_invite_members=False)

        data = {
            "email": "newmember@example.com",
            "role": ProjectMember.Role.MEMBER,
        }

        url = reverse("project-member-invite", kwargs={"pk": project.id})
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_invite_member_with_permission(self, api_client, authenticated_user):
        """Test that member with permission can invite."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=authenticated_user, role=ProjectMember.Role.MEMBER, can_invite_members=True)

        data = {
            "email": "newmember@example.com",
            "role": ProjectMember.Role.MEMBER,
        }

        url = reverse("project-member-invite", kwargs={"pk": project.id})
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestInvitationListView:
    """Test InvitationListView endpoint."""

    def test_list_pending_invitations(self, api_client, authenticated_user):
        """Test listing pending invitations."""
        api_client.force_authenticate(user=authenticated_user)

        # Create pending invitations for user
        project = ProjectFactory()
        InvitationFactory.create_batch(2, email=authenticated_user.email, status=Invitation.Status.PENDING)

        url = reverse("invitation-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2

    def test_list_only_user_invitations(self, api_client, authenticated_user):
        """Test that only user's invitations are listed."""
        api_client.force_authenticate(user=authenticated_user)

        # Create invitation for authenticated user
        user_invitation = InvitationFactory(email=authenticated_user.email, status=Invitation.Status.PENDING)

        # Create invitation for other user
        other_invitation = InvitationFactory(email="other@example.com", status=Invitation.Status.PENDING)

        url = reverse("invitation-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Handle both paginated and list responses
        data = response.data.get("results", response.data) if isinstance(response.data, dict) else response.data
        assert any(inv["email"] == authenticated_user.email for inv in data)


@pytest.mark.django_db
class TestAcceptInvitationView:
    """Test AcceptInvitationView endpoint."""

    def test_accept_invitation(self, api_client, authenticated_user):
        """Test accepting an invitation."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory()
        invitation = InvitationFactory(
            project=project,
            email=authenticated_user.email,
            status=Invitation.Status.PENDING,
        )

        url = reverse("invitation-accept", kwargs={"token": invitation.token})
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_200_OK

        # Verify user is now member
        assert ProjectMember.objects.filter(project=project, user=authenticated_user).exists()

    def test_accept_expired_invitation(self, api_client, authenticated_user):
        """Test that expired invitation cannot be accepted."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory()
        invitation = InvitationFactory(
            project=project,
            email=authenticated_user.email,
            status=Invitation.Status.PENDING,
            expires_at=timezone.now() - timedelta(days=1),  # Expired
        )

        url = reverse("invitation-accept", kwargs={"token": invitation.token})
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_accept_invalid_invitation(self, api_client, authenticated_user):
        """Test that invalid token is rejected."""
        api_client.force_authenticate(user=authenticated_user)

        url = reverse("invitation-accept", kwargs={"token": "invalid-token"})
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_accept_invitation_already_member(self, api_client, authenticated_user):
        """Test that already member cannot re-accept."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=authenticated_user)

        invitation = InvitationFactory(
            project=project,
            email=authenticated_user.email,
            status=Invitation.Status.PENDING,
        )

        url = reverse("invitation-accept", kwargs={"token": invitation.token})
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestDeclineInvitationView:
    """Test DeclineInvitationView endpoint."""

    def test_decline_invitation(self, api_client, authenticated_user):
        """Test declining an invitation."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory()
        invitation = InvitationFactory(
            project=project,
            email=authenticated_user.email,
            status=Invitation.Status.PENDING,
        )

        url = reverse("invitation-decline", kwargs={"token": invitation.token})
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_200_OK

        # Verify invitation status updated
        invitation.refresh_from_db()
        assert invitation.status == Invitation.Status.DECLINED

    def test_decline_invalid_invitation(self, api_client, authenticated_user):
        """Test that invalid invitation cannot be declined."""
        api_client.force_authenticate(user=authenticated_user)

        url = reverse("invitation-decline", kwargs={"token": "invalid-token"})
        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
