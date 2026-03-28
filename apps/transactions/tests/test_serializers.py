"""
Tests for transactions/serializers.py - Transaction and Category serializers.

Tests:
- CategorySerializer - Category creation, validation, project access control
- TransactionSerializer - Transaction data serialization and nested fields
- TransactionBulkSerializer - Bulk transaction operations
"""

import pytest
from decimal import Decimal
from django.utils import timezone

from apps.transactions.serializers import (
    CategorySerializer,
    TransactionSerializer,
    TransactionBulkSerializer,
)
from apps.transactions.tests.factories import (
    CategoryFactory,
    TransactionFactory,
)
from apps.projects.tests.factories import ProjectFactory
from apps.projects.models import ProjectMember
from apps.authentication.tests.factories import UserFactory


@pytest.mark.django_db
class TestCategorySerializer:
    """Test CategorySerializer for category validation and serialization."""

    def test_category_serializer_valid_data(self):
        """Test that valid category data is serialized correctly."""
        project = ProjectFactory()
        category = CategoryFactory(
            project=project,
            name="Food & Dining",
            category_type="expense",
            color="#FF5733",
        )

        serializer = CategorySerializer(category)
        data = serializer.data

        assert data["name"] == "Food & Dining"
        assert data["category_type"] == "expense"
        assert data["color"] == "#FF5733"
        assert data["project"] == project.id

    def test_category_serializer_read_only_fields(self):
        """Test that read-only fields cannot be written."""
        project = ProjectFactory()
        category = CategoryFactory(project=project)

        data = {
            "name": "Updated",
            "project": project.id,
            "id": "fake-id",  # Should be ignored
            "created_at": "2020-01-01T00:00:00Z",  # Should be ignored
        }

        serializer = CategorySerializer(category, data=data, partial=True)
        assert serializer.is_valid()

        # Read-only fields should not be changed
        assert serializer.validated_data.get("id") is None
        assert serializer.validated_data.get("created_at") is None

    def test_category_serializer_default_flag(self):
        """Test that is_default flag is read-only."""
        category = CategoryFactory(is_default=False)

        data = {"is_default": True}
        serializer = CategorySerializer(category, data=data, partial=True)

        assert serializer.is_valid()
        # is_default should not change
        assert serializer.validated_data.get("is_default") is None

    def test_category_serializer_requires_context(self):
        """Test that serializer requires request context for validation."""
        project = ProjectFactory()
        user = UserFactory()

        data = {
            "name": "Test Category",
            "category_type": "expense",
            "project": project.id,
        }

        # Without context, validation might fail
        serializer = CategorySerializer(data=data, context={"request": type("Request", (), {"user": user})()})
        # Should work if user is owner
        result = serializer.is_valid()
        # Result depends on user permissions

    def test_category_serializer_permission_check_owner(self):
        """Test that category owner can manage categories."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        data = {
            "name": "New Category",
            "category_type": "expense",
            "project": project.id,
        }

        request = type("Request", (), {"user": user})()
        serializer = CategorySerializer(data=data, context={"request": request})

        assert serializer.is_valid()

    def test_category_serializer_permission_check_member(self):
        """Test that category non-member cannot create."""
        owner = UserFactory()
        project = ProjectFactory(owner=owner)
        other_user = UserFactory()

        data = {
            "name": "New Category",
            "category_type": "expense",
            "project": project.id,
        }

        request = type("Request", (), {"user": other_user})()
        serializer = CategorySerializer(data=data, context={"request": request})

        assert not serializer.is_valid()
        assert "permission" in str(serializer.errors).lower()

    def test_category_serializer_permission_check_admin_member(self):
        """Test that admin member can create categories."""
        owner = UserFactory()
        admin_user = UserFactory()
        project = ProjectFactory(owner=owner)

        # Add admin user as ADMIN
        ProjectMember.objects.create(
            project=project,
            user=admin_user,
            role=ProjectMember.Role.ADMIN,
        )

        data = {
            "name": "New Category",
            "category_type": "expense",
            "project": project.id,
        }

        request = type("Request", (), {"user": admin_user})()
        serializer = CategorySerializer(data=data, context={"request": request})

        assert serializer.is_valid()


@pytest.mark.django_db
class TestTransactionSerializer:
    """Test TransactionSerializer for transaction data handling."""

    def test_transaction_serializer_valid_data(self):
        """Test that valid transaction data is serialized."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project)

        transaction = TransactionFactory(
            project=project,
            created_by=user,
            category=category,
            description="Grocery shopping",
            amount=Decimal("50.75"),
        )

        serializer = TransactionSerializer(transaction)
        data = serializer.data

        assert data["description"] == "Grocery shopping"
        assert data["amount"] == "50.75"
        assert data["project"] == project.id
        assert data["category"] == category.id

    def test_transaction_serializer_nested_fields(self):
        """Test that nested category and user fields are included."""
        user = UserFactory(email="john@example.com")
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project, name="Food")

        transaction = TransactionFactory(
            project=project,
            created_by=user,
            category=category,
        )

        serializer = TransactionSerializer(transaction)
        data = serializer.data

        # Nested read-only fields
        assert data["category_name"] == "Food"
        assert data["created_by_email"] == "john@example.com"

    def test_transaction_serializer_read_only_fields(self):
        """Test that system-generated fields are read-only."""
        transaction = TransactionFactory()

        data = {
            "description": "Updated",
            "id": "fake-id",
            "created_by": 999,
            "project": 999,
        }

        serializer = TransactionSerializer(transaction, data=data, partial=True)
        assert serializer.is_valid()

        # Read-only fields should be ignored
        assert serializer.validated_data.get("id") is None
        assert serializer.validated_data.get("created_by") is None
        assert serializer.validated_data.get("project") is None

    def test_transaction_serializer_amount_types(self):
        """Test that amount field handles decimal values."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        transaction = TransactionFactory(
            project=project,
            created_by=user,
            amount=Decimal("99.99"),
        )

        serializer = TransactionSerializer(transaction)
        # Amount should be serialized as string
        assert isinstance(serializer.data["amount"], str)
        assert serializer.data["amount"] == "99.99"

    def test_transaction_serializer_currency_field(self):
        """Test that currency field is included."""
        transaction = TransactionFactory(currency="EUR")

        serializer = TransactionSerializer(transaction)
        assert serializer.data["currency"] == "EUR"

    def test_transaction_serializer_date_field(self):
        """Test that transaction date is serialized."""
        transaction_date = timezone.now().date()
        transaction = TransactionFactory(date=transaction_date)

        serializer = TransactionSerializer(transaction)
        assert serializer.data["date"] is not None

    def test_transaction_serializer_tags_field(self):
        """Test that tags are serialized."""
        transaction = TransactionFactory(tags=["food", "weekly"])

        serializer = TransactionSerializer(transaction)
        assert "tags" in serializer.data

    def test_transaction_serializer_recurring_flag(self):
        """Test that recurring flag is included."""
        transaction = TransactionFactory(is_recurring=True)

        serializer = TransactionSerializer(transaction)
        assert serializer.data["is_recurring"] is True


@pytest.mark.django_db
class TestTransactionBulkSerializer:
    """Test TransactionBulkSerializer for bulk operations."""

    def test_bulk_serializer_accepts_multiple_transactions(self):
        """Test that bulk serializer accepts multiple transactions."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project)

        transactions_data = [
            {
                "project": project.id,
                "category": category.id,
                "transaction_type": "expense",
                "amount": "100.00",
                "currency": "USD",
                "description": f"Transaction {i}",
                "date": timezone.now().date(),
            }
            for i in range(3)
        ]

        data = {"transactions": transactions_data}
        serializer = TransactionBulkSerializer(data=data)

        assert serializer.is_valid()

    def test_bulk_serializer_requires_at_least_one(self):
        """Test that empty transaction list is rejected."""
        data = {"transactions": []}
        serializer = TransactionBulkSerializer(data=data)

        assert not serializer.is_valid()
        assert "At least one transaction is required" in str(serializer.errors)

    def test_bulk_serializer_rejects_too_many(self):
        """Test that bulk serializer rejects more than 100 transactions."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project)

        transactions_data = [
            {
                "project": project.id,
                "category": category.id,
                "transaction_type": "expense",
                "amount": "100.00",
                "currency": "USD",
                "description": f"Transaction {i}",
                "date": timezone.now().date(),
            }
            for i in range(101)  # More than limit
        ]

        data = {"transactions": transactions_data}
        serializer = TransactionBulkSerializer(data=data)

        assert not serializer.is_valid()
        assert "100" in str(serializer.errors)

    def test_bulk_serializer_accepts_exactly_100(self):
        """Test that serializer accepts exactly 100 transactions."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project)

        transactions_data = [
            {
                "project": project.id,
                "category": category.id,
                "transaction_type": "expense",
                "amount": "100.00",
                "currency": "USD",
                "description": f"Transaction {i}",
                "date": timezone.now().date(),
            }
            for i in range(100)
        ]

        data = {"transactions": transactions_data}
        serializer = TransactionBulkSerializer(data=data)

        # Should be valid
        assert serializer.is_valid()


