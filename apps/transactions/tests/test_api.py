import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.tests.factories import VerifiedUserFactory
from apps.projects.models import ProjectMember
from apps.projects.tests.factories import ProjectFactory, ProjectMemberFactory
from apps.transactions.models import Category, Transaction

from .factories import CategoryFactory, DefaultCategoryFactory, TransactionFactory


@pytest.fixture
def user():
    return VerifiedUserFactory()


@pytest.fixture
def auth_client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture
def project(user):
    return ProjectFactory(owner=user)


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCategoryListCreateView:
    def url(self, project):
        return reverse("category-list-create", kwargs={"project_id": project.pk})

    def test_list_categories_for_member(self, auth_client, project):
        before_count = auth_client.get(self.url(project)).data["count"]
        CategoryFactory(project=project)
        DefaultCategoryFactory()
        response = auth_client.get(self.url(project))
        assert response.status_code == status.HTTP_200_OK
        # 1 project-specific + 1 new default added above + existing defaults
        assert response.data["count"] == before_count + 2

    def test_list_requires_auth(self, project):
        c = APIClient()
        response = c.get(self.url(project))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_non_member_gets_403(self, project):
        other = VerifiedUserFactory()
        c = APIClient()
        c.force_authenticate(user=other)
        response = c.get(self.url(project))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_owner_can_create_category(self, auth_client, project):
        data = {"name": "Groceries", "category_type": "expense", "color": "#FF0000"}
        response = auth_client.post(self.url(project), data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Groceries"
        assert response.data["is_default"] is False

    def test_viewer_cannot_create_category(self, project):
        viewer = VerifiedUserFactory()
        ProjectMemberFactory(project=project, user=viewer, role=ProjectMember.Role.VIEWER)
        c = APIClient()
        c.force_authenticate(user=viewer)
        data = {"name": "Groceries", "category_type": "expense"}
        response = c.post(self.url(project), data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_member_cannot_create_category(self, project):
        member = VerifiedUserFactory()
        ProjectMemberFactory(project=project, user=member, role=ProjectMember.Role.MEMBER)
        c = APIClient()
        c.force_authenticate(user=member)
        data = {"name": "Groceries", "category_type": "expense"}
        response = c.post(self.url(project), data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_requires_name_and_type(self, auth_client, project):
        response = auth_client.post(self.url(project), {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCategoryDetailView:
    def url(self, project, category):
        return reverse(
            "category-detail", kwargs={"project_id": project.pk, "pk": category.pk}
        )

    def test_retrieve_category(self, auth_client, project):
        cat = CategoryFactory(project=project)
        response = auth_client.get(self.url(project, cat))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == cat.name

    def test_update_category(self, auth_client, project):
        cat = CategoryFactory(project=project)
        response = auth_client.patch(self.url(project, cat), {"name": "Updated"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated"

    def test_delete_category(self, auth_client, project):
        cat = CategoryFactory(project=project)
        response = auth_client.delete(self.url(project, cat))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(pk=cat.pk).exists()

    def test_non_member_cannot_access(self, project):
        cat = CategoryFactory(project=project)
        other = VerifiedUserFactory()
        c = APIClient()
        c.force_authenticate(user=other)
        response = c.get(self.url(project, cat))
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestDefaultCategoryListView:
    url = reverse("category-defaults")

    def test_returns_only_defaults(self, auth_client):
        before_count = auth_client.get(self.url).data["count"]
        DefaultCategoryFactory.create_batch(3)
        CategoryFactory()  # project-specific, should NOT appear
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        # Only 3 new defaults added; project-specific category must not appear
        assert response.data["count"] == before_count + 3

    def test_requires_auth(self):
        c = APIClient()
        response = c.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTransactionListCreateView:
    def url(self, project):
        return reverse("transaction-list-create", kwargs={"project_id": project.pk})

    def test_list_transactions(self, auth_client, project):
        TransactionFactory.create_batch(3, project=project, created_by=project.owner)
        TransactionFactory()  # other project
        response = auth_client.get(self.url(project))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

    def test_requires_auth(self, project):
        c = APIClient()
        response = c.get(self.url(project))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_non_member_gets_403(self, project):
        other = VerifiedUserFactory()
        c = APIClient()
        c.force_authenticate(user=other)
        response = c.get(self.url(project))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_transaction(self, auth_client, project, user):
        import datetime

        cat = CategoryFactory(project=project)
        data = {
            "transaction_type": "expense",
            "amount": "50.00",
            "currency": "USD",
            "description": "Lunch",
            "date": str(datetime.date.today()),
            "payment_method": "cash",
            "category": str(cat.pk),
        }
        response = auth_client.post(self.url(project), data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["description"] == "Lunch"
        assert str(response.data["created_by"]) == str(user.pk)
        assert str(response.data["project"]) == str(project.pk)

    def test_member_without_permission_cannot_create(self, project):
        member = VerifiedUserFactory()
        ProjectMemberFactory(
            project=project,
            user=member,
            role=ProjectMember.Role.VIEWER,
            can_create_transactions=False,
        )
        c = APIClient()
        c.force_authenticate(user=member)
        import datetime

        data = {
            "transaction_type": "expense",
            "amount": "10.00",
            "date": str(datetime.date.today()),
        }
        response = c.post(self.url(project), data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_filter_by_type(self, auth_client, project):
        TransactionFactory(
            project=project,
            created_by=project.owner,
            transaction_type=Transaction.TransactionType.INCOME,
        )
        TransactionFactory(
            project=project,
            created_by=project.owner,
            transaction_type=Transaction.TransactionType.EXPENSE,
        )
        response = auth_client.get(self.url(project), {"transaction_type": "income"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_search_by_description(self, auth_client, project):
        TransactionFactory(
            project=project, created_by=project.owner, description="Coffee shop"
        )
        TransactionFactory(
            project=project, created_by=project.owner, description="Grocery store"
        )
        response = auth_client.get(self.url(project), {"search": "Coffee"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_filter_date_range(self, auth_client, project):
        import datetime

        past = datetime.date(2024, 1, 15)
        present = datetime.date.today()
        TransactionFactory(project=project, created_by=project.owner, date=past)
        TransactionFactory(project=project, created_by=project.owner, date=present)
        response = auth_client.get(
            self.url(project),
            {"date_from": "2025-01-01", "date_to": str(present)},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1


@pytest.mark.django_db
class TestTransactionDetailView:
    def url(self, project, txn):
        return reverse(
            "transaction-detail",
            kwargs={"project_id": project.pk, "pk": txn.pk},
        )

    def test_retrieve(self, auth_client, project, user):
        txn = TransactionFactory(project=project, created_by=user)
        response = auth_client.get(self.url(project, txn))
        assert response.status_code == status.HTTP_200_OK
        assert str(response.data["id"]) == str(txn.pk)

    def test_update(self, auth_client, project, user):
        txn = TransactionFactory(project=project, created_by=user)
        response = auth_client.patch(self.url(project, txn), {"description": "Updated"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["description"] == "Updated"

    def test_delete_requires_permission(self, project, user):
        member = VerifiedUserFactory()
        ProjectMemberFactory(
            project=project,
            user=member,
            role=ProjectMember.Role.MEMBER,
            can_delete_transactions=False,
        )
        txn = TransactionFactory(project=project, created_by=user)
        c = APIClient()
        c.force_authenticate(user=member)
        response = c.delete(self.url(project, txn))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_owner_can_delete(self, auth_client, project, user):
        # Owner has can_delete_transactions=True by default via their membership role
        member_obj = ProjectMember.objects.get(project=project, user=user)
        member_obj.can_delete_transactions = True
        member_obj.save()
        txn = TransactionFactory(project=project, created_by=user)
        response = auth_client.delete(self.url(project, txn))
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_non_member_gets_403(self, project, user):
        txn = TransactionFactory(project=project, created_by=user)
        other = VerifiedUserFactory()
        c = APIClient()
        c.force_authenticate(user=other)
        response = c.get(self.url(project, txn))
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestTransactionExportView:
    def url(self, project):
        return reverse("transaction-export", kwargs={"project_id": project.pk})

    def test_export_csv(self, auth_client, project, user):
        TransactionFactory.create_batch(3, project=project, created_by=user)
        response = auth_client.get(self.url(project), {"export_format": "csv"})
        assert response.status_code == status.HTTP_200_OK
        assert "text/csv" in response["Content-Type"]

    def test_export_xlsx(self, auth_client, project, user):
        TransactionFactory.create_batch(2, project=project, created_by=user)
        response = auth_client.get(self.url(project), {"export_format": "xlsx"})
        assert response.status_code == status.HTTP_200_OK
        assert (
            "spreadsheetml" in response["Content-Type"]
            or "openxmlformats" in response["Content-Type"]
        )

    def test_non_member_cannot_export(self, project):
        other = VerifiedUserFactory()
        c = APIClient()
        c.force_authenticate(user=other)
        response = c.get(self.url(project))
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestTransactionBulkCreateView:
    def url(self, project):
        return reverse("transaction-bulk-create", kwargs={"project_id": project.pk})

    def test_bulk_create(self, auth_client, project):
        import datetime

        data = [
            {
                "transaction_type": "expense",
                "amount": "10.00",
                "date": str(datetime.date.today()),
                "payment_method": "cash",
            },
            {
                "transaction_type": "income",
                "amount": "200.00",
                "date": str(datetime.date.today()),
                "payment_method": "card",
            },
        ]
        response = auth_client.post(self.url(project), data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data) == 2
        assert Transaction.objects.filter(project=project).count() == 2

    def test_empty_list_returns_400(self, auth_client, project):
        response = auth_client.post(self.url(project), [], format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_exceeds_limit_returns_400(self, auth_client, project):
        import datetime

        data = [
            {
                "transaction_type": "expense",
                "amount": "1.00",
                "date": str(datetime.date.today()),
            }
        ] * 101
        response = auth_client.post(self.url(project), data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_non_member_gets_403(self, project):
        other = VerifiedUserFactory()
        c = APIClient()
        c.force_authenticate(user=other)
        response = c.post(self.url(project), [], format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN
