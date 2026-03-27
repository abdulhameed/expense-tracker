from decimal import Decimal
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import ProjectMember
from apps.projects.permissions import get_project_and_membership, require_owner_or_admin
from apps.transactions.models import Transaction
from .models import Budget
from .serializers import BudgetSerializer, BudgetStatusSerializer


# ---------------------------------------------------------------------------
# Budgets
# ---------------------------------------------------------------------------


class BudgetListCreateView(generics.ListCreateAPIView):
    """List and create budgets for a project."""

    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering_fields = ["created_at", "amount"]
    search_fields = ["category__name"]

    def get_queryset(self):
        project_id = self.kwargs.get("project_id")
        if not project_id:
            return Budget.objects.none()

        # Verify user is member of project
        try:
            project, membership = get_project_and_membership(project_id, self.request.user)
        except (NotFound, PermissionDenied):
            return Budget.objects.none()

        return Budget.objects.filter(project=project).select_related(
            "project", "category", "created_by"
        )

    def perform_create(self, serializer):
        project_id = self.kwargs.get("project_id")
        project, membership = get_project_and_membership(project_id, self.request.user)
        require_owner_or_admin(membership)

        serializer.save(project=project, created_by=self.request.user)


class BudgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, and delete a budget."""

    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_queryset(self):
        project_id = self.kwargs.get("project_id")
        if not project_id:
            return Budget.objects.none()

        try:
            project, membership = get_project_and_membership(project_id, self.request.user)
        except (NotFound, PermissionDenied):
            return Budget.objects.none()

        return Budget.objects.filter(project=project).select_related(
            "project", "category", "created_by"
        )

    def get_object(self):
        budget = super().get_object()
        project_id = self.kwargs.get("project_id")

        try:
            project, membership = get_project_and_membership(project_id, self.request.user)
        except (NotFound, PermissionDenied) as e:
            raise e

        # Check write permissions for update/delete
        if self.request.method in ("PATCH", "DELETE"):
            require_owner_or_admin(membership)

        return budget


class BudgetStatusView(APIView):
    """Get detailed status of all budgets for a project."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, project_id):
        """
        Get budget status including spent amount and alert status.
        Query parameters:
            - date: Filter transactions by specific date (YYYY-MM-DD), defaults to today
        """
        try:
            project, membership = get_project_and_membership(project_id, request.user)
        except (NotFound, PermissionDenied) as e:
            raise e

        # Get budgets for this project
        budgets = Budget.objects.filter(project=project).select_related(
            "category", "created_by"
        )

        status_data = []

        for budget in budgets:
            # Calculate spent amount for this budget's period
            spent = self._calculate_spent(budget)

            # Calculate remaining
            remaining = budget.amount - spent

            # Calculate percentage used
            if budget.amount > 0:
                percentage_used = (spent / budget.amount) * 100
            else:
                percentage_used = 0.0

            # Check if alert should be triggered
            alert_triggered = (
                budget.alert_enabled
                and percentage_used >= budget.alert_threshold
            )

            # Category name (None if budget is project-wide)
            category_name = budget.category.name if budget.category else None

            status_item = {
                "budget_id": budget.id,
                "allocated": budget.amount,
                "spent": spent,
                "remaining": remaining,
                "percentage_used": float(percentage_used),
                "alert_triggered": alert_triggered,
                "period": budget.period,
                "category_name": category_name,
            }
            status_data.append(status_item)

        serializer = BudgetStatusSerializer(status_data, many=True)
        return Response(serializer.data)

    def _calculate_spent(self, budget):
        """Calculate the amount spent within a budget's period."""
        filter_kwargs = {
            "project": budget.project,
            "transaction_type": "expense",
            "date__gte": budget.start_date,
            "date__lte": budget.end_date,
        }

        # If budget has a category, filter by category
        if budget.category:
            filter_kwargs["category"] = budget.category

        transactions = Transaction.objects.filter(**filter_kwargs)
        spent = sum(t.amount for t in transactions) or Decimal("0.00")
        return spent


class BudgetSummaryView(APIView):
    """Get summary of all budgets for a project."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, project_id):
        """
        Get summary statistics for budgets in a project.
        Returns:
            - total_allocated: Sum of all budget amounts
            - total_spent: Sum of all spent amounts
            - total_remaining: Sum of all remaining amounts
            - budget_count: Number of budgets in the project
            - alerts_triggered: Number of budgets with triggered alerts
        """
        try:
            project, membership = get_project_and_membership(project_id, request.user)
        except (NotFound, PermissionDenied) as e:
            raise e

        budgets = Budget.objects.filter(project=project).select_related("category")

        total_allocated = Decimal("0.00")
        total_spent = Decimal("0.00")
        alerts_triggered = 0

        for budget in budgets:
            total_allocated += budget.amount
            spent = self._calculate_spent(budget)
            total_spent += spent

            if budget.alert_enabled:
                percentage_used = (spent / budget.amount * 100) if budget.amount > 0 else 0
                if percentage_used >= budget.alert_threshold:
                    alerts_triggered += 1

        total_remaining = total_allocated - total_spent

        return Response({
            "project_id": str(project.id),
            "total_allocated": total_allocated,
            "total_spent": total_spent,
            "total_remaining": total_remaining,
            "budget_count": budgets.count(),
            "alerts_triggered": alerts_triggered,
        })

    def _calculate_spent(self, budget):
        """Calculate the amount spent within a budget's period."""
        filter_kwargs = {
            "project": budget.project,
            "transaction_type": "expense",
            "date__gte": budget.start_date,
            "date__lte": budget.end_date,
        }

        if budget.category:
            filter_kwargs["category"] = budget.category

        transactions = Transaction.objects.filter(**filter_kwargs)
        spent = sum(t.amount for t in transactions) or Decimal("0.00")
        return spent
