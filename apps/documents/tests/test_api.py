import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.tests.factories import VerifiedUserFactory
from apps.documents.models import Document
from apps.projects.models import ProjectMember
from apps.projects.tests.factories import ProjectFactory, ProjectMemberFactory
from apps.transactions.tests.factories import TransactionFactory

from .factories import DocumentFactory


def _pdf(name="receipt.pdf", size=1024):
    return SimpleUploadedFile(name, b"%PDF-1.4 " + b"x" * size, content_type="application/pdf")


def _png(name="image.png", size=1024):
    return SimpleUploadedFile(name, b"\x89PNG" + b"x" * size, content_type="image/png")


@pytest.fixture
def user():
    return VerifiedUserFactory()


@pytest.fixture
def auth_client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture
def project(user):
    return ProjectFactory(owner=user)


@pytest.fixture
def transaction(project):
    return TransactionFactory(project=project, created_by=project.owner)


def list_url(project, transaction):
    return reverse(
        "document-list-create",
        kwargs={"project_id": project.pk, "transaction_id": transaction.pk},
    )


def detail_url(project, transaction, doc):
    return reverse(
        "document-detail",
        kwargs={"project_id": project.pk, "transaction_id": transaction.pk, "pk": doc.pk},
    )


def download_url(project, transaction, doc):
    return reverse(
        "document-download",
        kwargs={"project_id": project.pk, "transaction_id": transaction.pk, "pk": doc.pk},
    )