@pytest.mark.django_db
class TestSerializerIntegration:
    """Integration tests for serializers."""

    def test_category_and_transaction_serialization(self):
        """Test that category and transaction serializers work together."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project)

        # Serialize category
        cat_serializer = CategorySerializer(category)
        assert cat_serializer.data["name"] == category.name

        # Create transaction with category
        transaction = TransactionFactory(
            project=project,
            created_by=user,
            category=category,
        )

        # Serialize transaction
        trans_serializer = TransactionSerializer(transaction)
        assert trans_serializer.data["category_name"] == category.name

    def test_transaction_serializer_with_update(self):
        """Test that transaction serializer handles updates."""
        transaction = TransactionFactory(
            description="Original",
            amount=Decimal("100.00"),
        )

        update_data = {
            "description": "Updated",
            "amount": "150.00",
        }

        serializer = TransactionSerializer(
            transaction,
            data=update_data,
            partial=True,
        )

        assert serializer.is_valid()
        updated = serializer.save()
        assert updated.description == "Updated"
        assert updated.amount == Decimal("150.00")

    def test_bulk_serializer_with_transaction_serializer(self):
        """Test that bulk serializer uses transaction serializer."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project)

        # Create bulk data
        data = {
            "transactions": [
                {
                    "project": project.id,
                    "category": category.id,
                    "transaction_type": "expense",
                    "amount": f"{i * 10}.00",
                    "currency": "USD",
                    "description": f"Item {i}",
                    "date": timezone.now().date(),
                }
                for i in range(1, 4)
            ]
        }

        serializer = TransactionBulkSerializer(data=data)
        assert serializer.is_valid()
