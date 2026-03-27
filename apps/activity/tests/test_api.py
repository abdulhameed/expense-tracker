from datetime import timedelta
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.tests.factories import UserFactory, VerifiedUserFactory
from apps.projects.models import ProjectMember
from apps.projects.tests.factories import ProjectFactory, ProjectMemberFactory
from apps.transactions.tests.factories import TransactionFactory, CategoryFactory
from apps.budgets.tests.factories import BudgetFactory
from apps.activity.models import ActivityLog


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


@pytest.fixture
def project_owner(user):
    return user


@pytest.fixture
def project_with_owner(project_owner):
    return ProjectFactory(owner=project_owner)


@pytest.fixture
def project_member(project_with_owner):
    user = VerifiedUserFactory()
    ProjectMemberFactory(project=project_with_owner, user=user, role=ProjectMember.Role.MEMBER)
    return user


@pytest.mark.django_db
class TestProjectActivityLogView:
    """Test project activity log endpoint."""

    def get_url(self, project_id):
        return reverse("project-activity-log", kwargs={"project_id": project_id})

    def test_list_project_activities(self, auth_client, project_with_owner, project_owner):
        """Test listing activities for a project."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        # Create some activities
        TransactionFactory(project=project_with_owner, created_by=project_owner)
        TransactionFactory(project=project_with_owner, created_by=project_owner)

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 2

    def test_list_activities_as_member(self, project_with_owner, project_member):
        """Test that project members can view activities."""
        client = APIClient()
        client.force_authenticate(user=project_member)

        # Create some activities
        TransactionFactory(project=project_with_owner, created_by=project_member)

        url = reverse("project-activity-log", kwargs={"project_id": project_with_owner.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_list_activities_non_member(self, project_with_owner):
        """Test that non-members cannot view activities."""
        other_user = VerifiedUserFactory()
        client = APIClient()
        client.force_authenticate(user=other_user)

        url = self.get_url(project_with_owner.id)
        response = client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_activities_unauthenticated(self, client, project_with_owner):
        """Test that unauthenticated users cannot view activities."""
        url = self.get_url(project_with_owner.id)
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_filter_activities_by_action(self, auth_client, project_with_owner, project_owner):
        """Test filtering activities by action type."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        # Create activities
        TransactionFactory(project=project_with_owner, created_by=project_owner)
        BudgetFactory(project=project_with_owner, created_by=project_owner)

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url + "?action=create")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 2

    def test_filter_activities_by_content_type(self, auth_client, project_with_owner, project_owner):
        """Test filtering activities by content type."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        TransactionFactory(project=project_with_owner, created_by=project_owner)
        BudgetFactory(project=project_with_owner, created_by=project_owner)

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url + "?content_type=transaction")

        assert response.status_code == status.HTTP_200_OK

    def test_search_activities(self, auth_client, project_with_owner, project_owner):
        """Test searching activities by description."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        TransactionFactory(
            project=project_with_owner,
            created_by=project_owner,
            title="Unique Transaction Title"
        )

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url + "?search=Unique")

        assert response.status_code == status.HTTP_200_OK

    def test_ordering_activities(self, auth_client, project_with_owner, project_owner):
        """Test ordering of activities."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        TransactionFactory(project=project_with_owner, created_by=project_owner)
        TransactionFactory(project=project_with_owner, created_by=project_owner)

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url + "?ordering=-created_at")

        assert response.status_code == status.HTTP_200_OK
        if response.data["count"] > 1:
            # Verify ordering (most recent first)
            first_date = response.data["results"][0]["created_at"]
            second_date = response.data["results"][1]["created_at"]
            assert first_date >= second_date


@pytest.mark.django_db
class TestUserActivityLogView:
    """Test user activity log endpoint."""

    def get_url(self):
        return reverse("user-activity-log")

    def test_list_user_activities(self, auth_client, user):
        """Test listing activities by the current user."""
        project = ProjectFactory(owner=user)

        # Create some activities
        TransactionFactory(project=project, created_by=user)
        TransactionFactory(project=project, created_by=user)

        url = self.get_url()
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 2

    def test_user_activities_only_their_own(self, auth_client, user):
        """Test that users only see their own activities."""
        other_user = UserFactory()
        project = ProjectFactory(owner=other_user)

        # Activity by other user
        TransactionFactory(project=project, created_by=other_user)

        # Activity by authenticated user
        project2 = ProjectFactory(owner=user)
        TransactionFactory(project=project2, created_by=user)

        url = self.get_url()
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Should only see their own activities
        for activity in response.data["results"]:
            assert activity["user"] == str(user.id)

    def test_user_activities_unauthenticated(self, client):
        """Test that unauthenticated users cannot view user activities."""
        url = self.get_url()
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_filter_user_activities_by_project(self, auth_client, user):
        """Test filtering user activities by project."""
        project1 = ProjectFactory(owner=user)
        project2 = ProjectFactory(owner=user)

        TransactionFactory(project=project1, created_by=user)
        TransactionFactory(project=project2, created_by=user)

        url = self.get_url()
        response = auth_client.get(url + f"?project={project1.id}")

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestObjectActivityLogView:
    """Test activity log for a specific object."""

    def get_url(self, project_id, content_type, object_id):
        return reverse(
            "object-activity-log",
            kwargs={
                "project_id": project_id,
                "content_type": content_type,
                "object_id": object_id,
            },
        )

    def test_list_transaction_activities(self, auth_client, project_with_owner, project_owner):
        """Test listing activities for a specific transaction."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        transaction = TransactionFactory(project=project_with_owner, created_by=project_owner)

        url = self.get_url(project_with_owner.id, "transaction", transaction.id)
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1
        assert response.data["results"][0]["object_id"] == str(transaction.id)

    def test_object_activity_non_member(self, project_with_owner):
        """Test that non-members cannot view object activities."""
        other_user = VerifiedUserFactory()
        client = APIClient()
        client.force_authenticate(user=other_user)

        transaction = TransactionFactory(project=project_with_owner, created_by=project_with_owner.owner)

        url = self.get_url(project_with_owner.id, "transaction", transaction.id)
        response = client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_object_activity_unauthenticated(self, client, project_with_owner):
        """Test that unauthenticated users cannot view object activities."""
        import uuid
        url = self.get_url(project_with_owner.id, "transaction", uuid.uuid4())
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestActivityLogSerialization:
    """Test activity log serialization in API responses."""

    def test_activity_includes_user_info(self, auth_client, project_with_owner, project_owner):
        """Test that activity response includes user information."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        TransactionFactory(project=project_with_owner, created_by=project_owner)

        url = reverse("project-activity-log", kwargs={"project_id": project_with_owner.id})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["results"][0]["user_email"] == project_owner.email
        assert "user_name" in response.data["results"][0]

    def test_activity_includes_action_display(self, auth_client, project_with_owner, project_owner):
        """Test that activity response includes display name for action."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        TransactionFactory(project=project_with_owner, created_by=project_owner)

        url = reverse("project-activity-log", kwargs={"project_id": project_with_owner.id})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "action_display" in response.data["results"][0]
        assert response.data["results"][0]["action_display"] == "Created"

    def test_activity_includes_metadata(self, auth_client, project_with_owner, project_owner):
        """Test that activity response includes metadata."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        TransactionFactory(project=project_with_owner, created_by=project_owner)

        url = reverse("project-activity-log", kwargs={"project_id": project_with_owner.id})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "metadata" in response.data["results"][0]