# ---------------------------------------------------------------------------
# List & Upload
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestDocumentListCreateView:
    def test_list_documents(self, auth_client, project, transaction):
        DocumentFactory.create_batch(3, transaction=transaction, uploaded_by=project.owner)
        response = auth_client.get(list_url(project, transaction))
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

    def test_list_only_shows_transaction_documents(self, auth_client, project, transaction):
        DocumentFactory(transaction=transaction, uploaded_by=project.owner)
        DocumentFactory()  # different transaction
        response = auth_client.get(list_url(project, transaction))
        assert response.data["count"] == 1

    def test_list_requires_auth(self, project, transaction):
        c = APIClient()
        response = c.get(list_url(project, transaction))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_non_member_gets_403(self, project, transaction):
        other = VerifiedUserFactory()
        c = APIClient()
        c.force_authenticate(user=other)
        response = c.get(list_url(project, transaction))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_upload_document(self, auth_client, project, transaction):
        data = {"file": _pdf(), "document_type": "receipt"}
        response = auth_client.post(list_url(project, transaction), data, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["file_name"] == "receipt.pdf"
        assert response.data["file_type"] == "application/pdf"
        assert Document.objects.filter(transaction=transaction).count() == 1

    def test_upload_png(self, auth_client, project, transaction):
        data = {"file": _png(), "document_type": "invoice"}
        response = auth_client.post(list_url(project, transaction), data, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["file_type"] == "image/png"

    def test_upload_sets_uploaded_by(self, auth_client, user, project, transaction):
        data = {"file": _pdf(), "document_type": "receipt"}
        response = auth_client.post(list_url(project, transaction), data, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED
        assert str(response.data["uploaded_by"]) == str(user.pk)

    def test_upload_invalid_file_type(self, auth_client, project, transaction):
        exe = SimpleUploadedFile("malware.exe", b"MZ fake exe", content_type="application/x-msdownload")
        data = {"file": exe, "document_type": "receipt"}
        response = auth_client.post(list_url(project, transaction), data, format="multipart")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_upload_zero_byte_file(self, auth_client, project, transaction):
        empty = SimpleUploadedFile("empty.pdf", b"", content_type="application/pdf")
        data = {"file": empty, "document_type": "receipt"}
        response = auth_client.post(list_url(project, transaction), data, format="multipart")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_upload_oversized_file(self, auth_client, project, transaction):
        oversized = SimpleUploadedFile(
            "big.pdf",
            b"%PDF-1.4 " + b"x" * (10 * 1024 * 1024 + 1),
            content_type="application/pdf",
        )
        data = {"file": oversized, "document_type": "receipt"}
        response = auth_client.post(list_url(project, transaction), data, format="multipart")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_upload_missing_file(self, auth_client, project, transaction):
        response = auth_client.post(
            list_url(project, transaction), {"document_type": "receipt"}, format="multipart"
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_viewer_without_create_permission_cannot_upload(self, project, transaction):
        viewer = VerifiedUserFactory()
        ProjectMemberFactory(
            project=project,
            user=viewer,
            role=ProjectMember.Role.VIEWER,
            can_create_transactions=False,
        )
        c = APIClient()
        c.force_authenticate(user=viewer)
        data = {"file": _pdf(), "document_type": "receipt"}
        response = c.post(list_url(project, transaction), data, format="multipart")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_upload_executable_sh(self, auth_client, project, transaction):
        sh = SimpleUploadedFile("script.sh", b"#!/bin/bash\nrm -rf /", content_type="application/x-sh")
        data = {"file": sh, "document_type": "receipt"}
        response = auth_client.post(list_url(project, transaction), data, format="multipart")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_upload_long_filename_truncated(self, auth_client, project, transaction):
        long_name = "a" * 300 + ".pdf"
        f = SimpleUploadedFile(long_name, b"%PDF-1.4 content", content_type="application/pdf")
        data = {"file": f, "document_type": "receipt"}
        response = auth_client.post(list_url(project, transaction), data, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.data["file_name"]) <= 255

    def test_upload_for_nonexistent_transaction(self, auth_client, project):
        import uuid
        fake_txn_id = uuid.uuid4()
        url = reverse(
            "document-list-create",
            kwargs={"project_id": project.pk, "transaction_id": fake_txn_id},
        )
        data = {"file": _pdf(), "document_type": "receipt"}
        response = auth_client.post(url, data, format="multipart")
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# Detail (Retrieve & Delete)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestDocumentDetailView:
    def test_retrieve_document(self, auth_client, project, transaction):
        doc = DocumentFactory(transaction=transaction, uploaded_by=project.owner)
        response = auth_client.get(detail_url(project, transaction, doc))
        assert response.status_code == status.HTTP_200_OK
        assert str(response.data["id"]) == str(doc.pk)

    def test_non_member_cannot_retrieve(self, project, transaction):
        doc = DocumentFactory(transaction=transaction, uploaded_by=project.owner)
        other = VerifiedUserFactory()
        c = APIClient()
        c.force_authenticate(user=other)
        response = c.get(detail_url(project, transaction, doc))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_owner_can_delete(self, auth_client, project, user, transaction):
        member_obj = ProjectMember.objects.get(project=project, user=user)
        member_obj.can_delete_transactions = True
        member_obj.save()
        doc = DocumentFactory(transaction=transaction, uploaded_by=user)
        response = auth_client.delete(detail_url(project, transaction, doc))
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Document.objects.filter(pk=doc.pk).exists()

    def test_member_without_delete_permission_gets_403(self, project, transaction):
        member = VerifiedUserFactory()
        ProjectMemberFactory(
            project=project,
            user=member,
            role=ProjectMember.Role.MEMBER,
            can_delete_transactions=False,
        )
        doc = DocumentFactory(transaction=transaction, uploaded_by=project.owner)
        c = APIClient()
        c.force_authenticate(user=member)
        response = c.delete(detail_url(project, transaction, doc))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_wrong_transaction_gives_404(self, auth_client, project, user):
        other_txn = TransactionFactory(project=project, created_by=user)
        doc = DocumentFactory(transaction=other_txn, uploaded_by=user)
        # Try to access doc via a different transaction
        yet_another_txn = TransactionFactory(project=project, created_by=user)
        url = reverse(
            "document-detail",
            kwargs={
                "project_id": project.pk,
                "transaction_id": yet_another_txn.pk,
                "pk": doc.pk,
            },
        )
        member_obj = ProjectMember.objects.get(project=project, user=user)
        member_obj.can_delete_transactions = True
        member_obj.save()
        response = auth_client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestDocumentDownloadView:
    def test_download_document(self, auth_client, project, transaction):
        doc = DocumentFactory(transaction=transaction, uploaded_by=project.owner)
        response = auth_client.get(download_url(project, transaction, doc))
        assert response.status_code == status.HTTP_200_OK
        assert response.get("Content-Disposition") is not None

    def test_download_requires_auth(self, project, transaction):
        doc = DocumentFactory(transaction=transaction, uploaded_by=project.owner)
        c = APIClient()
        response = c.get(download_url(project, transaction, doc))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_non_member_cannot_download(self, project, transaction):
        doc = DocumentFactory(transaction=transaction, uploaded_by=project.owner)
        other = VerifiedUserFactory()
        c = APIClient()
        c.force_authenticate(user=other)
        response = c.get(download_url(project, transaction, doc))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_download_wrong_transaction_gives_404(self, auth_client, project, user):
        other_txn = TransactionFactory(project=project, created_by=user)
        doc = DocumentFactory(transaction=other_txn, uploaded_by=user)
        yet_another = TransactionFactory(project=project, created_by=user)
        url = reverse(
            "document-download",
            kwargs={
                "project_id": project.pk,
                "transaction_id": yet_another.pk,
                "pk": doc.pk,
            },
        )
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
