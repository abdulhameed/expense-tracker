import os

from rest_framework import serializers

from .models import Document

_MAX_FILENAME_LEN = 240  # leave room for storage uniqueness suffixes

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "image/heic",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "text/plain",
    "text/csv",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "transaction",
            "file",
            "file_name",
            "file_size",
            "file_type",
            "document_type",
            "uploaded_by",
            "notes",
            "uploaded_at",
        ]
        read_only_fields = [
            "id",
            "transaction",
            "file_name",
            "file_size",
            "file_type",
            "uploaded_by",
            "uploaded_at",
        ]

    def validate_file(self, value):
        # Truncate extremely long filenames so the OS doesn't reject them
        name = value.name
        if len(name) > _MAX_FILENAME_LEN:
            base, ext = os.path.splitext(name)
            value.name = base[: _MAX_FILENAME_LEN - len(ext)] + ext

        if value.size == 0:
            raise serializers.ValidationError("Uploaded file is empty.")
        if value.size > MAX_FILE_SIZE:
            raise serializers.ValidationError(
                f"File size exceeds the 10 MB limit ({value.size} bytes)."
            )
        mime_type = value.content_type
        if mime_type not in ALLOWED_MIME_TYPES:
            raise serializers.ValidationError(
                f"File type '{mime_type}' is not allowed."
            )
        return value

    def create(self, validated_data):
        file = validated_data["file"]
        validated_data["file_name"] = file.name[:255]
        validated_data["file_size"] = file.size
        validated_data["file_type"] = file.content_type
        return super().create(validated_data)
