from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["file_name", "document_type", "file_type", "file_size", "transaction", "uploaded_by", "uploaded_at"]
    list_filter = ["document_type", "file_type"]
    search_fields = ["file_name", "notes"]
    readonly_fields = ["id", "file_name", "file_size", "file_type", "uploaded_at"]
