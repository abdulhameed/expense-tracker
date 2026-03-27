import uuid

import pytest

from apps.documents.models import Document

from .factories import DocumentFactory


@pytest.mark.django_db
class TestDocumentModel:
    def test_create_document(self):
        doc = DocumentFactory()
        assert doc.pk is not None
        assert isinstance(doc.pk, uuid.UUID)

    def test_str_representation(self):
        doc = DocumentFactory(document_type=Document.DocumentType.RECEIPT, file_name="bill.pdf")
        s = str(doc)
        assert "receipt" in s
        assert "bill.pdf" in s

    def test_default_document_type(self):
        doc = DocumentFactory()
        assert doc.document_type == Document.DocumentType.RECEIPT

    def test_document_types(self):
        for dtype in Document.DocumentType:
            doc = DocumentFactory(document_type=dtype)
            assert doc.document_type == dtype.value

    def test_cascade_delete_transaction(self):
        doc = DocumentFactory()
        txn_id = doc.transaction_id
        doc.transaction.delete()
        assert not Document.objects.filter(transaction_id=txn_id).exists()

    def test_uploaded_at_auto_set(self):
        doc = DocumentFactory()
        assert doc.uploaded_at is not None

    def test_ordering_newest_first(self):
        doc1 = DocumentFactory()
        doc2 = DocumentFactory()
        docs = list(Document.objects.filter(pk__in=[doc1.pk, doc2.pk]))
        assert docs[0].pk == doc2.pk
