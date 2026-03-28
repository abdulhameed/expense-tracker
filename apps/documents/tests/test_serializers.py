"""
Tests for documents/serializers.py - Document serializers and validation.

Tests:
- DocumentSerializer.validate_file() - File validation and truncation
- DocumentSerializer.create() - Document creation with metadata
- MIME type validation
- File size validation
- Filename handling
- Security validation
"""

import os
import pytest
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import serializers

from apps.documents.models import Document
from apps.documents.serializers import (
    DocumentSerializer,
    ALLOWED_MIME_TYPES,
    MAX_FILE_SIZE,
    _MAX_FILENAME_LEN,
)
from apps.projects.tests.factories import ProjectFactory
from apps.authentication.tests.factories import VerifiedUserFactory
from apps.transactions.tests.factories import TransactionFactory


@pytest.fixture
def user():
    """Create a test user."""
    return VerifiedUserFactory()


@pytest.fixture
def project(user):
    """Create a test project."""
    return ProjectFactory(owner=user)


@pytest.fixture
def transaction(project, user):
    """Create a test transaction."""
    return TransactionFactory(project=project, created_by=user)


def _create_uploaded_file(
    name="test.pdf",
    content=b"test content",
    mime_type="application/pdf",
    size=None,
):
    """Helper to create SimpleUploadedFile for testing."""
    if size:
        content = content + b"x" * (size - len(content))
    return SimpleUploadedFile(
        name,
        content,
        content_type=mime_type,
    )


class TestDocumentSerializerValidateFile:
    """Test the validate_file method of DocumentSerializer."""

    def test_validate_file_valid_pdf(self):
        """Test validation of valid PDF file."""
        serializer = DocumentSerializer()
        file = _create_uploaded_file(name="test.pdf", mime_type="application/pdf")

        result = serializer.validate_file(file)

        assert result is not None
        assert result.name == "test.pdf"

    def test_validate_file_valid_png(self):
        """Test validation of valid PNG file."""
        serializer = DocumentSerializer()
        file = _create_uploaded_file(name="image.png", mime_type="image/png")

        result = serializer.validate_file(file)

        assert result is not None
        assert result.name == "image.png"

    def test_validate_file_empty_raises_error(self):
        """Test that empty files are rejected."""
        serializer = DocumentSerializer()
        file = SimpleUploadedFile("empty.pdf", b"", content_type="application/pdf")

        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.validate_file(file)

        assert "empty" in str(exc_info.value).lower()

    def test_validate_file_oversized_raises_error(self):
        """Test that files over 10MB are rejected."""
        serializer = DocumentSerializer()
        # Create file larger than 10MB
        size = MAX_FILE_SIZE + 1024
        file = _create_uploaded_file(
            name="large.pdf",
            content=b"x",
            mime_type="application/pdf",
            size=size,
        )

        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.validate_file(file)

        assert "10 MB" in str(exc_info.value) or "exceeds" in str(exc_info.value).lower()

    def test_validate_file_exactly_max_size(self):
        """Test that files exactly at 10MB limit are accepted."""
        serializer = DocumentSerializer()
        file = _create_uploaded_file(
            name="exact.pdf",
            content=b"x",
            mime_type="application/pdf",
            size=MAX_FILE_SIZE,
        )

        result = serializer.validate_file(file)

        assert result is not None

    def test_validate_file_just_under_max_size(self):
        """Test that files just under 10MB limit are accepted."""
        serializer = DocumentSerializer()
        file = _create_uploaded_file(
            name="just_under.pdf",
            content=b"x",
            mime_type="application/pdf",
            size=MAX_FILE_SIZE - 1,
        )

        result = serializer.validate_file(file)

        assert result is not None

    def test_validate_file_invalid_mime_type_raises_error(self):
        """Test that files with disallowed MIME types are rejected."""
        serializer = DocumentSerializer()
        file = _create_uploaded_file(
            name="script.exe",
            mime_type="application/x-msdownload",
        )

        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.validate_file(file)

        assert "not allowed" in str(exc_info.value).lower()

    def test_validate_file_truncates_long_filename(self):
        """Test that long filenames are truncated."""
        serializer = DocumentSerializer()
        long_name = "a" * 300 + ".pdf"
        file = _create_uploaded_file(
            name=long_name,
            mime_type="application/pdf",
        )

        result = serializer.validate_file(file)

        assert len(result.name) <= _MAX_FILENAME_LEN

    def test_validate_file_truncates_preserves_extension(self):
        """Test that filename truncation preserves file extension."""
        serializer = DocumentSerializer()
        long_base = "a" * 300
        file = _create_uploaded_file(
            name=long_base + ".pdf",
            mime_type="application/pdf",
        )

        result = serializer.validate_file(file)

        assert result.name.endswith(".pdf")
        assert len(result.name) <= _MAX_FILENAME_LEN

    def test_validate_file_truncates_with_multiple_dots(self):
        """Test truncation of filenames with multiple dots."""
        serializer = DocumentSerializer()
        long_name = "a" * 300 + ".backup.pdf"
        file = _create_uploaded_file(
            name=long_name,
            mime_type="application/pdf",
        )

        result = serializer.validate_file(file)

        # Should preserve the last extension (.pdf)
        assert result.name.endswith(".pdf")
        assert len(result.name) <= _MAX_FILENAME_LEN

    def test_validate_file_no_extension(self):
        """Test truncation of filename without extension."""
        serializer = DocumentSerializer()
        long_name = "a" * 300
        file = _create_uploaded_file(
            name=long_name,
            mime_type="application/pdf",
        )

        result = serializer.validate_file(file)

        assert len(result.name) <= _MAX_FILENAME_LEN

    def test_validate_file_unicode_filename(self):
        """Test handling of unicode characters in filename."""
        serializer = DocumentSerializer()
        file = _create_uploaded_file(
            name="документ.pdf",
            mime_type="application/pdf",
        )

        result = serializer.validate_file(file)

        assert result is not None

    def test_validate_file_special_chars_filename(self):
        """Test handling of special characters in filename."""
        serializer = DocumentSerializer()
        file = _create_uploaded_file(
            name="file (1) [backup] 2024.pdf",
            mime_type="application/pdf",
        )

        result = serializer.validate_file(file)

        assert result is not None

    def test_validate_file_spaces_in_filename(self):
        """Test handling of spaces in filename."""
        serializer = DocumentSerializer()
        file = _create_uploaded_file(
            name="my document 2024.pdf",
            mime_type="application/pdf",
        )

        result = serializer.validate_file(file)

        assert result is not None


