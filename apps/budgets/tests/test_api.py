from datetime import timedelta
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.tests.factories import UserFactory, VerifiedUserFactory
from apps.budgets.models import Budget
from apps.projects.models import ProjectMember
from apps.projects.tests.factories import ProjectFactory, ProjectMemberFactory
from apps.transactions.tests.factories import CategoryFactory, TransactionFactory

from .factories import BudgetFactory, BudgetWithCategoryFactory


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
def project_admin(project_with_owner):
    user = VerifiedUserFactory()
    ProjectMemberFactory(project=project_with_owner, user=user, role=ProjectMember.Role.ADMIN)
    return user


@pytest.fixture
def project_member(project_with_owner):
    user = VerifiedUserFactory()
    ProjectMemberFactory(project=project_with_owner, user=user, role=ProjectMember.Role.MEMBER)
    return user


# ---------------------------------------------------------------------------
# Budget CRUD Tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestBudgetListCreateView:
    """Test listing and creating budgets."""

    def get_url(self, project_id):
        return reverse("budget-list", kwargs={"project_id": project_id})

    def test_list_project_budgets(self, auth_client, project_with_owner, project_owner):
        """Test listing budgets for a project."""
        # Add user as owner
        project_with_owner.owner = project_owner
        project_with_owner.save()

        BudgetFactory(project=project_with_owner)
        BudgetFactory(project=project_with_owner)

        # Other project's budgets shouldn't be included
        other_project = ProjectFactory()
        BudgetFactory(project=other_project)

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

    def test_create_budget_as_owner(self, auth_client, project_with_owner, project_owner):
        """Test creating a budget as project owner."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        url = self.get_url(project_with_owner.id)
        payload = {
            "amount": "1000.00",
            "period": "monthly",
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
            "alert_threshold": 80,
            "alert_enabled": True,
        }

        response = auth_client.post(url, payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["amount"] == "1000.00"
        assert response.data["period"] == "monthly"

    def test_create_budget_with_category(self, auth_client, project_with_owner, project_owner):
        """Test creating a budget with a category."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        category = CategoryFactory(project=project_with_owner)
        url = self.get_url(project_with_owner.id)

        payload = {
            "amount": "500.00",
            "category": str(category.id),
            "period": "monthly",
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
        }

        response = auth_client.post(url, payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["category"] == str(category.id)

    def test_create_budget_as_member_denied(self, project_with_owner, project_member):
        """Test that regular members cannot create budgets."""
        client = APIClient()
        client.force_authenticate(user=project_member)

        url = self.get_url(project_with_owner.id)
        payload = {
            "amount": "1000.00",
            "period": "monthly",
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
        }

        response = client.post(url, payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_budget_as_admin_allowed(self, auth_client, project_with_owner, project_admin):
        """Test that admins can create budgets."""
        admin_client = APIClient()
        admin_client.force_authenticate(user=project_admin)

        url = self.get_url(project_with_owner.id)
        payload = {
            "amount": "1000.00",
            "period": "monthly",
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
        }

        response = admin_client.post(url, payload)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_budget_invalid_amount(self, auth_client, project_with_owner, project_owner):
        """Test creating budget with invalid amount."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        url = self.get_url(project_with_owner.id)

        # Negative amount
        response = auth_client.post(url, {
            "amount": "-100.00",
            "period": "monthly",
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Zero amount
        response = auth_client.post(url, {
            "amount": "0.00",
            "period": "monthly",
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_budget_invalid_dates(self, auth_client, project_with_owner, project_owner):
        """Test creating budget with invalid date range."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        url = self.get_url(project_with_owner.id)
        payload = {
            "amount": "1000.00",
            "period": "monthly",
            "start_date": "2026-01-31",
            "end_date": "2026-01-01",  # end before start
        }

        response = auth_client.post(url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_budget_invalid_threshold(self, auth_client, project_with_owner, project_owner):
        """Test creating budget with invalid alert threshold."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        url = self.get_url(project_with_owner.id)

        # Threshold > 100
        response = auth_client.post(url, {
            "amount": "1000.00",
            "period": "monthly",
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
            "alert_threshold": 150,
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Threshold < 0
        response = auth_client.post(url, {
            "amount": "1000.00",
            "period": "monthly",
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
            "alert_threshold": -10,
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_budgets_non_member(self, client):
        """Test that non-members cannot list budgets."""
        project = ProjectFactory()
        other_user = VerifiedUserFactory()
        client.force_authenticate(user=other_user)

        url = self.get_url(project.id)
        response = client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_budget_unauthenticated(self, client, project_with_owner):
        """Test that unauthenticated users cannot create budgets."""
        url = self.get_url(project_with_owner.id)
        response = client.post(url, {"amount": "1000"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestBudgetDetailView:
    """Test retrieving, updating, and deleting budgets."""

    def get_url(self, project_id, budget_id):
        return reverse("budget-detail", kwargs={"project_id": project_id, "pk": budget_id})

    def test_get_budget_details(self, auth_client, project_with_owner, project_owner):
        """Test retrieving budget details."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        budget = BudgetFactory(project=project_with_owner, created_by=project_owner)
        url = self.get_url(project_with_owner.id, budget.id)

        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["id"] == str(budget.id)

    def test_update_budget_as_owner(self, auth_client, project_with_owner, project_owner):
        """Test updating budget as project owner."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        budget = BudgetFactory(project=project_with_owner)
        url = self.get_url(project_with_owner.id, budget.id)

        response = auth_client.patch(url, {"amount": "2000.00"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["amount"] == "2000.00"

    def test_update_budget_as_member_denied(self, project_with_owner, project_member):
        """Test that members cannot update budgets."""
        budget = BudgetFactory(project=project_with_owner)

        client = APIClient()
        client.force_authenticate(user=project_member)
        url = self.get_url(project_with_owner.id, budget.id)

        response = client.patch(url, {"amount": "2000.00"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_budget_as_owner(self, auth_client, project_with_owner, project_owner):
        """Test deleting budget as project owner."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        budget = BudgetFactory(project=project_with_owner)
        url = self.get_url(project_with_owner.id, budget.id)

        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Budget.objects.filter(id=budget.id).exists()

    def test_delete_budget_as_member_denied(self, project_with_owner, project_member):
        """Test that members cannot delete budgets."""
        budget = BudgetFactory(project=project_with_owner)

        client = APIClient()
        client.force_authenticate(user=project_member)
        url = self.get_url(project_with_owner.id, budget.id)

        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_nonexistent_budget(self, auth_client, project_with_owner, project_owner):
        """Test retrieving non-existent budget."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        import uuid
        url = self.get_url(project_with_owner.id, uuid.uuid4())

        response = auth_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_budget_from_different_project(self, auth_client, project_with_owner, project_owner):
        """Test accessing budget from different project."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        other_project = ProjectFactory()
        budget = BudgetFactory(project=other_project)

        url = self.get_url(project_with_owner.id, budget.id)
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestBudgetStatusView:
    """Test budget status and spending calculations."""

    def get_url(self, project_id):
        return reverse("budget-status", kwargs={"project_id": project_id})

    def test_budget_status_no_transactions(self, auth_client, project_with_owner, project_owner):
        """Test budget status with no transactions."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        budget = BudgetFactory(
            project=project_with_owner,
            amount=Decimal("1000.00")
        )

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

        status_item = response.data[0]
        assert status_item["spent"] == Decimal("0.00")
        assert status_item["remaining"] == Decimal("1000.00")
        assert status_item["percentage_used"] == 0.0
        assert status_item["alert_triggered"] is False

    def test_budget_status_with_transactions(self, auth_client, project_with_owner, project_owner):
        """Test budget status with transactions."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        start = timezone.now().date()
        end = start + timedelta(days=30)

        budget = BudgetFactory(
            project=project_with_owner,
            amount=Decimal("1000.00"),
            start_date=start,
            end_date=end,
        )

        # Create transactions within budget period
        TransactionFactory(
            project=project_with_owner,
            amount=Decimal("300.00"),
            date=start,
            created_by=project_owner,
        )
        TransactionFactory(
            project=project_with_owner,
            amount=Decimal("400.00"),
            date=start + timedelta(days=10),
            created_by=project_owner,
        )

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        status_item = response.data[0]
        assert status_item["spent"] == Decimal("700.00")
        assert status_item["remaining"] == Decimal("300.00")
        assert status_item["percentage_used"] == 70.0

    def test_budget_alert_triggered(self, auth_client, project_with_owner, project_owner):
        """Test budget alert is triggered at threshold."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        start = timezone.now().date()
        end = start + timedelta(days=30)

        budget = BudgetFactory(
            project=project_with_owner,
            amount=Decimal("1000.00"),
            start_date=start,
            end_date=end,
            alert_threshold=80,
            alert_enabled=True,
        )

        # Create transactions to reach 85% of budget
        TransactionFactory(
            project=project_with_owner,
            amount=Decimal("850.00"),
            date=start,
            created_by=project_owner,
        )

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        status_item = response.data[0]
        assert status_item["alert_triggered"] is True

    def test_budget_alert_disabled(self, auth_client, project_with_owner, project_owner):
        """Test that alert is not triggered when disabled."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        start = timezone.now().date()
        end = start + timedelta(days=30)

        budget = BudgetFactory(
            project=project_with_owner,
            amount=Decimal("1000.00"),
            start_date=start,
            end_date=end,
            alert_threshold=80,
            alert_enabled=False,  # Disabled
        )

        # Create transactions to reach 85% of budget
        TransactionFactory(
            project=project_with_owner,
            amount=Decimal("850.00"),
            date=start,
            created_by=project_owner,
        )

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        status_item = response.data[0]
        assert status_item["alert_triggered"] is False

    def test_budget_status_category_filter(self, auth_client, project_with_owner, project_owner):
        """Test budget status filtered by category."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        category1 = CategoryFactory(project=project_with_owner)
        category2 = CategoryFactory(project=project_with_owner)

        start = timezone.now().date()
        end = start + timedelta(days=30)

        budget1 = BudgetFactory(
            project=project_with_owner,
            category=category1,
            amount=Decimal("500.00"),
            start_date=start,
            end_date=end,
        )

        budget2 = BudgetFactory(
            project=project_with_owner,
            category=category2,
            amount=Decimal("300.00"),
            start_date=start,
            end_date=end,
        )

        # Create transactions for each category
        TransactionFactory(
            project=project_with_owner,
            category=category1,
            amount=Decimal("250.00"),
            date=start,
            created_by=project_owner,
        )

        TransactionFactory(
            project=project_with_owner,
            category=category2,
            amount=Decimal("100.00"),
            date=start,
            created_by=project_owner,
        )

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        # Verify each budget status
        statuses = {s["budget_id"]: s for s in response.data}
        assert statuses[str(budget1.id)]["spent"] == Decimal("250.00")
        assert statuses[str(budget2.id)]["spent"] == Decimal("100.00")

    def test_budget_status_non_member(self, project_with_owner):
        """Test that non-members cannot view budget status."""
        other_user = VerifiedUserFactory()
        client = APIClient()
        client.force_authenticate(user=other_user)

        url = self.get_url(project_with_owner.id)
        response = client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
