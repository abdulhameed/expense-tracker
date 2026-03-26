from datetime import timedelta

import factory
from django.utils import timezone
from factory.django import DjangoModelFactory

from apps.authentication.models import EmailVerificationToken, PasswordResetToken, User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_email_verified = False

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        raw = extracted if extracted is not None else "Str0ngPass!"
        obj.set_password(raw)
        if create:
            obj.save(update_fields=["password"])


class VerifiedUserFactory(UserFactory):
    is_email_verified = True


class EmailVerificationTokenFactory(DjangoModelFactory):
    class Meta:
        model = EmailVerificationToken

    user = factory.SubFactory(UserFactory)
    expires_at = factory.LazyFunction(lambda: timezone.now() + timedelta(hours=24))


class PasswordResetTokenFactory(DjangoModelFactory):
    class Meta:
        model = PasswordResetToken

    user = factory.SubFactory(UserFactory)
    expires_at = factory.LazyFunction(lambda: timezone.now() + timedelta(hours=1))
    is_used = False
