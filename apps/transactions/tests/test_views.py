"""
Tests for transactions/views.py - Transaction and Category API endpoints.

Tests:
- CategoryListCreateView - List and create categories
- CategoryDetailView - Retrieve, update, delete categories
- DefaultCategoryListView - List default categories
- TransactionListCreateView - List and create transactions
- TransactionDetailView - Retrieve, update, delete transactions
"""

import pytest
from decimal import Decimal
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from apps.transactions.tests.factories import (
    TransactionFactory,
    CategoryFactory,
)
from apps.projects.tests.factories import ProjectFactory, ProjectMemberFactory
from apps.projects.models import ProjectMember
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
class TestCategoryListCreateView:
    """Test CategoryListCreateView endpoint."""

    def test_list_categories_authenticated_user(self, api_client, authenticated_user, project_with_user):
        """Test that authenticated user can list project categories."""
        api_client.force_authenticate(user=authenticated_user)

        # Create some categories
        CategoryFactory.create_batch(3, project=project_with_user)

        url = f"/api/projects/{project_with_user.id}/categories/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 3

    def test_list_categories_includes_defaults(self, api_client, authenticated_user, project_with_user):
        """Test that default categories are included in list."""
        api_client.force_authenticate(user=authenticated_user)

        # Create default category
        CategoryFactory(is_default=True)

        url = f"/api/projects/{project_with_user.id}/categories/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Should include default categories
        assert any(cat.get("is_default") for cat in response.data)

    def test_create_category_owner(self, api_client, authenticated_user, project_with_user):
        """Test that project owner can create categories."""
        api_client.force_authenticate(user=authenticated_user)

        data = {
            "name": "New Category",
            "category_type": "expense",
            "color": "#FF5733",
        }

        url = f"/api/projects/{project_with_user.id}/categories/"
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "New Category"

    def test_create_category_non_member(self, api_client, authenticated_user):
        """Test that non-member cannot create category."""
        other_user = UserFactory()
        project = ProjectFactory(owner=other_user)

        api_client.force_authenticate(user=authenticated_user)

        data = {
            "name": "New Category",
            "category_type": "expense",
        }

        url = f"/api/projects/{project.id}/categories/"
        response = api_client.post(url, data, format="json")

        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

    def test_unauthenticated_list_categories(self, api_client, project_with_user):
        """Test that unauthenticated user cannot list categories."""
        url = f"/api/projects/{project_with_user.id}/categories/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCategoryDetailView:
    """Test CategoryDetailView endpoint."""

    def test_retrieve_category(self, api_client, authenticated_user, project_with_user):
        """Test retrieving a single category."""
        api_client.force_authenticate(user=authenticated_user)

        category = CategoryFactory(project=project_with_user)

        url = f"/api/projects/{project_with_user.id}/categories/{category.id}/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == category.name

    def test_update_category_owner(self, api_client, authenticated_user, project_with_user):
        """Test that owner can update category."""
        api_client.force_authenticate(user=authenticated_user)

        category = CategoryFactory(project=project_with_user, name="Old Name")

        data = {"name": "New Name"}
        url = f"/api/projects/{project_with_user.id}/categories/{category.id}/"
        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "New Name"

    def test_delete_category_owner(self, api_client, authenticated_user, project_with_user):
        """Test that owner can delete category."""
        api_client.force_authenticate(user=authenticated_user)

        category = CategoryFactory(project=project_with_user)
        category_id = category.id

        url = f"/api/projects/{project_with_user.id}/categories/{category.id}/"
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestDefaultCategoryListView:
    """Test DefaultCategoryListView endpoint."""

    def test_list_default_categories(self, api_client, authenticated_user):
        """Test that default categories can be listed."""
        api_client.force_authenticate(user=authenticated_user)

        # Create default categories
        CategoryFactory.create_batch(3, is_default=True)

        url = "/api/categories/default/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 3

    def test_default_categories_have_is_default_true(self, api_client, authenticated_user):
        """Test that all returned categories have is_default=True."""
        api_client.force_authenticate(user=authenticated_user)

        CategoryFactory.create_batch(2, is_default=True)

        url = "/api/categories/default/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        for cat in response.data:
            assert cat["is_default"] is True


