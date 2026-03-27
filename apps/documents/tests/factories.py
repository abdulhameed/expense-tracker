import io

import factory
from django.core.files.uploadedfile import SimpleUploadedFile
from factory.django import DjangoModelFactory

from apps.authentication.tests.factories import UserFactory
from apps.documents.models import Document
from apps.transactions.tests.factories import TransactionFactory


def _pdf_file(name="receipt.pdf"):
    content = b"%PDF-1.4 fake pdf content"
    return SimpleUploadedFile(name, content, content_type="application/pdf")


class DocumentFactory(DjangoModelFactory):
    class Meta:
        model = Document

    transaction = factory.SubFactory(TransactionFactory)
    file = factory.LazyFunction(lambda: _pdf_file())
    file_name = "receipt.pdf"
    file_size = 25
    file_type = "application/pdf"
    document_type = Document.DocumentType.RECEIPT
    uploaded_by = factory.SubFactory(UserFactory)
    notes = ""
