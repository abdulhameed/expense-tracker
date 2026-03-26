from datetime import timedelta
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.tests.factories import UserFactory, VerifiedUserFactory
from apps.projects.models import Invitation, Project, ProjectMember

from .factories import InvitationFactory, ProjectFactory, ProjectMemberFactory


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user():
    return VerifiedUserFactory()


@pytest.fixture
def auth_client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


# ---------------------------------------------------------------------------
# Projects CRUD
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestProjectListCreateView:
    url = reverse("project-list")

    def test_list_own_projects(self, auth_client, user):
        ProjectFactory(owner=user)
        ProjectFactory(owner=user)
        ProjectFactory()  # other user's project
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

    def test_list_projects_as_member(self, auth_client, user):
        other_project = ProjectFactory()
        ProjectMemberFactory(project=other_project, user=user)
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_create_project_success(self, auth_client, user):
        payload = {"name": "New Project", "project_type": "personal", "currency": "USD"}
        response = auth_client.post(self.url, payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "New Project"
        assert str(response.data["owner"]) == str(user.id)

    def test_create_project_auto_adds_owner_member(self, auth_client, user):
        auth_client.post(self.url, {"name": "P", "project_type": "personal"})
        project = Project.objects.get(owner=user)
        assert ProjectMember.objects.filter(
            project=project, user=user, role=ProjectMember.Role.OWNER
        ).exists()

    def test_create_project_unauthenticated(self, client):
        response = client.post(self.url, {"name": "P"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_project_negative_budget(self, auth_client):
        response = auth_client.post(self.url, {"name": "P", "project_type": "personal", "budget": "-100"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_project_end_date_before_start(self, auth_client):
        response = auth_client.post(self.url, {
            "name": "P", "project_type": "personal",
            "start_date": "2026-06-01", "end_date": "2026-01-01",
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_project_empty_name(self, auth_client):
        response = auth_client.post(self.url, {"name": "", "project_type": "personal"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_filter_by_project_type(self, auth_client, user):
        ProjectFactory(owner=user, project_type=Project.ProjectType.PERSONAL)
        ProjectFactory(owner=user, project_type=Project.ProjectType.BUSINESS)
        response = auth_client.get(self.url + "?project_type=personal")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_filter_by_is_active(self, auth_client, user):
        ProjectFactory(owner=user, is_active=True)
        ProjectFactory(owner=user, is_active=False, is_archived=True)
        response = auth_client.get(self.url + "?is_active=true")
        assert response.data["count"] == 1

    def test_list_unauthenticated(self, client):
        response = client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestProjectDetailView:
    def url(self, pk):
        return reverse("project-detail", kwargs={"pk": pk})

    def test_get_as_owner(self, auth_client, user):
        project = ProjectFactory(owner=user)
        response = auth_client.get(self.url(project.pk))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == project.name

    def test_get_as_member(self, auth_client, user):
        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=user)
        response = auth_client.get(self.url(project.pk))
        assert response.status_code == status.HTTP_200_OK

    def test_get_non_member_returns_403(self, auth_client):
        project = ProjectFactory()
        response = auth_client.get(self.url(project.pk))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_nonexistent_returns_404(self, auth_client):
        import uuid
        response = auth_client.get(self.url(uuid.uuid4()))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_patch_as_owner(self, auth_client, user):
        project = ProjectFactory(owner=user)
        response = auth_client.patch(self.url(project.pk), {"name": "Updated"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated"

    def test_patch_as_admin(self, auth_client, user):
        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=user, role=ProjectMember.Role.ADMIN)
        response = auth_client.patch(self.url(project.pk), {"name": "Admin Update"})
        assert response.status_code == status.HTTP_200_OK

    def test_patch_as_member_returns_403(self, auth_client, user):
        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=user, role=ProjectMember.Role.MEMBER)
        response = auth_client.patch(self.url(project.pk), {"name": "Hack"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_as_owner(self, auth_client, user):
        project = ProjectFactory(owner=user)
        response = auth_client.delete(self.url(project.pk))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Project.objects.filter(pk=project.pk).exists()

    def test_delete_as_member_returns_403(self, auth_client, user):
        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=user, role=ProjectMember.Role.MEMBER)
        response = auth_client.delete(self.url(project.pk))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_put_not_allowed(self, auth_client, user):
        project = ProjectFactory(owner=user)
        response = auth_client.put(self.url(project.pk), {"name": "x"})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
class TestProjectArchiveView:
    def url(self, pk):
        return reverse("project-archive", kwargs={"pk": pk})

    def test_archive_as_owner(self, auth_client, user):
        project = ProjectFactory(owner=user)
        response = auth_client.post(self.url(project.pk))
        assert response.status_code == status.HTTP_200_OK
        project.refresh_from_db()
        assert project.is_archived is True
        assert project.is_active is False

    def test_archive_as_member_returns_403(self, auth_client, user):
        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=user, role=ProjectMember.Role.MEMBER)
        response = auth_client.post(self.url(project.pk))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_archive_non_member_returns_403(self, auth_client):
        project = ProjectFactory()
        response = auth_client.post(self.url(project.pk))
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# Project Members
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestProjectMemberListView:
    def url(self, pk):
        return reverse("project-member-list", kwargs={"pk": pk})

    def test_list_members_as_member(self, auth_client, user):
        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=user)
        response = auth_client.get(self.url(project.pk))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_list_members_non_member_returns_403(self, auth_client):
        project = ProjectFactory()
        response = auth_client.get(self.url(project.pk))
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestProjectMemberDetailView:
    def url(self, pk, member_id):
        return reverse("project-member-detail", kwargs={"pk": pk, "member_id": member_id})

    def test_update_role_as_owner(self, auth_client, user):
        project = ProjectFactory(owner=user)
        target = ProjectMemberFactory(project=project, role=ProjectMember.Role.MEMBER)
        response = auth_client.patch(self.url(project.pk, target.pk), {"role": "admin"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["role"] == "admin"

    def test_cannot_change_owner_role(self, auth_client, user):
        project = ProjectFactory(owner=user)
        owner_member = ProjectMember.objects.get(project=project, user=user)
        response = auth_client.patch(self.url(project.pk, owner_member.pk), {"role": "member"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_member_cannot_update_roles(self, auth_client, user):
        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=user, role=ProjectMember.Role.MEMBER)
        target = ProjectMemberFactory(project=project)
        response = auth_client.patch(self.url(project.pk, target.pk), {"role": "admin"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_remove_member_as_owner(self, auth_client, user):
        project = ProjectFactory(owner=user)
        target = ProjectMemberFactory(project=project)
        response = auth_client.delete(self.url(project.pk, target.pk))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not ProjectMember.objects.filter(pk=target.pk).exists()

    def test_cannot_remove_owner(self, auth_client, user):
        project = ProjectFactory(owner=user)
        owner_member = ProjectMember.objects.get(project=project, user=user)
        response = auth_client.delete(self.url(project.pk, owner_member.pk))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_nonexistent_member_returns_404(self, auth_client, user):
        import uuid
        project = ProjectFactory(owner=user)
        response = auth_client.patch(self.url(project.pk, uuid.uuid4()), {"role": "admin"})
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestLeaveProjectView:
    def url(self, pk):
        return reverse("project-member-leave", kwargs={"pk": pk})

    def test_member_can_leave(self, auth_client, user):
        project = ProjectFactory()
        membership = ProjectMemberFactory(project=project, user=user)
        response = auth_client.post(self.url(project.pk))
        assert response.status_code == status.HTTP_200_OK
        assert not ProjectMember.objects.filter(pk=membership.pk).exists()

    def test_owner_cannot_leave(self, auth_client, user):
        project = ProjectFactory(owner=user)
        response = auth_client.post(self.url(project.pk))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_non_member_returns_403(self, auth_client):
        project = ProjectFactory()
        response = auth_client.post(self.url(project.pk))
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# Invitations
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestInviteMemberView:
    def url(self, pk):
        return reverse("project-member-invite", kwargs={"pk": pk})

    @patch("apps.projects.views.send_invitation_email.delay")
    def test_invite_success(self, mock_task, auth_client, user):
        project = ProjectFactory(owner=user)
        payload = {"email": "newuser@example.com", "role": "member"}
        response = auth_client.post(self.url(project.pk), payload)
        assert response.status_code == status.HTTP_201_CREATED
        mock_task.assert_called_once()

    @patch("apps.projects.views.send_invitation_email.delay")
    def test_invite_member_cannot_invite_by_default(self, mock_task, auth_client, user):
        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=user, role=ProjectMember.Role.MEMBER)
        response = auth_client.post(self.url(project.pk), {"email": "x@example.com"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("apps.projects.views.send_invitation_email.delay")
    def test_invite_existing_member_returns_400(self, mock_task, auth_client, user):
        project = ProjectFactory(owner=user)
        existing = UserFactory()
        ProjectMemberFactory(project=project, user=existing)
        response = auth_client.post(self.url(project.pk), {"email": existing.email})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("apps.projects.views.send_invitation_email.delay")
    def test_reinvite_expires_old_invitation(self, mock_task, auth_client, user):
        project = ProjectFactory(owner=user)
        old_inv = InvitationFactory(
            project=project,
            email="repeat@example.com",
            status=Invitation.Status.PENDING,
            invited_by=user,
        )
        auth_client.post(self.url(project.pk), {"email": "repeat@example.com"})
        old_inv.refresh_from_db()
        assert old_inv.status == Invitation.Status.EXPIRED

    def test_invite_non_member_returns_403(self, auth_client):
        project = ProjectFactory()
        response = auth_client.post(self.url(project.pk), {"email": "x@example.com"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @patch("apps.projects.views.send_invitation_email.delay")
    def test_invite_invalid_email(self, mock_task, auth_client, user):
        project = ProjectFactory(owner=user)
        response = auth_client.post(self.url(project.pk), {"email": "not-an-email"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestInvitationListView:
    url = reverse("invitation-list")

    def test_list_pending_invitations(self, auth_client, user):
        InvitationFactory(email=user.email, status=Invitation.Status.PENDING)
        InvitationFactory(email=user.email, status=Invitation.Status.ACCEPTED)
        InvitationFactory()  # different email
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_unauthenticated_returns_401(self, client):
        response = client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestAcceptInvitationView:
    def url(self, token):
        return reverse("invitation-accept", kwargs={"token": token})

    def test_accept_success(self, auth_client, user):
        inv = InvitationFactory(
            email=user.email,
            expires_at=timezone.now() + timedelta(days=1),
        )
        response = auth_client.post(self.url(inv.token))
        assert response.status_code == status.HTTP_200_OK
        assert ProjectMember.objects.filter(project=inv.project, user=user).exists()
        inv.refresh_from_db()
        assert inv.status == Invitation.Status.ACCEPTED

    def test_accept_expired_returns_400(self, auth_client, user):
        inv = InvitationFactory(
            email=user.email,
            expires_at=timezone.now() - timedelta(seconds=1),
        )
        response = auth_client.post(self.url(inv.token))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_accept_wrong_email_returns_400(self, auth_client, user):
        inv = InvitationFactory(email="other@example.com")
        response = auth_client.post(self.url(inv.token))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_accept_invalid_token_returns_400(self, auth_client):
        response = auth_client.post(self.url("bogustoken"))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_accept_already_member_returns_400(self, auth_client, user):
        inv = InvitationFactory(
            email=user.email,
            expires_at=timezone.now() + timedelta(days=1),
        )
        ProjectMemberFactory(project=inv.project, user=user)
        response = auth_client.post(self.url(inv.token))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_accept_unauthenticated_returns_401(self, client):
        inv = InvitationFactory()
        response = client.post(self.url(inv.token))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDeclineInvitationView:
    def url(self, token):
        return reverse("invitation-decline", kwargs={"token": token})

    def test_decline_success(self, auth_client, user):
        inv = InvitationFactory(email=user.email)
        response = auth_client.post(self.url(inv.token))
        assert response.status_code == status.HTTP_200_OK
        inv.refresh_from_db()
        assert inv.status == Invitation.Status.DECLINED

    def test_decline_wrong_email_returns_400(self, auth_client, user):
        inv = InvitationFactory(email="other@example.com")
        response = auth_client.post(self.url(inv.token))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_decline_invalid_token_returns_400(self, auth_client):
        response = auth_client.post(self.url("badtoken"))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
