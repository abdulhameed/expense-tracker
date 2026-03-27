"""
Signal handlers for logging model changes automatically.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from apps.transactions.models import Transaction, Category
from apps.budgets.models import Budget
from apps.documents.models import Document
from apps.projects.models import Project, ProjectMember, Invitation

from .models import ActivityLog
from .utils import get_client_ip

User = get_user_model()


# Transaction logging
@receiver(post_save, sender=Transaction)
def log_transaction(sender, instance, created, update_fields=None, **kwargs):
    """Log transaction creation or update."""
    if created:
        action = ActivityLog.ActionType.CREATE
        description = f"Created transaction '{instance.description}' for {instance.amount} {instance.currency}"
    else:
        action = ActivityLog.ActionType.UPDATE
        description = f"Updated transaction '{instance.description}'"

    ActivityLog.objects.create(
        user=instance.created_by,
        project=instance.project,
        action=action,
        content_type="transaction",
        object_id=instance.id,
        description=description,
        metadata={
            "transaction_type": instance.transaction_type,
            "amount": str(instance.amount),
            "currency": instance.currency,
        },
    )


@receiver(post_delete, sender=Transaction)
def log_transaction_delete(sender, instance, **kwargs):
    """Log transaction deletion."""
    ActivityLog.objects.create(
        user=None,  # User might be deleted
        project=instance.project,
        action=ActivityLog.ActionType.DELETE,
        content_type="transaction",
        object_id=instance.id,
        description=f"Deleted transaction '{instance.description}'",
        metadata={
            "transaction_type": instance.transaction_type,
            "amount": str(instance.amount),
        },
    )


# Category logging
@receiver(post_save, sender=Category)
def log_category(sender, instance, created, **kwargs):
    """Log category creation or update."""
    if created:
        action = ActivityLog.ActionType.CREATE
        description = f"Created category '{instance.name}'"
    else:
        action = ActivityLog.ActionType.UPDATE
        description = f"Updated category '{instance.name}'"

    ActivityLog.objects.create(
        user=None,  # Categories don't have a created_by field
        project=instance.project,
        action=action,
        content_type="category",
        object_id=instance.id,
        description=description,
        metadata={"category_type": instance.category_type},
    )


@receiver(post_delete, sender=Category)
def log_category_delete(sender, instance, **kwargs):
    """Log category deletion."""
    ActivityLog.objects.create(
        user=None,
        project=instance.project,
        action=ActivityLog.ActionType.DELETE,
        content_type="category",
        object_id=instance.id,
        description=f"Deleted category '{instance.name}'",
    )


# Budget logging
@receiver(post_save, sender=Budget)
def log_budget(sender, instance, created, **kwargs):
    """Log budget creation or update."""
    if created:
        action = ActivityLog.ActionType.CREATE
        category_info = f" for {instance.category.name}" if instance.category else " (project-wide)"
        description = f"Created budget of {instance.amount}{category_info}"
    else:
        action = ActivityLog.ActionType.UPDATE
        description = f"Updated budget"

    ActivityLog.objects.create(
        user=instance.created_by,
        project=instance.project,
        action=action,
        content_type="budget",
        object_id=instance.id,
        description=description,
        metadata={
            "amount": str(instance.amount),
            "period": instance.period,
            "alert_threshold": instance.alert_threshold,
        },
    )


@receiver(post_delete, sender=Budget)
def log_budget_delete(sender, instance, **kwargs):
    """Log budget deletion."""
    ActivityLog.objects.create(
        user=None,
        project=instance.project,
        action=ActivityLog.ActionType.DELETE,
        content_type="budget",
        object_id=instance.id,
        description=f"Deleted budget",
        metadata={"amount": str(instance.amount)},
    )


# Document logging
@receiver(post_save, sender=Document)
def log_document(sender, instance, created, **kwargs):
    """Log document upload."""
    if created:
        action = ActivityLog.ActionType.CREATE
        description = f"Uploaded document '{instance.file_name}' ({instance.get_document_type_display()})"

        ActivityLog.objects.create(
            user=instance.uploaded_by,
            project=instance.transaction.project,
            action=action,
            content_type="document",
            object_id=instance.id,
            description=description,
            metadata={
                "file_name": instance.file_name,
                "file_size": instance.file_size,
                "document_type": instance.document_type,
                "transaction_id": str(instance.transaction.id),
            },
        )


@receiver(post_delete, sender=Document)
def log_document_delete(sender, instance, **kwargs):
    """Log document deletion."""
    ActivityLog.objects.create(
        user=None,
        project=instance.transaction.project,
        action=ActivityLog.ActionType.DELETE,
        content_type="document",
        object_id=instance.id,
        description=f"Deleted document '{instance.file_name}'",
    )


# Project logging
@receiver(post_save, sender=Project)
def log_project(sender, instance, created, **kwargs):
    """Log project creation or update."""
    if created:
        action = ActivityLog.ActionType.CREATE
        description = f"Created {instance.get_project_type_display()} project '{instance.name}'"
    else:
        action = ActivityLog.ActionType.UPDATE
        description = f"Updated project '{instance.name}'"

    ActivityLog.objects.create(
        user=instance.owner,
        project=instance,
        action=action,
        content_type="project",
        object_id=instance.id,
        description=description,
        metadata={
            "project_type": instance.project_type,
            "currency": instance.currency,
        },
    )


@receiver(post_delete, sender=Project)
def log_project_delete(sender, instance, **kwargs):
    """Log project deletion."""
    # Note: Project can't be logged after deletion since we need the project reference
    pass


# ProjectMember logging
@receiver(post_save, sender=ProjectMember)
def log_project_member(sender, instance, created, **kwargs):
    """Log member addition or role change."""
    if created:
        action = ActivityLog.ActionType.CREATE
        description = f"Added {instance.user.email} as {instance.get_role_display()}"
    else:
        action = ActivityLog.ActionType.UPDATE
        description = f"Updated {instance.user.email} role to {instance.get_role_display()}"

    ActivityLog.objects.create(
        user=None,
        project=instance.project,
        action=action,
        content_type="project_member",
        object_id=instance.id,
        description=description,
        metadata={
            "user_email": instance.user.email,
            "role": instance.role,
        },
    )


@receiver(post_delete, sender=ProjectMember)
def log_project_member_delete(sender, instance, **kwargs):
    """Log member removal."""
    ActivityLog.objects.create(
        user=None,
        project=instance.project,
        action=ActivityLog.ActionType.DELETE,
        content_type="project_member",
        object_id=instance.id,
        description=f"Removed {instance.user.email} from project",
        metadata={"user_email": instance.user.email},
    )


# Invitation logging
@receiver(post_save, sender=Invitation)
def log_invitation(sender, instance, created, **kwargs):
    """Log invitation creation or status change."""
    if created:
        action = ActivityLog.ActionType.INVITE
        description = f"Invited {instance.email} as {instance.get_role_display()}"
    else:
        action = ActivityLog.ActionType.UPDATE
        if instance.status == Invitation.Status.ACCEPTED:
            description = f"{instance.email} accepted invitation"
        elif instance.status == Invitation.Status.DECLINED:
            description = f"{instance.email} declined invitation"
        else:
            description = f"Updated invitation for {instance.email}"

    ActivityLog.objects.create(
        user=instance.invited_by if created else None,
        project=instance.project,
        action=action,
        content_type="invitation",
        object_id=instance.id,
        description=description,
        metadata={
            "email": instance.email,
            "status": instance.status,
            "role": instance.role,
        },
    )