@pytest.mark.django_db
class TestTransactionListCreateView:
    """Test TransactionListCreateView endpoint."""

    def test_list_transactions(self, api_client, authenticated_user, project_with_user):
        """Test listing project transactions."""
        api_client.force_authenticate(user=authenticated_user)

        category = CategoryFactory(project=project_with_user)
        TransactionFactory.create_batch(
            3,
            project=project_with_user,
            created_by=authenticated_user,
            category=category,
        )

        url = f"/api/projects/{project_with_user.id}/transactions/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 3

    def test_create_transaction(self, api_client, authenticated_user, project_with_user):
        """Test creating a transaction."""
        api_client.force_authenticate(user=authenticated_user)

        category = CategoryFactory(project=project_with_user)

        data = {
            "category": category.id,
            "transaction_type": "expense",
            "amount": "50.75",
            "currency": "USD",
            "description": "Test transaction",
            "date": timezone.now().date(),
        }

        url = f"/api/projects/{project_with_user.id}/transactions/"
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["amount"] == "50.75"

    def test_filter_transactions_by_category(self, api_client, authenticated_user, project_with_user):
        """Test filtering transactions by category."""
        api_client.force_authenticate(user=authenticated_user)

        category1 = CategoryFactory(project=project_with_user, name="Food")
        category2 = CategoryFactory(project=project_with_user, name="Transport")

        TransactionFactory(
            project=project_with_user,
            created_by=authenticated_user,
            category=category1,
        )
        TransactionFactory(
            project=project_with_user,
            created_by=authenticated_user,
            category=category2,
        )

        url = f"/api/projects/{project_with_user.id}/transactions/?category={category1.id}"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        # Results should be filtered
        for transaction in response.data.get("results", []):
            if transaction:
                assert transaction["category"] == category1.id

    def test_search_transactions(self, api_client, authenticated_user, project_with_user):
        """Test searching transactions by description."""
        api_client.force_authenticate(user=authenticated_user)

        category = CategoryFactory(project=project_with_user)
        TransactionFactory(
            project=project_with_user,
            created_by=authenticated_user,
            category=category,
            description="Unique description",
        )

        url = f"/api/projects/{project_with_user.id}/transactions/?search=Unique"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_order_transactions_by_date(self, api_client, authenticated_user, project_with_user):
        """Test ordering transactions by date."""
        api_client.force_authenticate(user=authenticated_user)

        category = CategoryFactory(project=project_with_user)
        TransactionFactory.create_batch(
            3,
            project=project_with_user,
            created_by=authenticated_user,
            category=category,
        )

        url = f"/api/projects/{project_with_user.id}/transactions/?ordering=-date"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestTransactionDetailView:
    """Test TransactionDetailView endpoint."""

    def test_retrieve_transaction(self, api_client, authenticated_user, project_with_user):
        """Test retrieving a single transaction."""
        api_client.force_authenticate(user=authenticated_user)

        category = CategoryFactory(project=project_with_user)
        transaction = TransactionFactory(
            project=project_with_user,
            created_by=authenticated_user,
            category=category,
        )

        url = f"/api/projects/{project_with_user.id}/transactions/{transaction.id}/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["amount"] == str(transaction.amount)

    def test_update_transaction(self, api_client, authenticated_user, project_with_user):
        """Test updating a transaction."""
        api_client.force_authenticate(user=authenticated_user)

        category = CategoryFactory(project=project_with_user)
        transaction = TransactionFactory(
            project=project_with_user,
            created_by=authenticated_user,
            category=category,
            description="Old description",
        )

        data = {"description": "New description"}
        url = f"/api/projects/{project_with_user.id}/transactions/{transaction.id}/"
        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["description"] == "New description"

    def test_delete_transaction(self, api_client, authenticated_user, project_with_user):
        """Test deleting a transaction."""
        api_client.force_authenticate(user=authenticated_user)

        category = CategoryFactory(project=project_with_user)
        transaction = TransactionFactory(
            project=project_with_user,
            created_by=authenticated_user,
            category=category,
        )

        url = f"/api/projects/{project_with_user.id}/transactions/{transaction.id}/"
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestViewPermissions:
    """Test permission checks across all views."""

    def test_member_can_view_transactions(self, api_client, authenticated_user):
        """Test that project member can view transactions."""
        owner = UserFactory()
        project = ProjectFactory(owner=owner)

        # Add authenticated_user as member
        ProjectMemberFactory(project=project, user=authenticated_user)

        api_client.force_authenticate(user=authenticated_user)

        url = f"/api/projects/{project.id}/transactions/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_admin_can_create_category(self, api_client, authenticated_user):
        """Test that admin member can create categories."""
        owner = UserFactory()
        project = ProjectFactory(owner=owner)

        # Add authenticated_user as admin
        ProjectMemberFactory(
            project=project,
            user=authenticated_user,
            role=ProjectMember.Role.ADMIN,
        )

        api_client.force_authenticate(user=authenticated_user)

        data = {
            "name": "Admin Category",
            "category_type": "expense",
        }

        url = f"/api/projects/{project.id}/categories/"
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

    def test_member_cannot_create_category(self, api_client, authenticated_user):
        """Test that regular member cannot create categories."""
        owner = UserFactory()
        project = ProjectFactory(owner=owner)

        # Add authenticated_user as member (not admin)
        ProjectMemberFactory(
            project=project,
            user=authenticated_user,
            role=ProjectMember.Role.MEMBER,
        )

        api_client.force_authenticate(user=authenticated_user)

        data = {
            "name": "Member Category",
            "category_type": "expense",
        }

        url = f"/api/projects/{project.id}/categories/"
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
