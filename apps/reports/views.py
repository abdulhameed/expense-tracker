from datetime import datetime
from django.core.cache import cache
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import ProjectMember
from apps.projects.permissions import get_project_and_membership
from .serializers import (
    ReportSummarySerializer,
    TrendsReportSerializer,
    MonthlyReportSerializer,
    ComparisonReportSerializer,
)
from .utils import ReportCalculator


class ReportBaseView(APIView):
    """Base class for all report views."""

    permission_classes = [permissions.IsAuthenticated]

    def _get_cache_key(self, project_id, view_name, params):
        """Generate a cache key for report caching."""
        param_str = "_".join(f"{k}={v}" for k, v in sorted(params.items()))
        return f"report:{project_id}:{view_name}:{param_str}"

    def _parse_date(self, date_str):
        """Parse date string in YYYY-MM-DD format."""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid date format: {date_str}. Use YYYY-MM-DD")


class SummaryReportView(ReportBaseView):
    """Get financial summary for a project."""

    def get(self, request, project_id):
        """
        Get summary report for a date range.

        Query parameters:
            - start_date: Start date (YYYY-MM-DD), defaults to 30 days ago
            - end_date: End date (YYYY-MM-DD), defaults to today
        """
        try:
            project, membership = get_project_and_membership(project_id, request.user)
        except (NotFound, PermissionDenied) as e:
            raise e

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date:
            start_date = self._parse_date(start_date)
        if end_date:
            end_date = self._parse_date(end_date)

        # Check cache
        cache_params = {
            "start_date": str(start_date) if start_date else "",
            "end_date": str(end_date) if end_date else "",
        }
        cache_key = self._get_cache_key(project_id, "summary", cache_params)
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        # Calculate summary
        summary = ReportCalculator.get_summary(project, start_date, end_date)

        # Cache for 1 hour
        cache.set(cache_key, summary, 3600)

        serializer = ReportSummarySerializer(summary)
        return Response(serializer.data)


class CategoryBreakdownView(ReportBaseView):
    """Get spending breakdown by category."""

    def get(self, request, project_id):
        """
        Get category breakdown report.

        Query parameters:
            - start_date: Start date (YYYY-MM-DD)
            - end_date: End date (YYYY-MM-DD)
        """
        try:
            project, membership = get_project_and_membership(project_id, request.user)
        except (NotFound, PermissionDenied) as e:
            raise e

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if start_date:
            start_date = self._parse_date(start_date)
        if end_date:
            end_date = self._parse_date(end_date)

        breakdown = ReportCalculator.get_category_breakdown(
            project, start_date, end_date
        )

        return Response({"by_category": breakdown})


class TrendsReportView(ReportBaseView):
    """Get spending trends over time."""

    def get(self, request, project_id):
        """
        Get trends report for a date range.

        Query parameters:
            - start_date: Start date (YYYY-MM-DD)
            - end_date: End date (YYYY-MM-DD)
            - granularity: 'day' (default), 'week', or 'month'
        """
        try:
            project, membership = get_project_and_membership(project_id, request.user)
        except (NotFound, PermissionDenied) as e:
            raise e

        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        granularity = request.query_params.get("granularity", "day")

        if start_date:
            start_date = self._parse_date(start_date)
        if end_date:
            end_date = self._parse_date(end_date)

        if granularity not in ["day", "week", "month"]:
            raise ValidationError("Granularity must be 'day', 'week', or 'month'")

        trends = ReportCalculator.get_trends(
            project, start_date, end_date, granularity
        )

        return Response({"trends": trends})


class MonthlyReportView(ReportBaseView):
    """Get detailed report for a specific month."""

    def get(self, request, project_id):
        """
        Get detailed monthly report.

        Query parameters:
            - year: Year (defaults to current year)
            - month: Month 1-12 (defaults to current month)
        """
        try:
            project, membership = get_project_and_membership(project_id, request.user)
        except (NotFound, PermissionDenied) as e:
            raise e

        year = request.query_params.get("year", type=int)
        month = request.query_params.get("month", type=int)

        if year is None:
            year = timezone.now().year
        if month is None:
            month = timezone.now().month

        # Validate month
        if not (1 <= month <= 12):
            raise ValidationError("Month must be between 1 and 12")

        if year < 2000 or year > 2100:
            raise ValidationError("Year must be between 2000 and 2100")

        # Check cache
        cache_params = {"year": str(year), "month": str(month)}
        cache_key = self._get_cache_key(project_id, "monthly", cache_params)
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        # Calculate report
        report = ReportCalculator.get_monthly_report(project, year, month)

        # Cache for 1 hour
        cache.set(cache_key, report, 3600)

        serializer = MonthlyReportSerializer(report)
        return Response(serializer.data)


class ComparisonReportView(ReportBaseView):
    """Compare two date ranges."""

    def get(self, request, project_id):
        """
        Get comparison report for two date ranges.

        Query parameters:
            - start_date1: Start of first period (YYYY-MM-DD)
            - end_date1: End of first period (YYYY-MM-DD)
            - start_date2: Start of second period (YYYY-MM-DD)
            - end_date2: End of second period (YYYY-MM-DD)
        """
        try:
            project, membership = get_project_and_membership(project_id, request.user)
        except (NotFound, PermissionDenied) as e:
            raise e

        # Get and validate dates
        start_date1 = request.query_params.get("start_date1")
        end_date1 = request.query_params.get("end_date1")
        start_date2 = request.query_params.get("start_date2")
        end_date2 = request.query_params.get("end_date2")

        if not all([start_date1, end_date1, start_date2, end_date2]):
            raise ValidationError(
                "All date parameters are required: start_date1, end_date1, start_date2, end_date2"
            )

        start_date1 = self._parse_date(start_date1)
        end_date1 = self._parse_date(end_date1)
        start_date2 = self._parse_date(start_date2)
        end_date2 = self._parse_date(end_date2)

        # Validate date ranges
        if start_date1 > end_date1:
            raise ValidationError("start_date1 must be before end_date1")
        if start_date2 > end_date2:
            raise ValidationError("start_date2 must be before end_date2")

        # Calculate report
        report = ReportCalculator.get_comparison_report(
            project, start_date1, end_date1, start_date2, end_date2
        )

        return Response(report)


class PeriodComparisonView(ReportBaseView):
    """Compare current period with previous period."""

    def get(self, request, project_id):
        """
        Compare current period with previous period.

        Query parameters:
            - days: Number of days for comparison period (defaults to 30)
        """
        try:
            project, membership = get_project_and_membership(project_id, request.user)
        except (NotFound, PermissionDenied) as e:
            raise e

        days = request.query_params.get("days", 30, int)

        if days < 1 or days > 365:
            raise ValidationError("Days must be between 1 and 365")

        comparison = ReportCalculator.get_period_comparison(project, days)

        return Response(comparison)


# Cache invalidation helpers

def invalidate_report_cache(project_id):
    """Invalidate all report caches for a project."""
    from django.core.cache import cache

    # Get all keys and delete those matching the project
    # Note: With Redis, we can use pattern matching
    # For now, we'll clear the entire cache on transaction changes
    # In production, consider using django-cacheops or similar
    pass
