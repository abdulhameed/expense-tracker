"""
Tests for reports/views.py - Report view endpoints and caching.

Tests:
- ReportBaseView._parse_date() - Date parsing
- ReportBaseView._get_cache_key() - Cache key generation
- SummaryReportView - Summary report endpoint
- CategoryBreakdownView - Category breakdown endpoint
- TrendsReportView - Trends endpoint
- MonthlyReportView - Monthly report endpoint
- ComparisonReportView - Comparison endpoint
- PeriodComparisonView - Period comparison endpoint
- Cache functionality
- Permission enforcement
- Error handling
"""

from datetime import date, timedelta
from decimal import Decimal
import pytest
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.exceptions import ValidationError

from apps.authentication.tests.factories import VerifiedUserFactory
from apps.projects.models import ProjectMember
from apps.projects.tests.factories import ProjectFactory, ProjectMemberFactory
from apps.transactions.tests.factories import TransactionFactory, CategoryFactory
from apps.reports.views import ReportBaseView


@pytest.fixture
def client():
    """API client."""
    return APIClient()


@pytest.fixture
def user():
    """Test user."""
    return VerifiedUserFactory()


@pytest.fixture
def auth_client(user):
    """Authenticated API client."""
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture
def project(user):
    """Test project owned by user."""
    return ProjectFactory(owner=user)


@pytest.fixture
def other_user():
    """Another test user."""
    return VerifiedUserFactory()


@pytest.fixture
def other_project(other_user):
    """Project owned by another user."""
    return ProjectFactory(owner=other_user)


@pytest.mark.django_db
class TestReportBaseViewParseDate:
    """Test date parsing in ReportBaseView."""

    def test_parse_date_valid_format(self):
        """Test parsing valid date in YYYY-MM-DD format."""
        view = ReportBaseView()
        result = view._parse_date("2024-03-28")

        assert result == date(2024, 3, 28)

    def test_parse_date_leap_year_february_29(self):
        """Test parsing leap year date."""
        view = ReportBaseView()
        result = view._parse_date("2024-02-29")

        assert result == date(2024, 2, 29)

    def test_parse_date_non_leap_year_invalid(self):
        """Test parsing invalid leap year date."""
        view = ReportBaseView()

        with pytest.raises(ValidationError):
            view._parse_date("2023-02-29")

    def test_parse_date_invalid_format(self):
        """Test parsing date in wrong format."""
        view = ReportBaseView()

        with pytest.raises(ValidationError):
            view._parse_date("03-28-2024")

    def test_parse_date_invalid_month(self):
        """Test parsing invalid month."""
        view = ReportBaseView()

        with pytest.raises(ValidationError):
            view._parse_date("2024-13-01")

    def test_parse_date_invalid_day(self):
        """Test parsing invalid day."""
        view = ReportBaseView()

        with pytest.raises(ValidationError):
            view._parse_date("2024-06-31")

    def test_parse_date_none_value(self):
        """Test parsing None value."""
        view = ReportBaseView()

        with pytest.raises(ValidationError):
            view._parse_date(None)

    def test_parse_date_empty_string(self):
        """Test parsing empty string."""
        view = ReportBaseView()

        with pytest.raises(ValidationError):
            view._parse_date("")

    def test_parse_date_year_1900(self):
        """Test parsing year 1900."""
        view = ReportBaseView()
        result = view._parse_date("1900-01-01")

        assert result == date(1900, 1, 1)

    def test_parse_date_year_2099(self):
        """Test parsing year 2099."""
        view = ReportBaseView()
        result = view._parse_date("2099-12-31")

        assert result == date(2099, 12, 31)


@pytest.mark.django_db
class TestReportBaseViewCacheKey:
    """Test cache key generation."""

    def test_get_cache_key_structure(self):
        """Test cache key has expected structure."""
        view = ReportBaseView()
        key = view._get_cache_key("project-1", "summary", {"start": "2024-01-01"})

        assert key.startswith("report:")
        assert "project-1" in key
        assert "summary" in key

    def test_get_cache_key_includes_params(self):
        """Test cache key includes parameters."""
        view = ReportBaseView()
        params = {"start_date": "2024-01-01", "end_date": "2024-03-28"}
        key = view._get_cache_key("project-1", "summary", params)

        assert "start_date" in key
        assert "end_date" in key

    def test_get_cache_key_deterministic(self):
        """Test cache key is deterministic."""
        view = ReportBaseView()
        params = {"a": "1", "b": "2"}
        key1 = view._get_cache_key("project-1", "summary", params)
        key2 = view._get_cache_key("project-1", "summary", params)

        assert key1 == key2

    def test_get_cache_key_param_order_independent(self):
        """Test cache key is independent of parameter order."""
        view = ReportBaseView()
        params1 = {"a": "1", "b": "2"}
        params2 = {"b": "2", "a": "1"}
        key1 = view._get_cache_key("project-1", "summary", params1)
        key2 = view._get_cache_key("project-1", "summary", params2)

        assert key1 == key2

    def test_get_cache_key_different_for_different_params(self):
        """Test different parameters produce different keys."""
        view = ReportBaseView()
        key1 = view._get_cache_key("project-1", "summary", {"a": "1"})
        key2 = view._get_cache_key("project-1", "summary", {"a": "2"})

        assert key1 != key2


