from datetime import timedelta
from unittest.mock import patch

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.authentication.models import EmailVerificationToken, PasswordResetToken

from .factories import (
    EmailVerificationTokenFactory,
    PasswordResetTokenFactory,
    UserFactory,
    VerifiedUserFactory,
)


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def auth_client(client):
    user = VerifiedUserFactory()
    client.force_authenticate(user=user)
    client._user = user
    return client


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestRegisterView:
    url = reverse("auth-register")

    @patch("apps.authentication.views.send_email_verification.delay")
    def test_register_success(self, mock_task, client):
        payload = {
            "email": "new@example.com",
            "password": "Str0ngPass!",
            "password_confirm": "Str0ngPass!",
            "first_name": "John",
            "last_name": "Doe",
        }
        response = client.post(self.url, payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert "tokens" in response.data
        assert response.data["user"]["email"] == "new@example.com"
        mock_task.assert_called_once()

    def test_register_duplicate_email(self, client):
        user = UserFactory()
        payload = {
            "email": user.email,
            "password": "Str0ngPass!",
            "password_confirm": "Str0ngPass!",
        }
        response = client.post(self.url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_password_mismatch(self, client):
        payload = {
            "email": "mismatch@example.com",
            "password": "Str0ngPass!",
            "password_confirm": "Different1!",
        }
        response = client.post(self.url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password_confirm" in response.data

    def test_register_weak_password(self, client):
        payload = {
            "email": "weak@example.com",
            "password": "123",
            "password_confirm": "123",
        }
        response = client.post(self.url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_invalid_email(self, client):
        payload = {
            "email": "not-an-email",
            "password": "Str0ngPass!",
            "password_confirm": "Str0ngPass!",
        }
        response = client.post(self.url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_fields(self, client):
        response = client.post(self.url, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("apps.authentication.views.send_email_verification.delay")
    def test_register_returns_jwt_tokens(self, mock_task, client):
        payload = {
            "email": "jwt@example.com",
            "password": "Str0ngPass!",
            "password_confirm": "Str0ngPass!",
        }
        response = client.post(self.url, payload)
        assert "access" in response.data["tokens"]
        assert "refresh" in response.data["tokens"]


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestLoginView:
    url = reverse("auth-login")

    def test_login_success(self, client):
        user = UserFactory()
        response = client.post(self.url, {"email": user.email, "password": "Str0ngPass!"})
        assert response.status_code == status.HTTP_200_OK
        assert "tokens" in response.data
        assert response.data["user"]["email"] == user.email

    def test_login_wrong_password(self, client):
        user = UserFactory()
        response = client.post(self.url, {"email": user.email, "password": "WrongPass!"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_email(self, client):
        response = client.post(self.url, {"email": "ghost@example.com", "password": "Str0ngPass!"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_inactive_user(self, client):
        user = UserFactory(is_active=False)
        response = client.post(self.url, {"email": user.email, "password": "Str0ngPass!"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_updates_last_login_ip(self, client):
        user = UserFactory()
        client.post(self.url, {"email": user.email, "password": "Str0ngPass!"})
        user.refresh_from_db()
        assert user.last_login_ip is not None

    def test_login_missing_fields(self, client):
        response = client.post(self.url, {"email": "x@x.com"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_returns_access_and_refresh(self, client):
        user = UserFactory()
        response = client.post(self.url, {"email": user.email, "password": "Str0ngPass!"})
        assert "access" in response.data["tokens"]
        assert "refresh" in response.data["tokens"]


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestLogoutView:
    url = reverse("auth-logout")

    def test_logout_success(self, client):
        user = UserFactory()
        login_resp = client.post(reverse("auth-login"), {"email": user.email, "password": "Str0ngPass!"})
        refresh = login_resp.data["tokens"]["refresh"]

        client.force_authenticate(user=user)
        response = client.post(self.url, {"refresh": refresh})
        assert response.status_code == status.HTTP_200_OK

    def test_logout_unauthenticated(self, client):
        response = client.post(self.url, {"refresh": "sometoken"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_missing_refresh_token(self, auth_client):
        response = auth_client.post(self.url, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_logout_invalid_token(self, auth_client):
        response = auth_client.post(self.url, {"refresh": "invalid.token.here"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_blacklisted_token_cannot_refresh(self, client):
        user = UserFactory()
        login_resp = client.post(reverse("auth-login"), {"email": user.email, "password": "Str0ngPass!"})
        refresh = login_resp.data["tokens"]["refresh"]

        client.force_authenticate(user=user)
        client.post(self.url, {"refresh": refresh})

        # Try to use the blacklisted refresh token
        client.force_authenticate(user=None)
        response = client.post(reverse("auth-token-refresh"), {"refresh": refresh})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Me (profile)
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestMeView:
    url = reverse("auth-me")

    def test_get_profile_authenticated(self, auth_client):
        response = auth_client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == auth_client._user.email

    def test_get_profile_unauthenticated(self, client):
        response = client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self, auth_client):
        response = auth_client.patch(self.url, {"first_name": "Updated"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Updated"

    def test_cannot_update_email_via_patch(self, auth_client):
        original_email = auth_client._user.email
        auth_client.patch(self.url, {"email": "new@example.com"})
        auth_client._user.refresh_from_db()
        assert auth_client._user.email == original_email

    def test_update_timezone(self, auth_client):
        response = auth_client.patch(self.url, {"timezone": "America/New_York"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["timezone"] == "America/New_York"

    def test_update_currency_preference(self, auth_client):
        response = auth_client.patch(self.url, {"currency_preference": "EUR"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["currency_preference"] == "EUR"

    def test_put_not_allowed(self, auth_client):
        response = auth_client.put(self.url, {"first_name": "Test"})
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


# ---------------------------------------------------------------------------
# Email Verification
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestVerifyEmailView:
    url = reverse("auth-verify-email")

    def test_verify_email_success(self, client):
        token_obj = EmailVerificationTokenFactory(
            expires_at=timezone.now() + timedelta(hours=1)
        )
        response = client.post(self.url, {"token": token_obj.token})
        assert response.status_code == status.HTTP_200_OK
        token_obj.user.refresh_from_db()
        assert token_obj.user.is_email_verified is True

    def test_token_deleted_after_verification(self, client):
        token_obj = EmailVerificationTokenFactory(
            expires_at=timezone.now() + timedelta(hours=1)
        )
        token_val = token_obj.token
        client.post(self.url, {"token": token_val})
        assert not EmailVerificationToken.objects.filter(token=token_val).exists()

    def test_invalid_token(self, client):
        response = client.post(self.url, {"token": "notavalidtoken"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_expired_token(self, client):
        token_obj = EmailVerificationTokenFactory(
            expires_at=timezone.now() - timedelta(seconds=1)
        )
        response = client.post(self.url, {"token": token_obj.token})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_token_field(self, client):
        response = client.post(self.url, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


# ---------------------------------------------------------------------------
# Password Reset
# ---------------------------------------------------------------------------
@pytest.mark.django_db
class TestPasswordResetRequestView:
    url = reverse("auth-password-reset")

    @patch("apps.authentication.views.send_password_reset_email.delay")
    def test_reset_request_existing_email(self, mock_task, client):
        user = UserFactory()
        response = client.post(self.url, {"email": user.email})
        assert response.status_code == status.HTTP_200_OK
        mock_task.assert_called_once_with(str(user.id))

    def test_reset_request_nonexistent_email(self, client):
        # Should still return 200 to prevent enumeration
        response = client.post(self.url, {"email": "ghost@example.com"})
        assert response.status_code == status.HTTP_200_OK

    @patch("apps.authentication.views.send_password_reset_email.delay")
    def test_reset_invalidates_old_tokens(self, mock_task, client):
        user = UserFactory()
        old_token = PasswordResetTokenFactory(user=user, is_used=False)
        client.post(self.url, {"email": user.email})
        old_token.refresh_from_db()
        assert old_token.is_used is True

    def test_missing_email(self, client):
        response = client.post(self.url, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPasswordResetConfirmView:
    url = reverse("auth-password-confirm")

    def test_reset_confirm_success(self, client):
        token_obj = PasswordResetTokenFactory(
            expires_at=timezone.now() + timedelta(hours=1)
        )
        response = client.post(self.url, {
            "token": token_obj.token,
            "password": "NewStr0ng!",
            "password_confirm": "NewStr0ng!",
        })
        assert response.status_code == status.HTTP_200_OK
        token_obj.user.refresh_from_db()
        assert token_obj.user.check_password("NewStr0ng!")

    def test_token_marked_used_after_reset(self, client):
        token_obj = PasswordResetTokenFactory(
            expires_at=timezone.now() + timedelta(hours=1)
        )
        client.post(self.url, {
            "token": token_obj.token,
            "password": "NewStr0ng!",
            "password_confirm": "NewStr0ng!",
        })
        token_obj.refresh_from_db()
        assert token_obj.is_used is True

    def test_cannot_reuse_token(self, client):
        token_obj = PasswordResetTokenFactory(is_used=True)
        response = client.post(self.url, {
            "token": token_obj.token,
            "password": "NewStr0ng!",
            "password_confirm": "NewStr0ng!",
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_expired_token(self, client):
        token_obj = PasswordResetTokenFactory(
            expires_at=timezone.now() - timedelta(seconds=1)
        )
        response = client.post(self.url, {
            "token": token_obj.token,
            "password": "NewStr0ng!",
            "password_confirm": "NewStr0ng!",
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_token(self, client):
        response = client.post(self.url, {
            "token": "badtoken",
            "password": "NewStr0ng!",
            "password_confirm": "NewStr0ng!",
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_mismatch(self, client):
        token_obj = PasswordResetTokenFactory(
            expires_at=timezone.now() + timedelta(hours=1)
        )
        response = client.post(self.url, {
            "token": token_obj.token,
            "password": "NewStr0ng!",
            "password_confirm": "Different1!",
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_weak_password(self, client):
        token_obj = PasswordResetTokenFactory(
            expires_at=timezone.now() + timedelta(hours=1)
        )
        response = client.post(self.url, {
            "token": token_obj.token,
            "password": "123",
            "password_confirm": "123",
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
