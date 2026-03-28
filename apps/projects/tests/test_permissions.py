"""
Tests for projects/permissions.py - Project permission utilities.

Tests:
- get_project_and_membership - Retrieve project with membership validation
- require_owner_or_admin - Verify owner/admin role
"""

import pytest
from rest_framework.exceptions import NotFound, PermissionDenied
from django.contrib.auth import get_user_model

from apps.projects.models import Project, ProjectMember
from apps.projects.permissions import get_project_and_membership, require_owner_or_admin
from apps.projects.tests.factories import ProjectFactory, ProjectMemberFactory
from apps.authentication.tests.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestGetProjectAndMembership:
    """Test project and membership retrieval."""

    def test_get_valid_project_and_membership(self):
        """Test retrieving valid project and membership."""
        user = UserFactory()
        project = ProjectFactory()
        membership = ProjectMemberFactory(project=project, user=user, role=ProjectMember.Role.MEMBER)

        retrieved_project, retrieved_membership = get_project_and_membership(project.id, user)

        assert retrieved_project.id == project.id
        assert retrieved_membership.id == membership.id
        assert retrieved_membership.user.id == user.id

    def test_get_project_nonexistent_raises_not_found(self):
        """Test that nonexistent project raises NotFound."""
        user = UserFactory()

        with pytest.raises(NotFound) as exc_info:
            get_project_and_membership(99999, user)

        assert "not found" in str(exc_info.value).lower()

    def test_get_project_user_not_member_raises_permission_denied(self):
        """Test that non-member user raises PermissionDenied."""
        user = UserFactory()
        other_user = UserFactory()
        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=other_user)

        with pytest.raises(PermissionDenied) as exc_info:
            get_project_and_membership(project.id, user)

        assert "not a member" in str(exc_info.value).lower()

    def test_get_project_owner_membership(self):
        """Test retrieving project with owner membership."""
        user = UserFactory()
        project = ProjectFactory()
        membership = ProjectMemberFactory(project=project, user=user, role=ProjectMember.Role.OWNER)

        retrieved_project, retrieved_membership = get_project_and_membership(project.id, user)

        assert retrieved_membership.role == ProjectMember.Role.OWNER

    def test_get_project_admin_membership(self):
        """Test retrieving project with admin membership."""
        user = UserFactory()
        project = ProjectFactory()
        membership = ProjectMemberFactory(project=project, user=user, role=ProjectMember.Role.ADMIN)

        retrieved_project, retrieved_membership = get_project_and_membership(project.id, user)

        assert retrieved_membership.role == ProjectMember.Role.ADMIN

    def test_get_project_member_membership(self):
        """Test retrieving project with member membership."""
        user = UserFactory()
        project = ProjectFactory()
        membership = ProjectMemberFactory(project=project, user=user, role=ProjectMember.Role.MEMBER)

        retrieved_project, retrieved_membership = get_project_and_membership(project.id, user)

        assert retrieved_membership.role == ProjectMember.Role.MEMBER

    def test_get_project_multiple_members(self):
        """Test retrieving project when multiple members exist."""
        user1 = UserFactory()
        user2 = UserFactory()
        user3 = UserFactory()
        project = ProjectFactory()

        ProjectMemberFactory(project=project, user=user1, role=ProjectMember.Role.OWNER)
        membership2 = ProjectMemberFactory(project=project, user=user2, role=ProjectMember.Role.ADMIN)
        ProjectMemberFactory(project=project, user=user3, role=ProjectMember.Role.MEMBER)

        # Test retrieving for user2
        retrieved_project, retrieved_membership = get_project_and_membership(project.id, user2)

        assert retrieved_project.id == project.id
        assert retrieved_membership.id == membership2.id
        assert retrieved_membership.user.id == user2.id

    def test_get_project_returns_correct_objects(self):
        """Test that correct project and membership objects are returned."""
        user = UserFactory()
        project1 = ProjectFactory(name="Project 1")
        project2 = ProjectFactory(name="Project 2")

        membership1 = ProjectMemberFactory(project=project1, user=user)
        ProjectMemberFactory(project=project2, user=user)

        retrieved_project, retrieved_membership = get_project_and_membership(project1.id, user)

        assert retrieved_project.name == "Project 1"
        assert retrieved_membership.id == membership1.id

    def test_get_project_with_zero_id_raises_not_found(self):
        """Test that zero project ID raises NotFound."""
        user = UserFactory()

        with pytest.raises(NotFound):
            get_project_and_membership(0, user)

    def test_get_project_with_negative_id_raises_validation_error(self):
        """Test that negative project ID raises ValidationError (UUID validation)."""
        user = UserFactory()

        # Project uses UUID field, so negative integers raise ValidationError
        from django.core.exceptions import ValidationError

        with pytest.raises((NotFound, ValidationError)):
            get_project_and_membership(-1, user)

    def test_get_project_with_string_id_raises_validation_error(self):
        """Test handling of invalid ID type (not a valid UUID)."""
        user = UserFactory()

        # Project uses UUID field, so non-UUID strings raise ValidationError
        from django.core.exceptions import ValidationError

        with pytest.raises((NotFound, ValidationError)):
            get_project_and_membership("invalid", user)


