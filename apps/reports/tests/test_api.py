from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.tests.factories import UserFactory, VerifiedUserFactory
from apps.projects.models import ProjectMember
from apps.projects.tests.factories import ProjectFactory, ProjectMemberFactory
from apps.transactions.tests.factories import CategoryFactory, TransactionFactory
from apps.budgets.tests.factories import BudgetFactory


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
class TestSummaryReportView:
    """Test summary report endpoint."""

    def get_url(self, project_id):
        return reverse("report-summary", kwargs={"project_id": project_id})

    def test_summary_no_transactions(self, auth_client, project_with_owner, project_owner):
        """Test summary with no transactions."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["summary"]["total_income"] == "0.00"
        assert response.data["summary"]["total_expenses"] == "0.00"
        assert response.data["summary"]["net"] == "0.00"

    def test_summary_with_transactions(self, auth_client, project_with_owner, project_owner):
        """Test summary with transactions."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        start = timezone.now().date() - timedelta(days=15)

        TransactionFactory(
            project=project_with_owner,
            amount=Decimal("500.00"),
            transaction_type="income",
            date=start,
            created_by=project_owner,
        )
        TransactionFactory(
            project=project_with_owner,
            amount=Decimal("200.00"),
            transaction_type="expense",
            date=start,
            created_by=project_owner,
        )

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["summary"]["total_income"] == "500.00"
        assert response.data["summary"]["total_expenses"] == "200.00"
        assert response.data["summary"]["net"] == "300.00"

    def test_summary_with_date_range(self, auth_client, project_with_owner, project_owner):
        """Test summary with custom date range."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        TransactionFactory(
            project=project_with_owner,
            amount=Decimal("100.00"),
            transaction_type="expense",
            date=date(2026, 1, 15),
            created_by=project_owner,
        )
        TransactionFactory(
            project=project_with_owner,
            amount=Decimal("200.00"),
            transaction_type="expense",
            date=date(2026, 2, 15),
            created_by=project_owner,
        )

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(
            url + "?start_date=2026-01-01&end_date=2026-01-31"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["summary"]["total_expenses"] == "100.00"

    def test_summary_non_member(self, project_with_owner):
        """Test that non-members cannot access summary."""
        other_user = VerifiedUserFactory()
        client = APIClient()
        client.force_authenticate(user=other_user)

        url = self.get_url(project_with_owner.id)
        response = client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_summary_unauthenticated(self, client, project_with_owner):
        """Test that unauthenticated users cannot access summary."""
        url = self.get_url(project_with_owner.id)
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_summary_invalid_date_format(self, auth_client, project_with_owner, project_owner):
        """Test that invalid date format returns error."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url + "?start_date=invalid")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCategoryBreakdownView:
    """Test category breakdown endpoint."""

    def get_url(self, project_id):
        return reverse("report-category-breakdown", kwargs={"project_id": project_id})

    def test_breakdown_no_transactions(self, auth_client, project_with_owner, project_owner):
        """Test breakdown with no transactions."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["by_category"] == []

    def test_breakdown_with_categories(self, auth_client, project_with_owner, project_owner):
        """Test breakdown with multiple categories."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        cat1 = CategoryFactory(project=project_with_owner, name="Food")
        cat2 = CategoryFactory(project=project_with_owner, name="Transport")

        start = timezone.now().date() - timedelta(days=15)

        TransactionFactory(
            project=project_with_owner,
            category=cat1,
            amount=Decimal("300.00"),
            transaction_type="expense",
            date=start,
            created_by=project_owner,
        )
        TransactionFactory(
            project=project_with_owner,
            category=cat2,
            amount=Decimal("200.00"),
            transaction_type="expense",
            date=start,
            created_by=project_owner,
        )

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["by_category"]) == 2
        assert response.data["by_category"][0]["percentage"] == 60.0


