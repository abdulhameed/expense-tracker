from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_invitation_email(invitation_id):
    from .models import Invitation

    try:
        invitation = Invitation.objects.select_related("project", "invited_by").get(id=invitation_id)
    except Invitation.DoesNotExist:
        return

    send_mail(
        subject=f"You've been invited to join {invitation.project.name}",
        message=(
            f"Hi,\n\n"
            f"{invitation.invited_by.email} has invited you to join "
            f"'{invitation.project.name}' as a {invitation.get_role_display()}.\n\n"
            f"Use this token to accept the invitation:\n\n"
            f"{invitation.token}\n\n"
            f"This invitation expires in 7 days."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[invitation.email],
        fail_silently=True,
    )