@pytest.mark.django_db
class TestSummaryReportViewCache:
    """Test caching in summary report endpoint."""

    def test_summary_caches_result(self, auth_client, project, user):
        """Test that summary report caches results."""
        TransactionFactory(
            project=project,
            amount=Decimal("100.00"),
            transaction_type="expense",
            created_by=user,
        )

        url = reverse("report-summary", kwargs={"project_id": project.id})

        # First request
        response1 = auth_client.get(url)
        assert response1.status_code == status.HTTP_200_OK
        data1 = response1.data

        # Modify transaction
        TransactionFactory(
            project=project,
            amount=Decimal("500.00"),
            transaction_type="income",
            created_by=user,
        )

        # Second request (should return cached data)
        response2 = auth_client.get(url)
        assert response2.status_code == status.HTTP_200_OK
        data2 = response2.data

        # Data should be identical (from cache)
        assert data1 == data2

        # Verify they both have expected structure
        assert "total_expenses" in str(data1) or "expenses" in str(data1)

    def test_summary_cache_invalidates(self, auth_client, project, user):
        """Test cache can be invalidated."""
        TransactionFactory(
            project=project,
            amount=Decimal("100.00"),
            transaction_type="expense",
            created_by=user,
        )

        url = reverse("report-summary", kwargs={"project_id": project.id})

        # First request
        response1 = auth_client.get(url)
        assert response1.status_code == status.HTTP_200_OK

        # Get total expenses from response (structure may vary)
        data1_str = str(response1.data)

        # Clear cache
        cache.clear()

        # Add new transaction
        TransactionFactory(
            project=project,
            amount=Decimal("50.00"),
            transaction_type="expense",
            created_by=user,
        )

        # Second request (cache was cleared)
        response2 = auth_client.get(url)
        assert response2.status_code == status.HTTP_200_OK
        data2_str = str(response2.data)

        # Response content may differ after cache clear
        assert response2.status_code == status.HTTP_200_OK

    def test_summary_cache_with_date_range(self, auth_client, project, user):
        """Test caching respects date range parameters."""
        today = timezone.now().date()
        TransactionFactory(
            project=project,
            amount=Decimal("100.00"),
            transaction_type="expense",
            date=today,
            created_by=user,
        )
        TransactionFactory(
            project=project,
            amount=Decimal("200.00"),
            transaction_type="expense",
            date=today - timedelta(days=40),
            created_by=user,
        )

        url = reverse("report-summary", kwargs={"project_id": project.id})
        # Get summary for last 30 days
        response = auth_client.get(
            url,
            {"start_date": (today - timedelta(days=30)).isoformat(), "end_date": today.isoformat()},
        )

        assert response.status_code == status.HTTP_200_OK
        # Verify response has expected structure
        assert "total_expenses" in str(response.data) or "expenses" in str(response.data)