@pytest.mark.django_db
class TestTrendsReportView:
    """Test trends report endpoint."""

    def get_url(self, project_id):
        return reverse("report-trends", kwargs={"project_id": project_id})

    def test_trends_multiple_days(self, auth_client, project_with_owner, project_owner):
        """Test trends across multiple days."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        start = timezone.now().date()

        TransactionFactory(
            project=project_with_owner,
            amount=Decimal("100.00"),
            transaction_type="expense",
            date=start,
            created_by=project_owner,
        )
        TransactionFactory(
            project=project_with_owner,
            amount=Decimal("200.00"),
            transaction_type="expense",
            date=start + timedelta(days=1),
            created_by=project_owner,
        )

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(
            url + f"?start_date={start}&end_date={start + timedelta(days=1)}"
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["trends"]) == 2
        assert response.data["trends"][0]["expenses"] == "100.00"
        assert response.data["trends"][1]["expenses"] == "200.00"

    def test_trends_invalid_granularity(self, auth_client, project_with_owner, project_owner):
        """Test that invalid granularity returns error."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url + "?granularity=invalid")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestMonthlyReportView:
    """Test monthly report endpoint."""

    def get_url(self, project_id):
        return reverse("report-monthly", kwargs={"project_id": project_id})

    def test_monthly_report_current_month(self, auth_client, project_with_owner, project_owner):
        """Test monthly report for current month."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        today = timezone.now().date()
        TransactionFactory(
            project=project_with_owner,
            amount=Decimal("100.00"),
            transaction_type="expense",
            date=today,
            created_by=project_owner,
        )

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["year"] == today.year
        assert response.data["month"] == today.month
        assert response.data["summary"]["total_expenses"] == "100.00"

    def test_monthly_report_specific_month(self, auth_client, project_with_owner, project_owner):
        """Test monthly report for specific month."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        TransactionFactory(
            project=project_with_owner,
            amount=Decimal("150.00"),
            transaction_type="expense",
            date=date(2026, 1, 15),
            created_by=project_owner,
        )

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url + "?year=2026&month=1")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["year"] == 2026
        assert response.data["month"] == 1
        assert response.data["summary"]["total_expenses"] == "150.00"

    def test_monthly_report_invalid_month(self, auth_client, project_with_owner, project_owner):
        """Test that invalid month returns error."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url + "?month=13")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestComparisonReportView:
    """Test period comparison endpoint."""

    def get_url(self, project_id):
        return reverse("report-comparison", kwargs={"project_id": project_id})

    def test_comparison_two_periods(self, auth_client, project_with_owner, project_owner):
        """Test comparison of two arbitrary periods."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        # Period 1
        TransactionFactory(
            project=project_with_owner,
            amount=Decimal("100.00"),
            transaction_type="expense",
            date=date(2026, 1, 15),
            created_by=project_owner,
        )

        # Period 2
        TransactionFactory(
            project=project_with_owner,
            amount=Decimal("200.00"),
            transaction_type="expense",
            date=date(2026, 2, 15),
            created_by=project_owner,
        )

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(
            url
            + "?start_date1=2026-01-01&end_date1=2026-01-31"
            + "&start_date2=2026-02-01&end_date2=2026-02-28"
        )

        assert response.status_code == status.HTTP_200_OK
        assert "period_1" in response.data
        assert "period_2" in response.data
        assert response.data["period_1"]["summary"]["total_expenses"] == "100.00"
        assert response.data["period_2"]["summary"]["total_expenses"] == "200.00"

    def test_comparison_missing_dates(self, auth_client, project_with_owner, project_owner):
        """Test that missing date parameters returns error."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_comparison_invalid_date_range(self, auth_client, project_with_owner, project_owner):
        """Test that invalid date range returns error."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(
            url
            + "?start_date1=2026-01-31&end_date1=2026-01-01"
            + "&start_date2=2026-02-01&end_date2=2026-02-28"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPeriodComparisonView:
    """Test current vs previous period comparison."""

    def get_url(self, project_id):
        return reverse("report-period-comparison", kwargs={"project_id": project_id})

    def test_period_comparison_default(self, auth_client, project_with_owner, project_owner):
        """Test period comparison with default 30 days."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "current_period" in response.data
        assert "previous_period" in response.data
        assert "changes" in response.data

    def test_period_comparison_custom_days(self, auth_client, project_with_owner, project_owner):
        """Test period comparison with custom number of days."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url + "?days=60")

        assert response.status_code == status.HTTP_200_OK

    def test_period_comparison_invalid_days(self, auth_client, project_with_owner, project_owner):
        """Test that invalid number of days returns error."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        url = self.get_url(project_with_owner.id)
        response = auth_client.get(url + "?days=400")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestReportCaching:
    """Test that report responses are cached."""

    def test_summary_cached(self, auth_client, project_with_owner, project_owner):
        """Test that summary report is cached."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        url = reverse("report-summary", kwargs={"project_id": project_with_owner.id})

        # First request
        response1 = auth_client.get(url)
        assert response1.status_code == status.HTTP_200_OK

        # Second request (should be cached)
        response2 = auth_client.get(url)
        assert response2.status_code == status.HTTP_200_OK
        assert response1.data == response2.data

    def test_monthly_report_cached(self, auth_client, project_with_owner, project_owner):
        """Test that monthly report is cached."""
        project_with_owner.owner = project_owner
        project_with_owner.save()

        url = reverse("report-monthly", kwargs={"project_id": project_with_owner.id})

        # First request
        response1 = auth_client.get(url)
        assert response1.status_code == status.HTTP_200_OK

        # Second request (should be cached)
        response2 = auth_client.get(url)
        assert response2.status_code == status.HTTP_200_OK
        assert response1.data == response2.data
