from uuid import uuid4

from django.conf import settings
from django.db import models

from apps.transactions.models import Transaction


class Document(models.Model):
    class DocumentType(models.TextChoices):
        RECEIPT = "receipt", "Receipt"
        INVOICE = "invoice", "Invoice"
        CONTRACT = "contract", "Contract"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    transaction = models.ForeignKey(
        Transaction, on_delete=models.CASCADE, related_name="documents"
    )

    # File details
    file = models.FileField(upload_to="documents/%Y/%m/", max_length=500)
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField()  # bytes
    file_type = models.CharField(max_length=100)  # MIME type
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        default=DocumentType.RECEIPT,
    )

    # Metadata
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="uploaded_documents",
    )
    notes = models.TextField(blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.document_type} – {self.file_name}"
