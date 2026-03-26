import uuid
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.projects.models import Invitation, Project, ProjectMember

from .factories import InvitationFactory, ProjectFactory, ProjectMemberFactory


@pytest.mark.django_db
class TestProjectModel:
    def test_create_project(self):
        project = ProjectFactory()
        assert project.pk is not None
        assert project.name

    def test_uuid_primary_key(self):
        project = ProjectFactory()
        assert isinstance(project.pk, uuid.UUID)

    def test_str_representation(self):
        project = ProjectFactory(name="My Budget")
        assert str(project) == "My Budget"

    def test_default_values(self):
        project = ProjectFactory()
        assert project.currency == "USD"
        assert project.is_active is True
        assert project.is_archived is False
        assert project.project_type == Project.ProjectType.PERSONAL
        assert project.budget is None

    def test_owner_relationship(self):
        from apps.authentication.tests.factories import UserFactory
        user = UserFactory()
        project = ProjectFactory(owner=user, add_owner_member=False)
        assert project.owner == user

    def test_timestamps(self):
        project = ProjectFactory()
        assert project.created_at is not None
        assert project.updated_at is not None

    def test_owner_member_auto_created(self):
        project = ProjectFactory()
        assert ProjectMember.objects.filter(
            project=project, user=project.owner, role=ProjectMember.Role.OWNER
        ).exists()

    def test_project_types(self):
        for ptype in Project.ProjectType:
            p = ProjectFactory(project_type=ptype, add_owner_member=False)
            assert p.project_type == ptype.value


@pytest.mark.django_db
class TestProjectMemberModel:
    def test_create_member(self):
        member = ProjectMemberFactory()
        assert member.pk is not None

    def test_unique_constraint(self):
        from django.db import IntegrityError
        member = ProjectMemberFactory()
        with pytest.raises(IntegrityError):
            ProjectMemberFactory(project=member.project, user=member.user)

    def test_default_role(self):
        member = ProjectMemberFactory()
        assert member.role == ProjectMember.Role.MEMBER

    def test_default_permissions(self):
        member = ProjectMemberFactory()
        assert member.can_create_transactions is True
        assert member.can_edit_transactions is True
        assert member.can_delete_transactions is False
        assert member.can_view_reports is True
        assert member.can_invite_members is False

    def test_str_representation(self):
        member = ProjectMemberFactory()
        assert member.project.name in str(member)
        assert member.user.email in str(member)

    def test_all_roles_valid(self):
        for role in ProjectMember.Role:
            m = ProjectMemberFactory(role=role)
            assert m.role == role.value

    def test_cascade_delete_with_project(self):
        member = ProjectMemberFactory()
        project_id = member.project_id
        member.project.delete()
        assert not ProjectMember.objects.filter(project_id=project_id).exists()

    def test_cascade_delete_with_user(self):
        member = ProjectMemberFactory()
        user_id = member.user_id
        member.user.delete()
        assert not ProjectMember.objects.filter(user_id=user_id).exists()


@pytest.mark.django_db
class TestInvitationModel:
    def test_token_auto_generated(self):
        inv = InvitationFactory()
        assert inv.token
        assert len(inv.token) > 0

    def test_tokens_are_unique(self):
        i1 = InvitationFactory()
        i2 = InvitationFactory()
        assert i1.token != i2.token

    def test_not_expired(self):
        inv = InvitationFactory(expires_at=timezone.now() + timedelta(hours=1))
        assert not inv.is_expired

    def test_is_expired(self):
        inv = InvitationFactory(expires_at=timezone.now() - timedelta(seconds=1))
        assert inv.is_expired

    def test_default_status_pending(self):
        inv = InvitationFactory()
        assert inv.status == Invitation.Status.PENDING

    def test_str_representation(self):
        inv = InvitationFactory()
        assert inv.email in str(inv)
        assert inv.project.name in str(inv)

    def test_unique_together_pending(self):
        from django.db import IntegrityError
        inv = InvitationFactory()
        with pytest.raises(IntegrityError):
            InvitationFactory(
                project=inv.project,
                email=inv.email,
                status=Invitation.Status.PENDING,
            )

    def test_cascade_delete_with_project(self):
        inv = InvitationFactory()
        project_id = inv.project_id
        inv.project.delete()
        assert not Invitation.objects.filter(project_id=project_id).exists()
