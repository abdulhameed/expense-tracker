from datetime import timedelta

import pytest
from django.utils import timezone

from apps.authentication.models import EmailVerificationToken, PasswordResetToken, User

from .factories import (
    EmailVerificationTokenFactory,
    PasswordResetTokenFactory,
    UserFactory,
    VerifiedUserFactory,
)


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = UserFactory()
        assert user.pk is not None
        assert user.email

    def test_email_is_unique(self):
        from django.db import IntegrityError

        user = UserFactory()
        with pytest.raises(IntegrityError):
            UserFactory(email=user.email)

    def test_str_returns_email(self):
        user = UserFactory(email="test@example.com")
        assert str(user) == "test@example.com"

    def test_default_values(self):
        user = UserFactory()
        assert user.timezone == "UTC"
        assert user.currency_preference == "USD"
        assert user.is_email_verified is False
        assert user.last_login_ip is None
        assert user.phone_number == ""

    def test_uuid_primary_key(self):
        import uuid

        user = UserFactory()
        assert isinstance(user.pk, uuid.UUID)

    def test_timestamps_set_on_create(self):
        user = UserFactory()
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_username_field_is_email(self):
        assert User.USERNAME_FIELD == "email"

    def test_required_fields_empty(self):
        assert User.REQUIRED_FIELDS == []

    def test_password_is_hashed(self):
        user = UserFactory()
        assert not user.password.startswith("Str0ngPass!")
        assert user.check_password("Str0ngPass!")

    def test_create_superuser(self):
        admin = User.objects.create_superuser(email="admin@example.com", password="Admin123!")
        assert admin.is_staff
        assert admin.is_superuser

    def test_inactive_user(self):
        user = UserFactory(is_active=False)
        assert not user.is_active

    def test_verified_user_factory(self):
        user = VerifiedUserFactory()
        assert user.is_email_verified is True


@pytest.mark.django_db
class TestEmailVerificationTokenModel:
    def test_token_auto_generated(self):
        token_obj = EmailVerificationTokenFactory()
        assert token_obj.token
        assert len(token_obj.token) > 0

    def test_token_is_unique(self):
        t1 = EmailVerificationTokenFactory()
        t2 = EmailVerificationTokenFactory()
        assert t1.token != t2.token

    def test_not_expired(self):
        token_obj = EmailVerificationTokenFactory(
            expires_at=timezone.now() + timedelta(hours=1)
        )
        assert not token_obj.is_expired

    def test_is_expired(self):
        token_obj = EmailVerificationTokenFactory(
            expires_at=timezone.now() - timedelta(seconds=1)
        )
        assert token_obj.is_expired

    def test_str_representation(self):
        user = UserFactory(email="verify@example.com")
        token_obj = EmailVerificationTokenFactory(user=user)
        assert "verify@example.com" in str(token_obj)

    def test_cascade_delete_with_user(self):
        token_obj = EmailVerificationTokenFactory()
        user_id = token_obj.user_id
        token_obj.user.delete()
        assert not EmailVerificationToken.objects.filter(user_id=user_id).exists()

    def test_one_to_one_constraint(self):
        from django.db import IntegrityError

        user = UserFactory()
        EmailVerificationTokenFactory(user=user)
        with pytest.raises(IntegrityError):
            EmailVerificationTokenFactory(user=user)


@pytest.mark.django_db
class TestPasswordResetTokenModel:
    def test_token_auto_generated(self):
        token_obj = PasswordResetTokenFactory()
        assert token_obj.token
        assert len(token_obj.token) > 0

    def test_token_is_unique(self):
        t1 = PasswordResetTokenFactory()
        t2 = PasswordResetTokenFactory()
        assert t1.token != t2.token

    def test_not_expired(self):
        token_obj = PasswordResetTokenFactory(
            expires_at=timezone.now() + timedelta(hours=1)
        )
        assert not token_obj.is_expired

    def test_is_expired(self):
        token_obj = PasswordResetTokenFactory(
            expires_at=timezone.now() - timedelta(seconds=1)
        )
        assert token_obj.is_expired

    def test_default_is_used_false(self):
        token_obj = PasswordResetTokenFactory()
        assert token_obj.is_used is False

    def test_str_representation(self):
        user = UserFactory(email="reset@example.com")
        token_obj = PasswordResetTokenFactory(user=user)
        assert "reset@example.com" in str(token_obj)

    def test_cascade_delete_with_user(self):
        token_obj = PasswordResetTokenFactory()
        user_id = token_obj.user_id
        token_obj.user.delete()
        assert not PasswordResetToken.objects.filter(user_id=user_id).exists()

    def test_user_can_have_multiple_tokens(self):
        user = UserFactory()
        t1 = PasswordResetTokenFactory(user=user)
        t2 = PasswordResetTokenFactory(user=user)
        assert PasswordResetToken.objects.filter(user=user).count() == 2
        assert t1.token != t2.token
