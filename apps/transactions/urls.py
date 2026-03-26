from django.urls import path

from .views import (
    CategoryDetailView,
    CategoryListCreateView,
    DefaultCategoryListView,
    TransactionBulkCreateView,
    TransactionDetailView,
    TransactionExportView,
    TransactionListCreateView,
)

urlpatterns = [
    # Categories
    path(
        "projects/<uuid:project_id>/categories/",
        CategoryListCreateView.as_view(),
        name="category-list-create",
    ),
    path(
        "projects/<uuid:project_id>/categories/<uuid:pk>/",
        CategoryDetailView.as_view(),
        name="category-detail",
    ),
    path(
        "categories/defaults/",
        DefaultCategoryListView.as_view(),
        name="category-defaults",
    ),
    # Transactions
    path(
        "projects/<uuid:project_id>/transactions/",
        TransactionListCreateView.as_view(),
        name="transaction-list-create",
    ),
    path(
        "projects/<uuid:project_id>/transactions/bulk/",
        TransactionBulkCreateView.as_view(),
        name="transaction-bulk-create",
    ),
    path(
        "projects/<uuid:project_id>/transactions/export/",
        TransactionExportView.as_view(),
        name="transaction-export",
    ),
    path(
        "projects/<uuid:project_id>/transactions/<uuid:pk>/",
        TransactionDetailView.as_view(),
        name="transaction-detail",
    ),
]
