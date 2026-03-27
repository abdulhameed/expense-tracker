import os

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.projects.permissions import get_project_and_membership
from apps.transactions.models import Transaction

from .models import Document
from .serializers import DocumentSerializer


def _get_transaction_and_membership(project_id, transaction_id, user):
    """Validate project membership and return (transaction, membership)."""
    project, membership = get_project_and_membership(project_id, user)
    transaction = get_object_or_404(
        Transaction, pk=transaction_id, project=project
    )
    return transaction, membership


class DocumentListCreateView(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def _get_context(self):
        return _get_transaction_and_membership(
            self.kwargs["project_id"],
            self.kwargs["transaction_id"],
            self.request.user,
        )

    def get_queryset(self):
        transaction, _ = self._get_context()
        return Document.objects.filter(transaction=transaction)

    def perform_create(self, serializer):
        transaction, membership = self._get_context()
        if not membership.can_create_transactions:
            raise PermissionDenied(
                "You do not have permission to upload documents."
            )
        serializer.save(
            transaction=transaction, uploaded_by=self.request.user
        )


class DocumentDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def _get_context(self):
        return _get_transaction_and_membership(
            self.kwargs["project_id"],
            self.kwargs["transaction_id"],
            self.request.user,
        )

    def get_object(self):
        transaction, _ = self._get_context()
        return get_object_or_404(
            Document, pk=self.kwargs["pk"], transaction=transaction
        )

    def perform_destroy(self, instance):
        _, membership = self._get_context()
        if not membership.can_delete_transactions:
            raise PermissionDenied(
                "You do not have permission to delete documents."
            )
        # Remove file from filesystem
        storage, path = instance.file.storage, instance.file.name
        instance.delete()
        storage.delete(path)


class DocumentDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id, transaction_id, pk):
        transaction, _ = _get_transaction_and_membership(
            project_id, transaction_id, request.user
        )
        document = get_object_or_404(Document, pk=pk, transaction=transaction)

        file_handle = document.file.open("rb")
        response = FileResponse(
            file_handle,
            content_type=document.file_type,
            as_attachment=True,
            filename=document.file_name,
        )
        return response
