import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_factory():
    from apps.authentication.tests.factories import UserFactory
    return UserFactory


@pytest.fixture
def verified_user_factory():
    from apps.authentication.tests.factories import VerifiedUserFactory
    return VerifiedUserFactory