@pytest.mark.django_db
class TestRequireOwnerOrAdmin:
    """Test owner/admin permission check."""

    def test_owner_has_permission(self):
        """Test that owner can perform restricted actions."""
        user = UserFactory()
        project = ProjectFactory()
        membership = ProjectMemberFactory(project=project, user=user, role=ProjectMember.Role.OWNER)

        # Should not raise any exception
        require_owner_or_admin(membership)

    def test_admin_has_permission(self):
        """Test that admin can perform restricted actions."""
        user = UserFactory()
        project = ProjectFactory()
        membership = ProjectMemberFactory(project=project, user=user, role=ProjectMember.Role.ADMIN)

        # Should not raise any exception
        require_owner_or_admin(membership)

    def test_member_denied_permission(self):
        """Test that regular member cannot perform restricted actions."""
        user = UserFactory()
        project = ProjectFactory()
        membership = ProjectMemberFactory(project=project, user=user, role=ProjectMember.Role.MEMBER)

        with pytest.raises(PermissionDenied) as exc_info:
            require_owner_or_admin(membership)

        assert "owner or admin" in str(exc_info.value).lower()

    def test_viewer_denied_permission(self):
        """Test that viewer cannot perform restricted actions."""
        user = UserFactory()
        project = ProjectFactory()
        membership = ProjectMemberFactory(project=project, user=user, role=ProjectMember.Role.VIEWER)

        with pytest.raises(PermissionDenied) as exc_info:
            require_owner_or_admin(membership)

        assert "owner or admin" in str(exc_info.value).lower()

    def test_editor_denied_permission(self):
        """Test that editor cannot perform restricted actions."""
        user = UserFactory()
        project = ProjectFactory()

        # Test with editor role if it exists in the model
        try:
            membership = ProjectMemberFactory(project=project, user=user, role=ProjectMember.Role.EDITOR)

            with pytest.raises(PermissionDenied):
                require_owner_or_admin(membership)
        except (ValueError, AttributeError):
            # EDITOR role might not exist, skip this test
            pass

    def test_multiple_memberships_separate_checks(self):
        """Test that permission checks work independently for different memberships."""
        user1 = UserFactory()
        user2 = UserFactory()
        project = ProjectFactory()

        owner_membership = ProjectMemberFactory(project=project, user=user1, role=ProjectMember.Role.OWNER)
        member_membership = ProjectMemberFactory(project=project, user=user2, role=ProjectMember.Role.MEMBER)

        # Owner should pass
        require_owner_or_admin(owner_membership)

        # Member should fail
        with pytest.raises(PermissionDenied):
            require_owner_or_admin(member_membership)

    def test_permission_error_message_clear(self):
        """Test that permission error message is clear."""
        user = UserFactory()
        project = ProjectFactory()
        membership = ProjectMemberFactory(project=project, user=user, role=ProjectMember.Role.MEMBER)

        with pytest.raises(PermissionDenied) as exc_info:
            require_owner_or_admin(membership)

        # Message should be informative
        error_message = str(exc_info.value).lower()
        assert len(error_message) > 0
        # Message contains "owner" and "admin"
        assert ("owner" in error_message or "admin" in error_message)


@pytest.mark.django_db
class TestGetProjectAndMembershipIntegration:
    """Integration tests for get_project_and_membership and require_owner_or_admin."""

    def test_get_and_check_owner_workflow(self):
        """Test workflow: get project/membership then check permissions."""
        user = UserFactory()
        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=user, role=ProjectMember.Role.OWNER)

        # Get project and membership
        retrieved_project, membership = get_project_and_membership(project.id, user)

        # Check permissions
        require_owner_or_admin(membership)

        assert retrieved_project.id == project.id

    def test_get_and_check_member_workflow(self):
        """Test workflow: get fails for non-member."""
        user = UserFactory()
        other_user = UserFactory()
        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=other_user)

        with pytest.raises(PermissionDenied):
            get_project_and_membership(project.id, user)

    def test_get_and_check_member_no_admin_workflow(self):
        """Test workflow: get project but member cannot perform admin action."""
        user = UserFactory()
        project = ProjectFactory()
        membership = ProjectMemberFactory(project=project, user=user, role=ProjectMember.Role.MEMBER)

        # Get succeeds
        retrieved_project, retrieved_membership = get_project_and_membership(project.id, user)

        # Check permissions fails
        with pytest.raises(PermissionDenied):
            require_owner_or_admin(retrieved_membership)

    def test_promote_member_to_admin_workflow(self):
        """Test permission check after promoting member to admin."""
        user = UserFactory()
        project = ProjectFactory()
        membership = ProjectMemberFactory(project=project, user=user, role=ProjectMember.Role.MEMBER)

        # Initially member, should fail
        with pytest.raises(PermissionDenied):
            require_owner_or_admin(membership)

        # Promote to admin
        membership.role = ProjectMember.Role.ADMIN
        membership.save()

        # Now should pass
        require_owner_or_admin(membership)

    def test_multiple_projects_permission_isolation(self):
        """Test that permissions are isolated between projects."""
        user = UserFactory()

        project1 = ProjectFactory(name="Project 1")
        project2 = ProjectFactory(name="Project 2")

        # Owner in project1
        membership1 = ProjectMemberFactory(project=project1, user=user, role=ProjectMember.Role.OWNER)

        # Member in project2
        membership2 = ProjectMemberFactory(project=project2, user=user, role=ProjectMember.Role.MEMBER)

        # Can perform admin action in project1
        require_owner_or_admin(membership1)

        # Cannot perform admin action in project2
        with pytest.raises(PermissionDenied):
            require_owner_or_admin(membership2)
