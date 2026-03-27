from datetime import timedelta

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from apps.authentication.tests.factories import UserFactory
from apps.budgets.models import Budget
from apps.projects.tests.factories import ProjectFactory
from apps.transactions.tests.factories import CategoryFactory


class BudgetFactory(DjangoModelFactory):
    """Factory for creating test Budget instances."""

    class Meta:
        model = Budget

    project = factory.SubFactory(ProjectFactory)
    category = None  # Project-wide budget by default
    amount = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    period = Budget.Period.MONTHLY
    start_date = factory.LazyFunction(lambda: timezone.now().date())
    end_date = factory.LazyFunction(
        lambda: timezone.now().date() + timedelta(days=30)
    )
    alert_threshold = 80
    alert_enabled = True
    created_by = factory.SubFactory(UserFactory)


class BudgetWithCategoryFactory(DjangoModelFactory):
    """Factory for creating test Budget instances with a category."""

    class Meta:
        model = Budget

    project = factory.SubFactory(ProjectFactory)
    category = factory.SubFactory(CategoryFactory)
    amount = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    period = Budget.Period.MONTHLY
    start_date = factory.LazyFunction(lambda: timezone.now().date())
    end_date = factory.LazyFunction(
        lambda: timezone.now().date() + timedelta(days=30)
    )
    alert_threshold = 80
    alert_enabled = True
    created_by = factory.SubFactory(UserFactory)