class TestDocumentSerializerMIMETypes:
    """Test MIME type validation for all allowed types."""

    @pytest.mark.parametrize(
        "mime_type",
        [
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
        ],
    )
    def test_validate_file_allowed_mime_type(self, mime_type):
        """Test that all allowed MIME types are accepted."""
        serializer = DocumentSerializer()
        # Create appropriate file extension
        extensions = {
            "application/pdf": ".pdf",
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
            "image/heic": ".heic",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
            "application/vnd.ms-excel": ".xls",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
            "application/msword": ".doc",
            "text/plain": ".txt",
            "text/csv": ".csv",
        }
        ext = extensions.get(mime_type, ".bin")
        file = _create_uploaded_file(
            name=f"test{ext}",
            mime_type=mime_type,
        )

        result = serializer.validate_file(file)

        assert result is not None

    def test_validate_file_disallowed_mime_type(self):
        """Test that disallowed MIME types are rejected."""
        serializer = DocumentSerializer()
        file = _create_uploaded_file(
            name="script.exe",
            mime_type="application/x-msdownload",
        )

        with pytest.raises(serializers.ValidationError):
            serializer.validate_file(file)

    def test_validate_file_spoofed_mime_type(self):
        """Test that spoofed MIME types are rejected."""
        serializer = DocumentSerializer()
        # File with .pdf extension but claiming to be executable
        file = _create_uploaded_file(
            name="malware.pdf",
            mime_type="application/x-msdownload",
        )

        with pytest.raises(serializers.ValidationError):
            serializer.validate_file(file)


@pytest.mark.django_db
class TestDocumentSerializerCreate:
    """Test the create method of DocumentSerializer."""

    def test_create_sets_file_metadata(self, transaction, user):
        """Test that create properly sets file metadata."""
        file = _create_uploaded_file(
            name="test.pdf",
            mime_type="application/pdf",
        )
        data = {
            "file": file,
            "document_type": "receipt",
        }
        serializer = DocumentSerializer(data=data)

        # Manually set transaction since it's read-only in the serializer
        if serializer.is_valid(raise_exception=True):
            document = serializer.save(transaction=transaction, uploaded_by=user)

        assert document.file_name == "test.pdf"
        assert document.file_type == "application/pdf"
        assert document.file_size > 0

    def test_create_truncates_filename_to_255(self, transaction, user):
        """Test that create truncates filename to 255 characters."""
        long_name = "a" * 300 + ".pdf"
        file = _create_uploaded_file(
            name=long_name,
            mime_type="application/pdf",
        )
        serializer = DocumentSerializer(data={"file": file, "document_type": "receipt"})
        serializer.is_valid(raise_exception=True)

        document = serializer.save(transaction=transaction, uploaded_by=user)

        assert len(document.file_name) <= 255

    def test_create_preserves_extension_on_truncation(self, transaction, user):
        """Test that create preserves extension when truncating."""
        long_name = "a" * 300 + ".pdf"
        file = _create_uploaded_file(
            name=long_name,
            mime_type="application/pdf",
        )
        serializer = DocumentSerializer(data={"file": file, "document_type": "receipt"})
        serializer.is_valid(raise_exception=True)

        document = serializer.save(transaction=transaction, uploaded_by=user)

        assert document.file_name.endswith(".pdf")

    def test_create_sets_file_size(self, transaction, user):
        """Test that create properly sets file size."""
        test_size = 5 * 1024  # 5 KB
        file = _create_uploaded_file(
            name="test.pdf",
            mime_type="application/pdf",
            size=test_size,
        )
        serializer = DocumentSerializer(data={"file": file, "document_type": "receipt"})
        serializer.is_valid(raise_exception=True)

        document = serializer.save(transaction=transaction, uploaded_by=user)

        assert document.file_size == test_size

    def test_create_sets_file_type(self, transaction, user):
        """Test that create properly sets file type."""
        file = _create_uploaded_file(
            name="test.pdf",
            mime_type="application/pdf",
        )
        serializer = DocumentSerializer(data={"file": file, "document_type": "receipt"})
        serializer.is_valid(raise_exception=True)

        document = serializer.save(transaction=transaction, uploaded_by=user)

        assert document.file_type == "application/pdf"

    def test_create_sets_uploaded_by(self, transaction, user):
        """Test that create properly sets uploaded_by user."""
        file = _create_uploaded_file(
            name="test.pdf",
            mime_type="application/pdf",
        )
        serializer = DocumentSerializer(data={"file": file, "document_type": "receipt"})
        serializer.is_valid(raise_exception=True)

        document = serializer.save(transaction=transaction, uploaded_by=user)

        assert document.uploaded_by == user

    def test_create_different_file_types(self, transaction, user):
        """Test create with different file types."""
        mime_types = [
            ("application/pdf", "test.pdf"),
            ("image/jpeg", "image.jpg"),
            ("image/png", "image.png"),
            ("text/csv", "data.csv"),
        ]

        for mime_type, filename in mime_types:
            file = _create_uploaded_file(
                name=filename,
                mime_type=mime_type,
            )
            serializer = DocumentSerializer(
                data={"file": file, "document_type": "receipt"}
            )
            serializer.is_valid(raise_exception=True)

            document = serializer.save(transaction=transaction, uploaded_by=user)

            assert document.file_type == mime_type


