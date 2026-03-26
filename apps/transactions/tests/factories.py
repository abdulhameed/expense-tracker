import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from apps.authentication.tests.factories import UserFactory
from apps.projects.tests.factories import ProjectFactory
from apps.transactions.models import Category, Transaction


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    category_type = Category.CategoryType.EXPENSE
    icon = "tag"
    color = "#6B7280"
    project = factory.SubFactory(ProjectFactory)
    is_default = False


class DefaultCategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Default Category {n}")
    category_type = Category.CategoryType.EXPENSE
    project = None
    is_default = True


class TransactionFactory(DjangoModelFactory):
    class Meta:
        model = Transaction

    project = factory.SubFactory(ProjectFactory)
    category = factory.SubFactory(CategoryFactory, project=factory.SelfAttribute("..project"))
    created_by = factory.SubFactory(UserFactory)
    transaction_type = Transaction.TransactionType.EXPENSE
    amount = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    currency = "USD"
    description = factory.Faker("sentence", nb_words=5)
    date = factory.LazyFunction(lambda: timezone.now().date())
    payment_method = Transaction.PaymentMethod.CASH
