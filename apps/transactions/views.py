import csv
import io

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.models import Project, ProjectMember
from apps.projects.permissions import get_project_and_membership, require_owner_or_admin

from .filters import TransactionFilter
from .models import Category, Transaction
from .serializers import CategorySerializer, TransactionSerializer


def _get_project_member(project_id, user):
    """Return (project, membership) or raise appropriate DRF exception."""
    return get_project_and_membership(project_id, user)


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------


class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs["project_id"]
        project, _ = _get_project_member(project_id, self.request.user)
        # Return project-specific categories plus defaults
        from django.db.models import Q

        return Category.objects.filter(
            Q(project=project) | Q(is_default=True)
        ).order_by("name")

    def perform_create(self, serializer):
        project_id = self.kwargs["project_id"]
        project, membership = _get_project_member(project_id, self.request.user)
        require_owner_or_admin(membership)
        serializer.save(project=project, is_default=False)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_object(self):
        project_id = self.kwargs["project_id"]
        project, membership = _get_project_member(project_id, self.request.user)
        category = get_object_or_404(Category, pk=self.kwargs["pk"], project=project)
        return category

    def perform_update(self, serializer):
        project_id = self.kwargs["project_id"]
        _, membership = _get_project_member(project_id, self.request.user)
        require_owner_or_admin(membership)
        serializer.save()

    def perform_destroy(self, instance):
        project_id = self.kwargs["project_id"]
        _, membership = _get_project_member(project_id, self.request.user)
        require_owner_or_admin(membership)
        instance.delete()


class DefaultCategoryListView(generics.ListAPIView):
    """Returns the global default categories (project=None, is_default=True)."""

    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.filter(is_default=True)


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------


class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TransactionFilter
    search_fields = ["description", "notes", "reference_number"]
    ordering_fields = ["date", "amount", "created_at"]
    ordering = ["-date"]

    def get_queryset(self):
        project_id = self.kwargs["project_id"]
        project, _ = _get_project_member(project_id, self.request.user)
        return Transaction.objects.filter(project=project).select_related(
            "category", "created_by"
        )

    def perform_create(self, serializer):
        project_id = self.kwargs["project_id"]
        project, membership = _get_project_member(project_id, self.request.user)
        if not membership.can_create_transactions:
            raise PermissionDenied("You do not have permission to create transactions.")
        serializer.save(project=project, created_by=self.request.user)


class TransactionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_object(self):
        project_id = self.kwargs["project_id"]
        project, _ = _get_project_member(project_id, self.request.user)
        return get_object_or_404(Transaction, pk=self.kwargs["pk"], project=project)

    def _get_membership(self):
        project_id = self.kwargs["project_id"]
        _, membership = _get_project_member(project_id, self.request.user)
        return membership

    def perform_update(self, serializer):
        membership = self._get_membership()
        if not membership.can_edit_transactions:
            raise PermissionDenied("You do not have permission to edit transactions.")
        serializer.save()

    def perform_destroy(self, instance):
        membership = self._get_membership()
        if not membership.can_delete_transactions:
            raise PermissionDenied("You do not have permission to delete transactions.")
        instance.delete()


class TransactionBulkCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        project, membership = _get_project_member(project_id, request.user)
        if not membership.can_create_transactions:
            raise PermissionDenied("You do not have permission to create transactions.")

        items = request.data if isinstance(request.data, list) else []
        if not items:
            return Response(
                {"detail": "Provide a non-empty list of transactions."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(items) > 100:
            return Response(
                {"detail": "Cannot bulk create more than 100 transactions at once."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializers_list = [
            TransactionSerializer(data=item, context={"request": request}) for item in items
        ]
        errors = []
        for i, s in enumerate(serializers_list):
            if not s.is_valid():
                errors.append({"index": i, "errors": s.errors})
        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        transactions = Transaction.objects.bulk_create(
            [
                Transaction(project=project, created_by=request.user, **s.validated_data)
                for s in serializers_list
            ]
        )
        return Response(
            TransactionSerializer(transactions, many=True).data,
            status=status.HTTP_201_CREATED,
        )


class TransactionExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        project, _ = _get_project_member(project_id, request.user)
        fmt = request.query_params.get("format", "csv").lower()

        qs = Transaction.objects.filter(project=project).select_related(
            "category", "created_by"
        )

        if fmt == "xlsx":
            return self._export_xlsx(qs, project)
        return self._export_csv(qs, project)

    def _export_csv(self, qs, project):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="{project.name}_transactions.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(
            [
                "Date",
                "Type",
                "Amount",
                "Currency",
                "Category",
                "Description",
                "Payment Method",
                "Reference",
                "Tags",
            ]
        )
        for t in qs:
            writer.writerow(
                [
                    t.date,
                    t.transaction_type,
                    t.amount,
                    t.currency,
                    t.category.name if t.category else "",
                    t.description,
                    t.payment_method,
                    t.reference_number,
                    ",".join(t.tags) if t.tags else "",
                ]
            )
        return response

    def _export_xlsx(self, qs, project):
        import openpyxl

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Transactions"
        headers = [
            "Date",
            "Type",
            "Amount",
            "Currency",
            "Category",
            "Description",
            "Payment Method",
            "Reference",
            "Tags",
        ]
        ws.append(headers)
        for t in qs:
            ws.append(
                [
                    str(t.date),
                    t.transaction_type,
                    float(t.amount),
                    t.currency,
                    t.category.name if t.category else "",
                    t.description,
                    t.payment_method,
                    t.reference_number,
                    ",".join(t.tags) if t.tags else "",
                ]
            )
        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)
        response = HttpResponse(
            buf.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{project.name}_transactions.xlsx"'
        )
        return response


