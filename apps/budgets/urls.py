from django.urls import path

from .views import (
    BudgetListCreateView,
    BudgetDetailView,
    BudgetStatusView,
    BudgetSummaryView,
)

urlpatterns = [
    # Budgets
    path("projects/<uuid:project_id>/budgets/", BudgetListCreateView.as_view(), name="budget-list"),
    path("projects/<uuid:project_id>/budgets/<uuid:pk>/", BudgetDetailView.as_view(), name="budget-detail"),
    path("projects/<uuid:project_id>/budgets/status/", BudgetStatusView.as_view(), name="budget-status"),
    path("projects/<uuid:project_id>/budgets/summary/", BudgetSummaryView.as_view(), name="budget-summary"),
]
