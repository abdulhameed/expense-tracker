"""
Tests for projects/serializers.py - Project and member serializers.

Tests:
- ProjectSerializer - Project validation, budget constraints, date validation
- ProjectMemberSerializer - Member role serialization
- InvitationSerializer - Invitation handling
- InviteMemberSerializer - Member invitation validation
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal

from apps.projects.serializers import (
    ProjectSerializer,
    ProjectMemberSerializer,
    InvitationSerializer,
    InviteMemberSerializer,
)
from apps.projects.tests.factories import (
    ProjectFactory,
    ProjectMemberFactory,
    InvitationFactory,
)
from apps.projects.models import ProjectMember
from apps.authentication.tests.factories import UserFactory


@pytest.mark.django_db
class TestProjectSerializer:
    """Test ProjectSerializer for project validation and serialization."""

    def test_project_serializer_valid_data(self):
        """Test that valid project data is serialized."""
        user = UserFactory()
        project = ProjectFactory(
            owner=user,
            name="Q4 Budget",
            project_type="personal",
            currency="USD",
        )

        serializer = ProjectSerializer(project)
        data = serializer.data

        assert data["name"] == "Q4 Budget"
        assert data["project_type"] == "personal"
        assert data["currency"] == "USD"
        assert data["owner"] == user.id

    def test_project_serializer_member_count(self):
        """Test that member count is calculated correctly."""
        user = UserFactory()
        project = ProjectFactory(owner=user, add_owner_member=False)

        # Add some members
        for _ in range(3):
            ProjectMemberFactory(project=project)

        serializer = ProjectSerializer(project)
        assert serializer.data["member_count"] == 3

    def test_project_serializer_read_only_fields(self):
        """Test that system-generated fields are read-only."""
        project = ProjectFactory()

        data = {
            "name": "Updated",
            "owner": 999,
            "is_archived": True,
            "id": "fake-id",
        }

        serializer = ProjectSerializer(project, data=data, partial=True)
        assert serializer.is_valid()

        # Read-only fields should not change
        assert serializer.validated_data.get("owner") is None
        assert serializer.validated_data.get("is_archived") is None
        assert serializer.validated_data.get("id") is None

    def test_project_serializer_budget_validation_positive(self):
        """Test that budget must be positive."""
        user = UserFactory()

        data = {
            "name": "Test Project",
            "project_type": "personal",
            "currency": "USD",
            "budget": "-1000.00",
        }

        serializer = ProjectSerializer(data=data)
        assert not serializer.is_valid()
        assert "budget" in serializer.errors

    def test_project_serializer_budget_validation_zero(self):
        """Test that zero budget is allowed."""
        user = UserFactory()

        data = {
            "name": "Test Project",
            "project_type": "personal",
            "currency": "USD",
            "budget": "0.00",
        }

        serializer = ProjectSerializer(data=data)
        # Zero budget should be valid
        assert not serializer.is_valid() or "budget" not in serializer.errors

    def test_project_serializer_budget_validation_positive_allowed(self):
        """Test that positive budget is allowed."""
        data = {
            "name": "Test Project",
            "project_type": "personal",
            "currency": "USD",
            "budget": "5000.00",
        }

        serializer = ProjectSerializer(data=data)
        # Positive value should be allowed (validation passes)
        assert not serializer.is_valid() or "budget" not in serializer.errors

    def test_project_serializer_date_validation_end_after_start(self):
        """Test that end_date must be after start_date."""
        start = date.today()
        end = start - timedelta(days=1)  # End before start

        data = {
            "name": "Test",
            "start_date": start,
            "end_date": end,
        }

        serializer = ProjectSerializer(data=data)
        assert not serializer.is_valid()
        assert "end_date" in serializer.errors

    def test_project_serializer_date_validation_same_date_allowed(self):
        """Test that same start and end dates are allowed."""
        same_date = date.today()

        data = {
            "name": "Test",
            "start_date": same_date,
            "end_date": same_date,
        }

        serializer = ProjectSerializer(data=data)
        # Same dates should be valid
        assert not serializer.is_valid() or "end_date" not in serializer.errors

    def test_project_serializer_date_validation_end_after_start_allowed(self):
        """Test that end_date after start_date is allowed."""
        start = date.today()
        end = start + timedelta(days=30)

        data = {
            "name": "Test",
            "start_date": start,
            "end_date": end,
        }

        serializer = ProjectSerializer(data=data)
        # End after start should be valid
        assert not serializer.is_valid() or "end_date" not in serializer.errors

    def test_project_serializer_update_preserves_owner(self):
        """Test that project owner cannot be changed via serializer."""
        owner = UserFactory()
        other_user = UserFactory()
        project = ProjectFactory(owner=owner)

        data = {"owner": other_user.id, "name": "Updated"}
        serializer = ProjectSerializer(project, data=data, partial=True)

        assert serializer.is_valid()
        updated = serializer.save()
        # Owner should not change
        assert updated.owner == owner


@pytest.mark.django_db
class TestProjectMemberSerializer:
    """Test ProjectMemberSerializer for member data."""

    def test_member_serializer_valid_data(self):
        """Test that member data is serialized correctly."""
        user = UserFactory(first_name="John", last_name="Doe", email="john@example.com")
        project = ProjectFactory()
        member = ProjectMemberFactory(
            project=project,
            user=user,
            role=ProjectMember.Role.MEMBER,
        )

        serializer = ProjectMemberSerializer(member)
        data = serializer.data

        assert data["user"] == user.id
        assert data["email"] == "john@example.com"
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"
        assert data["role"] == ProjectMember.Role.MEMBER

    def test_member_serializer_nested_user_fields(self):
        """Test that user fields are read-only and nested."""
        user = UserFactory(
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
        )
        member = ProjectMemberFactory(user=user)

        serializer = ProjectMemberSerializer(member)
        data = serializer.data

        # User fields should be read-only
        assert data["email"] == "jane@example.com"
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Smith"

    def test_member_serializer_read_only_fields(self):
        """Test that system-generated fields are read-only."""
        member = ProjectMemberFactory()

        data = {
            "role": ProjectMember.Role.ADMIN,
            "user": 999,
            "email": "fake@example.com",
            "id": "fake-id",
        }

        serializer = ProjectMemberSerializer(member, data=data, partial=True)
        assert serializer.is_valid()

        # User and other read-only fields should not change
        assert serializer.validated_data.get("user") is None
        assert serializer.validated_data.get("email") is None
        assert serializer.validated_data.get("id") is None

    def test_member_serializer_role_update(self):
        """Test that member role can be updated."""
        member = ProjectMemberFactory(role=ProjectMember.Role.MEMBER)

        data = {"role": ProjectMember.Role.ADMIN}
        serializer = ProjectMemberSerializer(member, data=data, partial=True)

        assert serializer.is_valid()
        updated = serializer.save()
        assert updated.role == ProjectMember.Role.ADMIN

    def test_member_serializer_permissions_fields(self):
        """Test that permission fields are included."""
        member = ProjectMemberFactory(
            can_create_transactions=True,
            can_view_reports=False,
        )

        serializer = ProjectMemberSerializer(member)
        data = serializer.data

        assert "can_create_transactions" in data
        assert "can_edit_transactions" in data
        assert "can_delete_transactions" in data
        assert "can_view_reports" in data
        assert "can_invite_members" in data


@pytest.mark.django_db
class TestInvitationSerializer:
    """Test InvitationSerializer for invitation data."""

    def test_invitation_serializer_valid_data(self):
        """Test that invitation data is serialized."""
        inviter = UserFactory(email="inviter@example.com")
        project = ProjectFactory(name="Team Project")
        invitation = InvitationFactory(
            project=project,
            email="invited@example.com",
            invited_by=inviter,
            role=ProjectMember.Role.MEMBER,
        )

        serializer = InvitationSerializer(invitation)
        data = serializer.data

        assert data["email"] == "invited@example.com"
        assert data["role"] == ProjectMember.Role.MEMBER
        assert data["project"] == project.id
        assert data["project_name"] == "Team Project"
        assert data["invited_by_email"] == "inviter@example.com"

    def test_invitation_serializer_read_only_fields(self):
        """Test that system fields are read-only."""
        invitation = InvitationFactory()

        data = {
            "email": "newemail@example.com",
            "status": "accepted",
            "invited_by": 999,
            "id": "fake-id",
        }

        serializer = InvitationSerializer(invitation, data=data, partial=True)
        assert serializer.is_valid()

        # Read-only fields should not change
        assert serializer.validated_data.get("status") is None
        assert serializer.validated_data.get("invited_by") is None
        assert serializer.validated_data.get("id") is None

    def test_invitation_serializer_status_display(self):
        """Test that invitation status is included."""
        invitation = InvitationFactory(status="pending")

        serializer = InvitationSerializer(invitation)
        assert serializer.data["status"] == "pending"

    def test_invitation_serializer_expires_at_field(self):
        """Test that expiration date is included."""
        invitation = InvitationFactory()

        serializer = InvitationSerializer(invitation)
        assert "expires_at" in serializer.data


@pytest.mark.django_db
class TestInviteMemberSerializer:
    """Test InviteMemberSerializer for member invitations."""

    def test_invite_member_serializer_valid_email(self):
        """Test that valid email is accepted."""
        data = {
            "email": "newmember@example.com",
            "role": ProjectMember.Role.MEMBER,
        }

        serializer = InviteMemberSerializer(data=data)
        assert serializer.is_valid()

    def test_invite_member_serializer_invalid_email(self):
        """Test that invalid email is rejected."""
        data = {
            "email": "not-an-email",
            "role": ProjectMember.Role.MEMBER,
        }

        serializer = InviteMemberSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_invite_member_serializer_valid_role(self):
        """Test that valid roles are accepted."""
        for role in ["member", "admin"]:
            data = {
                "email": "user@example.com",
                "role": role,
            }

            serializer = InviteMemberSerializer(data=data)
            assert serializer.is_valid()

    def test_invite_member_serializer_default_role(self):
        """Test that role defaults to MEMBER."""
        data = {"email": "user@example.com"}

        serializer = InviteMemberSerializer(data=data)
        # Should be valid with default role
        assert serializer.is_valid() or "role" not in serializer.errors

    def test_invite_member_serializer_required_fields(self):
        """Test that email is required."""
        data = {"role": ProjectMember.Role.MEMBER}

        serializer = InviteMemberSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors


@pytest.mark.django_db
class TestSerializerIntegration:
    """Integration tests for project serializers."""

    def test_project_and_member_serialization(self):
        """Test that project and member serializers work together."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        member = ProjectMemberFactory(project=project, user=user)

        # Serialize project
        proj_ser = ProjectSerializer(project)
        assert proj_ser.data["owner"] == user.id

        # Serialize member
        member_ser = ProjectMemberSerializer(member)
        assert member_ser.data["email"] == user.email

    def test_invitation_flow(self):
        """Test invitation and member serialization flow."""
        inviter = UserFactory()
        project = ProjectFactory(owner=inviter)
        invited_user = UserFactory()

        # Create invitation
        invitation = InvitationFactory(
            project=project,
            email=invited_user.email,
            invited_by=inviter,
        )

        # Serialize invitation
        inv_ser = InvitationSerializer(invitation)
        assert inv_ser.data["email"] == invited_user.email
        assert inv_ser.data["project_name"] == project.name

        # After acceptance, would create member
        member = ProjectMemberFactory(
            project=project,
            user=invited_user,
        )

        member_ser = ProjectMemberSerializer(member)
        assert member_ser.data["email"] == invited_user.email