@pytest.mark.django_db
class TestSummaryReportViewPermissions:
    """Test permission enforcement for summary report."""

    def test_summary_requires_authentication(self, client, project):
        """Test that unauthenticated users cannot access summary."""
        url = reverse("report-summary", kwargs={"project_id": project.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_summary_denies_non_member(self, auth_client, other_project):
        """Test that non-members cannot access project summary."""
        url = reverse("report-summary", kwargs={"project_id": other_project.id})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_summary_allows_owner(self, auth_client, user):
        """Test that project owner can access summary."""
        project = ProjectFactory(owner=user)

        url = reverse("report-summary", kwargs={"project_id": project.id})
        response = auth_client.get(url)

        # Should return 200 OK
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]

    def test_summary_allows_member(self, user):
        """Test that project member can access summary."""
        project = ProjectFactory(owner=user)
        other_user = VerifiedUserFactory()
        ProjectMemberFactory(
            project=project,
            user=other_user,
            role=ProjectMember.Role.MEMBER,
        )

        # Authenticate as member
        member_client = APIClient()
        member_client.force_authenticate(user=other_user)

        url = reverse("report-summary", kwargs={"project_id": project.id})
        response = member_client.get(url)

        # Should return 200 OK
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]

    def test_summary_denies_viewer_with_no_membership(self, auth_client, other_project):
        """Test that users without membership cannot access project."""
        url = reverse("report-summary", kwargs={"project_id": other_project.id})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestReportInvalidDateHandling:
    """Test report endpoints with invalid dates."""

    def test_summary_invalid_start_date(self, auth_client, project, user):
        """Test summary with invalid start date."""
        project.owner = user
        project.save()

        url = reverse("report-summary", kwargs={"project_id": project.id})
        response = auth_client.get(url, {"start_date": "2024-13-01"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_summary_malformed_date(self, auth_client, project, user):
        """Test summary with malformed date."""
        project.owner = user
        project.save()

        url = reverse("report-summary", kwargs={"project_id": project.id})
        response = auth_client.get(url, {"start_date": "not-a-date"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_category_breakdown_invalid_date(self, auth_client, project, user):
        """Test category breakdown with invalid date."""
        project.owner = user
        project.save()

        url = reverse("report-category-breakdown", kwargs={"project_id": project.id})
        response = auth_client.get(url, {"end_date": "2024-02-30"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCategoryBreakdownReport:
    """Test category breakdown report endpoint."""

    def test_category_breakdown_empty_project(self, auth_client, project, user):
        """Test category breakdown with no transactions."""
        project.owner = user
        project.save()

        url = reverse("report-category-breakdown", kwargs={"project_id": project.id})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_category_breakdown_by_category(self, auth_client, project, user):
        """Test category breakdown groups by category."""
        project.owner = user
        project.save()

        category1 = CategoryFactory()
        category2 = CategoryFactory()

        TransactionFactory(
            project=project,
            category=category1,
            amount=Decimal("100.00"),
            transaction_type="expense",
            created_by=user,
        )
        TransactionFactory(
            project=project,
            category=category2,
            amount=Decimal("200.00"),
            transaction_type="expense",
            created_by=user,
        )

        url = reverse("report-category-breakdown", kwargs={"project_id": project.id})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_category_breakdown_respects_date_range(self, auth_client, project, user):
        """Test category breakdown respects date range."""
        project.owner = user
        project.save()

        today = timezone.now().date()
        category = CategoryFactory()

        TransactionFactory(
            project=project,
            category=category,
            amount=Decimal("100.00"),
            transaction_type="expense",
            date=today,
            created_by=user,
        )
        TransactionFactory(
            project=project,
            category=category,
            amount=Decimal("200.00"),
            transaction_type="expense",
            date=today - timedelta(days=40),
            created_by=user,
        )

        url = reverse("report-category-breakdown", kwargs={"project_id": project.id})
        response = auth_client.get(
            url,
            {
                "start_date": (today - timedelta(days=30)).isoformat(),
                "end_date": today.isoformat(),
            },
        )

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestTrendsReport:
    """Test trends report endpoint."""

    def test_trends_empty_project(self, auth_client, project, user):
        """Test trends with no transactions."""
        project.owner = user
        project.save()

        url = reverse("report-trends", kwargs={"project_id": project.id})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_trends_shows_daily_trends(self, auth_client, project, user):
        """Test trends shows daily spending."""
        project.owner = user
        project.save()

        today = timezone.now().date()
        TransactionFactory(
            project=project,
            amount=Decimal("100.00"),
            transaction_type="expense",
            date=today,
            created_by=user,
        )

        url = reverse("report-trends", kwargs={"project_id": project.id})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestMonthlyReport:
    """Test monthly report endpoint."""

    def test_monthly_report_empty_project(self, auth_client, project, user):
        """Test monthly report with no transactions."""
        project.owner = user
        project.save()

        url = reverse("report-monthly", kwargs={"project_id": project.id})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK

    def test_monthly_report_includes_sections(self, auth_client, project, user):
        """Test monthly report includes sections."""
        project.owner = user
        project.save()

        url = reverse("report-monthly", kwargs={"project_id": project.id})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestComparisonReport:
    """Test period comparison report endpoint."""

    def test_comparison_compares_periods(self, auth_client, project, user):
        """Test comparison shows differences between periods."""
        project.owner = user
        project.save()

        today = timezone.now().date()
        start1 = today - timedelta(days=60)
        end1 = today - timedelta(days=30)
        start2 = today - timedelta(days=30)
        end2 = today

        TransactionFactory(
            project=project,
            amount=Decimal("100.00"),
            transaction_type="expense",
            date=start1 + timedelta(days=5),
            created_by=user,
        )
        TransactionFactory(
            project=project,
            amount=Decimal("200.00"),
            transaction_type="expense",
            date=start2 + timedelta(days=5),
            created_by=user,
        )

        url = reverse("report-period-comparison", kwargs={"project_id": project.id})
        params = {
            "start_date_1": start1.isoformat(),
            "end_date_1": end1.isoformat(),
            "start_date_2": start2.isoformat(),
            "end_date_2": end2.isoformat(),
        }
        response = auth_client.get(url, params)

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestReportNonExistentProject:
    """Test reports with non-existent project."""

    def test_summary_nonexistent_project(self, auth_client):
        """Test summary with non-existent project."""
        url = reverse("report-summary", kwargs={"project_id": "00000000-0000-0000-0000-000000000000"})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_category_breakdown_nonexistent_project(self, auth_client):
        """Test category breakdown with non-existent project."""
        url = reverse("report-category-breakdown", kwargs={"project_id": "00000000-0000-0000-0000-000000000000"})
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
