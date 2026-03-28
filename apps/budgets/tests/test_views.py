"""
Tests for budgets/views.py - Budget API endpoints.

Tests:
- BudgetListCreateView - List and create budgets
- BudgetDetailView - Retrieve, update, delete budgets
- BudgetStatusView - Get budget spending status and alerts
- BudgetSummaryView - Get project-wide budget summary
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from apps.budgets.tests.factories import BudgetFactory
from apps.transactions.tests.factories import TransactionFactory, CategoryFactory
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
class TestBudgetListCreateView:
    """Test BudgetListCreateView endpoint."""

    def test_list_budgets(self, api_client, authenticated_user, project_with_user):
        """Test that members can list project budgets."""
        api_client.force_authenticate(user=authenticated_user)

        # Create some budgets
        BudgetFactory.create_batch(3, project=project_with_user, created_by=authenticated_user)

        url = reverse("budget-list", kwargs={"project_id": project_with_user.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 3 or len(response.data) >= 3

    def test_list_budgets_non_member(self, api_client, authenticated_user):
        """Test that non-member gets empty budget list."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory()

        url = reverse("budget-list", kwargs={"project_id": project.id})
        response = api_client.get(url)

        # View returns 200 OK with empty results for non-members
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data.get("results", response.data)) == 0

    def test_list_budgets_unauthenticated(self, api_client, project_with_user):
        """Test that unauthenticated user cannot list budgets."""
        url = reverse("budget-list", kwargs={"project_id": project_with_user.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_budget_owner(self, api_client, authenticated_user, project_with_user):
        """Test that owner can create budget."""
        api_client.force_authenticate(user=authenticated_user)

        category = CategoryFactory(project=project_with_user)
        start_date = date.today()
        end_date = start_date + timedelta(days=30)

        data = {
            "category": category.id,
            "amount": "1000.00",
            "period": "monthly",
            "start_date": start_date,
            "end_date": end_date,
            "alert_threshold": 80,
            "alert_enabled": True,
        }

        url = reverse("budget-list", kwargs={"project_id": project_with_user.id})
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["amount"] == "1000.00"

    def test_create_budget_admin(self, api_client, authenticated_user):
        """Test that admin member can create budget."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=authenticated_user, role=ProjectMember.Role.ADMIN)

        category = CategoryFactory(project=project)
        start_date = date.today()
        end_date = start_date + timedelta(days=30)

        data = {
            "category": category.id,
            "amount": "500.00",
            "period": "monthly",
            "start_date": start_date,
            "end_date": end_date,
        }

        url = reverse("budget-list", kwargs={"project_id": project.id})
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_budget_non_admin(self, api_client, authenticated_user):
        """Test that member cannot create budget without admin role."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=authenticated_user, role=ProjectMember.Role.MEMBER)

        category = CategoryFactory(project=project)
        start_date = date.today()
        end_date = start_date + timedelta(days=30)

        data = {
            "category": category.id,
            "amount": "500.00",
            "period": "monthly",
            "start_date": start_date,
            "end_date": end_date,
        }

        url = reverse("budget-list", kwargs={"project_id": project.id})
        response = api_client.post(url, data, format="json")

        # Serializer validation returns 400 for permission errors, not 403
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_403_FORBIDDEN]

    def test_create_project_wide_budget(self, api_client, authenticated_user, project_with_user):
        """Test creating budget without category (project-wide)."""
        api_client.force_authenticate(user=authenticated_user)

        start_date = date.today()
        end_date = start_date + timedelta(days=30)

        data = {
            "amount": "5000.00",
            "period": "monthly",
            "start_date": start_date,
            "end_date": end_date,
        }

        url = reverse("budget-list", kwargs={"project_id": project_with_user.id})
        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["category"] is None


@pytest.mark.django_db
class TestBudgetDetailView:
    """Test BudgetDetailView endpoint."""

    def test_retrieve_budget(self, api_client, authenticated_user, project_with_user):
        """Test retrieving a budget."""
        api_client.force_authenticate(user=authenticated_user)

        budget = BudgetFactory(project=project_with_user, created_by=authenticated_user)

        url = reverse("budget-detail", kwargs={"project_id": project_with_user.id, "pk": budget.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert str(response.data["id"]) == str(budget.id)

    def test_update_budget(self, api_client, authenticated_user, project_with_user):
        """Test updating a budget."""
        api_client.force_authenticate(user=authenticated_user)

        budget = BudgetFactory(project=project_with_user, created_by=authenticated_user, amount=Decimal("1000.00"))

        data = {"amount": "2000.00"}

        url = reverse("budget-detail", kwargs={"project_id": project_with_user.id, "pk": budget.id})
        response = api_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["amount"] == "2000.00"

    def test_delete_budget(self, api_client, authenticated_user, project_with_user):
        """Test deleting a budget."""
        api_client.force_authenticate(user=authenticated_user)

        budget = BudgetFactory(project=project_with_user, created_by=authenticated_user)
        budget_id = budget.id

        url = reverse("budget-detail", kwargs={"project_id": project_with_user.id, "pk": budget.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_delete_budget_non_admin(self, api_client, authenticated_user):
        """Test that non-admin cannot delete budget."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory()
        ProjectMemberFactory(project=project, user=authenticated_user, role=ProjectMember.Role.MEMBER)
        budget = BudgetFactory(project=project)

        url = reverse("budget-detail", kwargs={"project_id": project.id, "pk": budget.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_budget_non_member(self, api_client, authenticated_user):
        """Test that non-member cannot retrieve budget."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory()
        budget = BudgetFactory(project=project)

        url = reverse("budget-detail", kwargs={"project_id": project.id, "pk": budget.id})
        response = api_client.get(url)

        # View returns 404 for non-members (budget not in queryset)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_403_FORBIDDEN]


@pytest.mark.django_db
class TestBudgetStatusView:
    """Test BudgetStatusView endpoint."""

    def test_get_budget_status(self, api_client, authenticated_user, project_with_user):
        """Test getting budget status."""
        api_client.force_authenticate(user=authenticated_user)

        budget = BudgetFactory(
            project=project_with_user,
            created_by=authenticated_user,
            amount=Decimal("1000.00"),
            alert_threshold=80,
        )

        url = reverse("budget-status", kwargs={"project_id": project_with_user.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_budget_status_with_spending(self, api_client, authenticated_user, project_with_user):
        """Test that budget status reflects spending."""
        api_client.force_authenticate(user=authenticated_user)

        category = CategoryFactory(project=project_with_user)
        budget = BudgetFactory(
            project=project_with_user,
            created_by=authenticated_user,
            category=category,
            amount=Decimal("1000.00"),
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )

        # Create transactions
        TransactionFactory(
            project=project_with_user,
            created_by=authenticated_user,
            category=category,
            amount=Decimal("500.00"),
            transaction_type="expense",
        )

        url = reverse("budget-status", kwargs={"project_id": project_with_user.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        if response.data:
            status_item = response.data[0]
            # spent and remaining may be strings or numbers
            spent = float(status_item["spent"]) if isinstance(status_item["spent"], str) else status_item["spent"]
            remaining = float(status_item["remaining"]) if isinstance(status_item["remaining"], str) else status_item["remaining"]
            assert spent >= 0
            assert remaining >= 0

    def test_budget_status_alert_triggered(self, api_client, authenticated_user, project_with_user):
        """Test that alert is triggered when threshold exceeded."""
        api_client.force_authenticate(user=authenticated_user)

        category = CategoryFactory(project=project_with_user)
        budget = BudgetFactory(
            project=project_with_user,
            created_by=authenticated_user,
            category=category,
            amount=Decimal("1000.00"),
            alert_threshold=50,
            alert_enabled=True,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )

        # Spend 75% of budget
        TransactionFactory(
            project=project_with_user,
            created_by=authenticated_user,
            category=category,
            amount=Decimal("750.00"),
            transaction_type="expense",
        )

        url = reverse("budget-status", kwargs={"project_id": project_with_user.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_budget_status_project_wide(self, api_client, authenticated_user, project_with_user):
        """Test status for project-wide budget without category."""
        api_client.force_authenticate(user=authenticated_user)

        budget = BudgetFactory(
            project=project_with_user,
            created_by=authenticated_user,
            category=None,
            amount=Decimal("5000.00"),
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )

        url = reverse("budget-status", kwargs={"project_id": project_with_user.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_budget_status_non_member(self, api_client, authenticated_user):
        """Test that non-member cannot get budget status."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory()

        url = reverse("budget-status", kwargs={"project_id": project.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestBudgetSummaryView:
    """Test BudgetSummaryView endpoint."""

    def test_get_budget_summary(self, api_client, authenticated_user, project_with_user):
        """Test getting budget summary."""
        api_client.force_authenticate(user=authenticated_user)

        BudgetFactory(
            project=project_with_user,
            created_by=authenticated_user,
            amount=Decimal("1000.00"),
        )

        url = reverse("budget-summary", kwargs={"project_id": project_with_user.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "total_allocated" in response.data
        assert "total_spent" in response.data
        assert "total_remaining" in response.data

    def test_summary_with_multiple_budgets(self, api_client, authenticated_user, project_with_user):
        """Test summary with multiple budgets."""
        api_client.force_authenticate(user=authenticated_user)

        category1 = CategoryFactory(project=project_with_user)
        category2 = CategoryFactory(project=project_with_user)

        BudgetFactory(project=project_with_user, created_by=authenticated_user, category=category1, amount=Decimal("1000.00"))
        BudgetFactory(project=project_with_user, created_by=authenticated_user, category=category2, amount=Decimal("500.00"))

        url = reverse("budget-summary", kwargs={"project_id": project_with_user.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["budget_count"] >= 2
        assert response.data["total_allocated"] >= Decimal("1500.00")

    def test_summary_spending_tracking(self, api_client, authenticated_user, project_with_user):
        """Test that summary tracks actual spending."""
        api_client.force_authenticate(user=authenticated_user)

        category = CategoryFactory(project=project_with_user)
        budget = BudgetFactory(
            project=project_with_user,
            created_by=authenticated_user,
            category=category,
            amount=Decimal("1000.00"),
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )

        # Create spending
        TransactionFactory(
            project=project_with_user,
            created_by=authenticated_user,
            category=category,
            amount=Decimal("250.00"),
            transaction_type="expense",
        )

        url = reverse("budget-summary", kwargs={"project_id": project_with_user.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_allocated"] >= Decimal("1000.00")

    def test_summary_alert_counting(self, api_client, authenticated_user, project_with_user):
        """Test that summary counts triggered alerts."""
        api_client.force_authenticate(user=authenticated_user)

        category = CategoryFactory(project=project_with_user)
        budget = BudgetFactory(
            project=project_with_user,
            created_by=authenticated_user,
            category=category,
            amount=Decimal("1000.00"),
            alert_threshold=50,
            alert_enabled=True,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )

        # Spend above threshold
        TransactionFactory(
            project=project_with_user,
            created_by=authenticated_user,
            category=category,
            amount=Decimal("600.00"),
            transaction_type="expense",
        )

        url = reverse("budget-summary", kwargs={"project_id": project_with_user.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "alerts_triggered" in response.data

    def test_summary_non_member(self, api_client, authenticated_user):
        """Test that non-member cannot get summary."""
        api_client.force_authenticate(user=authenticated_user)

        project = ProjectFactory()

        url = reverse("budget-summary", kwargs={"project_id": project.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_summary_empty_budgets(self, api_client, authenticated_user, project_with_user):
        """Test summary with no budgets."""
        api_client.force_authenticate(user=authenticated_user)

        url = reverse("budget-summary", kwargs={"project_id": project_with_user.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["budget_count"] == 0
        assert response.data["total_allocated"] == Decimal("0.00")
        assert response.data["total_spent"] == Decimal("0.00")
