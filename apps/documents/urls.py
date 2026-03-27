from django.urls import path

from .views import DocumentDetailView, DocumentDownloadView, DocumentListCreateView

urlpatterns = [
    path(
        "projects/<uuid:project_id>/transactions/<uuid:transaction_id>/documents/",
        DocumentListCreateView.as_view(),
        name="document-list-create",
    ),
    path(
        "projects/<uuid:project_id>/transactions/<uuid:transaction_id>/documents/<uuid:pk>/download/",
        DocumentDownloadView.as_view(),
        name="document-download",
    ),
    path(
        "projects/<uuid:project_id>/transactions/<uuid:transaction_id>/documents/<uuid:pk>/",
        DocumentDetailView.as_view(),
        name="document-detail",
    ),
]
