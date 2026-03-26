from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone


@shared_task
def send_email_verification(user_id):
    from .models import EmailVerificationToken, User

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    # Replace any existing token
    EmailVerificationToken.objects.filter(user=user).delete()
    token_obj = EmailVerificationToken.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(hours=24),
    )

    send_mail(
        subject="Verify your email address",
        message=(
            f"Hi {user.first_name or user.email},\n\n"
            f"Use the following token to verify your email address:\n\n"
            f"{token_obj.token}\n\n"
            "This token expires in 24 hours."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


@shared_task
def send_password_reset_email(user_id):
    from .models import PasswordResetToken, User

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return

    token_obj = PasswordResetToken.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(hours=1),
    )

    send_mail(
        subject="Reset your password",
        message=(
            f"Hi {user.first_name or user.email},\n\n"
            f"Use the following token to reset your password:\n\n"
            f"{token_obj.token}\n\n"
            "This token expires in 1 hour. If you did not request a password reset, ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )
