from django.urls import path

from .views import (
    SummaryReportView,
    CategoryBreakdownView,
    TrendsReportView,
    MonthlyReportView,
    ComparisonReportView,
    PeriodComparisonView,
)

urlpatterns = [
    # Reports
    path("projects/<uuid:project_id>/reports/summary/", SummaryReportView.as_view(), name="report-summary"),
    path("projects/<uuid:project_id>/reports/category-breakdown/", CategoryBreakdownView.as_view(), name="report-category-breakdown"),
    path("projects/<uuid:project_id>/reports/trends/", TrendsReportView.as_view(), name="report-trends"),
    path("projects/<uuid:project_id>/reports/monthly/", MonthlyReportView.as_view(), name="report-monthly"),
    path("projects/<uuid:project_id>/reports/comparison/", ComparisonReportView.as_view(), name="report-comparison"),
    path("projects/<uuid:project_id>/reports/period-comparison/", PeriodComparisonView.as_view(), name="report-period-comparison"),
]
