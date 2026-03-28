import uuid
from decimal import Decimal
from datetime import date

import pytest

from apps.transactions.models import Category, Transaction
from apps.projects.tests.factories import ProjectFactory
from apps.authentication.tests.factories import UserFactory

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

    def test_category_with_project(self):
        """Test category linked to project."""
        project = ProjectFactory()
        cat = CategoryFactory(project=project)
        assert cat.project == project

    def test_category_color_default(self):
        """Test default color value."""
        cat = CategoryFactory()
        assert cat.color == "#6B7280"

    def test_category_custom_color(self):
        """Test custom color assignment."""
        cat = CategoryFactory(color="#FF5733")
        assert cat.color == "#FF5733"

    def test_category_with_icon(self):
        """Test category icon field."""
        cat = CategoryFactory(icon="restaurant")
        assert cat.icon == "restaurant"

    def test_category_ordering_by_name(self):
        """Test categories are ordered by name."""
        project = ProjectFactory()
        CategoryFactory(project=project, name="Zebra")
        CategoryFactory(project=project, name="Apple")
        CategoryFactory(project=project, name="Banana")

        cats = Category.objects.filter(project=project)
        names = [c.name for c in cats]
        assert names == sorted(names)

    def test_category_project_cascade_delete(self):
        """Test that deleting project deletes categories."""
        project = ProjectFactory()
        cat = CategoryFactory(project=project)
        cat_id = cat.id

        project.delete()
        assert not Category.objects.filter(id=cat_id).exists()

    def test_category_transaction_relationship(self):
        """Test category relationship with transactions."""
        cat = CategoryFactory()
        TransactionFactory(category=cat)
        TransactionFactory(category=cat)

        assert cat.transactions.count() >= 2

    def test_expense_category(self):
        """Test expense category type."""
        cat = CategoryFactory(category_type=Category.CategoryType.EXPENSE)
        assert cat.category_type == "expense"

    def test_income_category(self):
        """Test income category type."""
        cat = CategoryFactory(category_type=Category.CategoryType.INCOME)
        assert cat.category_type == "income"

    def test_category_blank_icon(self):
        """Test category with blank icon."""
        cat = CategoryFactory(icon="")
        assert cat.icon == ""


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

    def test_transaction_with_tags(self):
        """Test transaction with tags."""
        txn = TransactionFactory(tags=["food", "weekly"])
        assert "food" in txn.tags
        assert "weekly" in txn.tags

    def test_recurring_transaction(self):
        """Test recurring transaction flag."""
        txn = TransactionFactory(is_recurring=True)
        assert txn.is_recurring is True

    def test_transaction_currency(self):
        """Test transaction currency field."""
        txn = TransactionFactory(currency="EUR")
        assert txn.currency == "EUR"

    def test_transaction_default_currency(self):
        """Test default currency is USD."""
        txn = TransactionFactory()
        assert txn.currency == "USD"

    def test_transaction_description(self):
        """Test transaction description."""
        txn = TransactionFactory(description="Lunch at restaurant")
        assert txn.description == "Lunch at restaurant"

    def test_transaction_notes(self):
        """Test transaction notes field."""
        txn = TransactionFactory(notes="Great food and service")
        assert txn.notes == "Great food and service"

    def test_transaction_reference_number(self):
        """Test transaction reference number."""
        txn = TransactionFactory(reference_number="REF123456")
        assert txn.reference_number == "REF123456"

    def test_transaction_decimal_amount(self):
        """Test decimal amount precision."""
        amount = Decimal("1234.56")
        txn = TransactionFactory(amount=amount)
        assert txn.amount == amount

    def test_transaction_large_amount(self):
        """Test handling large amounts."""
        amount = Decimal("999999999.99")
        txn = TransactionFactory(amount=amount)
        assert txn.amount == amount

    def test_transaction_date_field(self):
        """Test transaction date field."""
        transaction_date = date(2024, 3, 15)
        txn = TransactionFactory(date=transaction_date)
        assert txn.date == transaction_date

    def test_transaction_category_optional(self):
        """Test category is optional."""
        txn = TransactionFactory(category=None)
        assert txn.category is None

    def test_transaction_created_by_optional(self):
        """Test created_by can be null."""
        txn = TransactionFactory(created_by=None)
        assert txn.created_by is None

    def test_transaction_cash_payment(self):
        """Test cash payment method."""
        txn = TransactionFactory(payment_method=Transaction.PaymentMethod.CASH)
        assert txn.payment_method == "cash"

    def test_transaction_card_payment(self):
        """Test card payment method."""
        txn = TransactionFactory(payment_method=Transaction.PaymentMethod.CARD)
        assert txn.payment_method == "card"

    def test_transaction_bank_transfer_payment(self):
        """Test bank transfer payment method."""
        txn = TransactionFactory(payment_method=Transaction.PaymentMethod.BANK_TRANSFER)
        assert txn.payment_method == "bank_transfer"

    def test_transaction_mobile_payment(self):
        """Test mobile payment method."""
        txn = TransactionFactory(payment_method=Transaction.PaymentMethod.MOBILE_PAYMENT)
        assert txn.payment_method == "mobile_payment"

    def test_transaction_other_payment(self):
        """Test other payment method."""
        txn = TransactionFactory(payment_method=Transaction.PaymentMethod.OTHER)
        assert txn.payment_method == "other"

    def test_transaction_default_payment_method(self):
        """Test default payment method is cash."""
        txn = TransactionFactory()
        assert txn.payment_method == "cash"

    def test_transaction_expense_type(self):
        """Test expense transaction type."""
        txn = TransactionFactory(transaction_type=Transaction.TransactionType.EXPENSE)
        assert txn.transaction_type == "expense"

    def test_transaction_income_type(self):
        """Test income transaction type."""
        txn = TransactionFactory(transaction_type=Transaction.TransactionType.INCOME)
        assert txn.transaction_type == "income"

    def test_transaction_ordering(self):
        """Test transactions ordered by date desc."""
        project = ProjectFactory()
        user = UserFactory()

        date1 = date(2024, 1, 1)
        date2 = date(2024, 1, 2)
        date3 = date(2024, 1, 3)

        TransactionFactory(project=project, created_by=user, date=date1)
        TransactionFactory(project=project, created_by=user, date=date2)
        TransactionFactory(project=project, created_by=user, date=date3)

        txns = Transaction.objects.filter(project=project)
        dates = [t.date for t in txns]
        # Most recent should be first
        assert dates[0] >= dates[-1]

    def test_transaction_created_by_set_null_on_user_delete(self):
        """Test that created_by becomes null when user is deleted."""
        user = UserFactory()
        txn = TransactionFactory(created_by=user)

        user.delete()

        txn.refresh_from_db()
        assert txn.created_by is None

    def test_transaction_blank_description(self):
        """Test transaction with blank description."""
        txn = TransactionFactory(description="")
        assert txn.description == ""

    def test_transaction_blank_notes(self):
        """Test transaction with blank notes."""
        txn = TransactionFactory(notes="")
        assert txn.notes == ""

    def test_transaction_blank_reference(self):
        """Test transaction with blank reference number."""
        txn = TransactionFactory(reference_number="")
        assert txn.reference_number == ""

    def test_transaction_max_description_length(self):
        """Test transaction with max description length."""
        long_desc = "x" * 500
        txn = TransactionFactory(description=long_desc)
        assert len(txn.description) == 500
