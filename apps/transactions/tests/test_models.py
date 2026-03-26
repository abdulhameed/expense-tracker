import uuid

import pytest

from apps.transactions.models import Category, Transaction

from .factories import CategoryFactory, DefaultCategoryFactory, TransactionFactory


@pytest.mark.django_db
class TestCategoryModel:
    def test_create_category(self):
        cat = CategoryFactory()
        assert cat.pk is not None
        assert isinstance(cat.pk, uuid.UUID)

    def test_str_representation(self):
        cat = CategoryFactory(name="Food", category_type=Category.CategoryType.EXPENSE)
        assert "Food" in str(cat)
        assert "expense" in str(cat)

    def test_default_category(self):
        cat = DefaultCategoryFactory()
        assert cat.is_default is True
        assert cat.project is None

    def test_category_types(self):
        for ctype in Category.CategoryType:
            cat = CategoryFactory(category_type=ctype)
            assert cat.category_type == ctype.value


@pytest.mark.django_db
class TestTransactionModel:
    def test_create_transaction(self):
        txn = TransactionFactory()
        assert txn.pk is not None
        assert isinstance(txn.pk, uuid.UUID)

    def test_str_representation(self):
        txn = TransactionFactory(transaction_type=Transaction.TransactionType.EXPENSE)
        s = str(txn)
        assert "expense" in s
        assert str(txn.amount) in s

    def test_timestamps(self):
        txn = TransactionFactory()
        assert txn.created_at is not None
        assert txn.updated_at is not None

    def test_cascade_delete_project(self):
        txn = TransactionFactory()
        project_id = txn.project_id
        txn.project.delete()
        assert not Transaction.objects.filter(project_id=project_id).exists()

    def test_category_set_null_on_delete(self):
        txn = TransactionFactory()
        txn.category.delete()
        txn.refresh_from_db()
        assert txn.category is None

    def test_transaction_types(self):
        for ttype in Transaction.TransactionType:
            txn = TransactionFactory(transaction_type=ttype)
            assert txn.transaction_type == ttype.value

    def test_payment_methods(self):
        for method in Transaction.PaymentMethod:
            txn = TransactionFactory(payment_method=method)
            assert txn.payment_method == method.value

    def test_default_tags(self):
        txn = TransactionFactory()
        assert txn.tags == []

    def test_is_not_recurring_by_default(self):
        txn = TransactionFactory()
        assert txn.is_recurring is False