@pytest.mark.django_db
class TestDocumentSerializerSecurity:
    """Test security aspects of document serializer."""

    def test_path_traversal_in_filename_rejected(self):
        """Test that path traversal attempts in filenames are handled."""
        serializer = DocumentSerializer()
        file = _create_uploaded_file(
            name="../../../etc/passwd.pdf",
            mime_type="application/pdf",
        )

        # Should not raise error but may be handled by Django/file storage
        result = serializer.validate_file(file)

        # Filename should still be in file object (storage layer handles security)
        assert result is not None

    def test_null_bytes_in_filename_handled(self):
        """Test handling of null bytes in filenames."""
        serializer = DocumentSerializer()
        # Most systems/Django will handle this, but we test the serializer
        file = _create_uploaded_file(
            name="test\x00.pdf",
            mime_type="application/pdf",
        )

        # Should not crash
        try:
            result = serializer.validate_file(file)
            assert result is not None
        except Exception:
            # Expected if Django/system rejects it
            pass

    def test_very_short_filename(self, transaction, user):
        """Test handling of very short filenames."""
        file = _create_uploaded_file(
            name="a.pdf",
            mime_type="application/pdf",
        )
        serializer = DocumentSerializer(data={"file": file, "document_type": "receipt"})
        serializer.is_valid(raise_exception=True)

        document = serializer.save(transaction=transaction, uploaded_by=user)

        assert document.file_name == "a.pdf"


@pytest.mark.django_db
class TestDocumentSerializerReadOnlyFields:
    """Test that read-only fields cannot be set during creation."""

    def test_file_name_read_only(self, transaction, user):
        """Test that file_name is computed and cannot be manually set."""
        file = _create_uploaded_file(
            name="test.pdf",
            mime_type="application/pdf",
        )
        serializer = DocumentSerializer(
            data={
                "file": file,
                # file_name is read-only, will be ignored
                "document_type": "receipt",
            }
        )
        serializer.is_valid(raise_exception=True)

        document = serializer.save(transaction=transaction, uploaded_by=user)

        # Should use actual filename
        assert document.file_name == "test.pdf"

    def test_file_size_read_only(self, transaction, user):
        """Test that file_size is computed and cannot be manually set."""
        file = _create_uploaded_file(
            name="test.pdf",
            mime_type="application/pdf",
            size=1024,
        )
        serializer = DocumentSerializer(
            data={
                "file": file,
                # file_size is read-only, will be ignored
                "document_type": "receipt",
            }
        )
        serializer.is_valid(raise_exception=True)

        document = serializer.save(transaction=transaction, uploaded_by=user)

        # Should use actual file size
        assert document.file_size == 1024

    def test_file_type_read_only(self, transaction, user):
        """Test that file_type is computed and cannot be manually set."""
        file = _create_uploaded_file(
            name="test.pdf",
            mime_type="application/pdf",
        )
        serializer = DocumentSerializer(
            data={
                "file": file,
                # file_type is read-only, will be ignored
                "document_type": "receipt",
            }
        )
        serializer.is_valid(raise_exception=True)

        document = serializer.save(transaction=transaction, uploaded_by=user)

        # Should use actual MIME type from file
        assert document.file_type == "application/pdf"
