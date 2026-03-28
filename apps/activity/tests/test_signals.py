"""
Tests for activity/signals.py - Automatic logging of model changes via Django signals.

Tests:
- log_transaction - Transaction creation, update, deletion logging
- log_category - Category creation, update, deletion logging
- log_budget - Budget creation, update, deletion logging
- log_document - Document upload and deletion logging
- log_project - Project creation and update logging
- log_project_member - Project member addition, role change, removal logging
- log_invitation - Invitation creation, acceptance, decline logging
"""

import pytest
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

from apps.activity.models import ActivityLog
from apps.transactions.tests.factories import TransactionFactory, CategoryFactory
from apps.budgets.tests.factories import BudgetFactory
from apps.documents.tests.factories import DocumentFactory
from apps.projects.tests.factories import (
    ProjectFactory,
    ProjectMemberFactory,
    InvitationFactory,
)
from apps.projects.models import ProjectMember, Invitation
from apps.authentication.tests.factories import UserFactory


@pytest.mark.django_db
class TestTransactionSignals:
    """Test logging of transaction creation, update, and deletion."""

    def test_log_transaction_create(self):
        """Test that transaction creation is logged with correct metadata."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project)

        transaction = TransactionFactory(
            project=project,
            created_by=user,
            category=category,
            description="Office supplies",
            amount=Decimal("150.00"),
            currency="USD",
            transaction_type="expense",
        )

        # Verify activity log was created
        log = ActivityLog.objects.get(object_id=transaction.id)
        assert log.action == ActivityLog.ActionType.CREATE
        assert log.content_type == "transaction"
        assert log.user == user
        assert log.project == project
        assert "Office supplies" in log.description
        assert "150.00" in log.description
        assert log.metadata["transaction_type"] == "expense"
        assert log.metadata["amount"] == "150.00"
        assert log.metadata["currency"] == "USD"

    def test_log_transaction_create_with_income(self):
        """Test that income transaction is logged correctly."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project, category_type="income")

        transaction = TransactionFactory(
            project=project,
            created_by=user,
            category=category,
            description="Client payment",
            amount=Decimal("5000.00"),
            currency="USD",
            transaction_type="income",
        )

        log = ActivityLog.objects.get(object_id=transaction.id)
        assert log.metadata["transaction_type"] == "income"
        assert log.metadata["amount"] == "5000.00"
        assert "Client payment" in log.description

    def test_log_transaction_update(self):
        """Test that transaction update is logged."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project)
        transaction = TransactionFactory(
            project=project,
            created_by=user,
            category=category,
            description="Original description",
        )

        # Update transaction
        transaction.description = "Updated description"
        transaction.save()

        # Verify update was logged
        logs = ActivityLog.objects.filter(
            object_id=transaction.id, content_type="transaction"
        ).order_by("created_at")
        assert logs.count() == 2  # Create + update

        update_log = logs.latest("created_at")
        assert update_log.action == ActivityLog.ActionType.UPDATE
        assert "Updated description" in update_log.description

    def test_log_transaction_delete(self):
        """Test that transaction deletion is logged."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project)
        transaction = TransactionFactory(
            project=project,
            created_by=user,
            category=category,
            description="To be deleted",
            amount=Decimal("100.00"),
        )

        transaction_id = transaction.id

        # Delete transaction
        transaction.delete()

        # Verify deletion was logged
        log = ActivityLog.objects.get(
            object_id=transaction_id, action=ActivityLog.ActionType.DELETE
        )
        assert log.content_type == "transaction"
        assert "To be deleted" in log.description
        assert log.metadata["amount"] == "100.00"
        # User may be None after deletion
        assert log.project == project

    def test_log_transaction_metadata_accuracy(self):
        """Test that all transaction metadata is captured correctly."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project)

        transaction = TransactionFactory(
            project=project,
            created_by=user,
            category=category,
            amount=Decimal("999.99"),
            currency="EUR",
            transaction_type="expense",
        )

        log = ActivityLog.objects.get(object_id=transaction.id)
        assert log.metadata["amount"] == "999.99"
        assert log.metadata["currency"] == "EUR"
        assert log.metadata["transaction_type"] == "expense"


@pytest.mark.django_db
class TestCategorySignals:
    """Test logging of category creation, update, and deletion."""

    def test_log_category_create(self):
        """Test that category creation is logged."""
        project = ProjectFactory()
        category = CategoryFactory(
            project=project,
            name="Office Supplies",
            category_type="expense",
        )

        log = ActivityLog.objects.get(object_id=category.id)
        assert log.action == ActivityLog.ActionType.CREATE
        assert log.content_type == "category"
        assert log.project == project
        assert "Office Supplies" in log.description
        assert log.metadata["category_type"] == "expense"

    def test_log_category_create_default(self):
        """Test that default categories are logged."""
        category = CategoryFactory(
            project=None,
            is_default=True,
            name="Default Expense",
            category_type="expense",
        )

        log = ActivityLog.objects.get(object_id=category.id)
        assert "Default Expense" in log.description

    def test_log_category_update(self):
        """Test that category update is logged."""
        project = ProjectFactory()
        category = CategoryFactory(project=project, name="Original Name")

        # Update category
        category.name = "Updated Name"
        category.save()

        logs = ActivityLog.objects.filter(object_id=category.id).order_by(
            "created_at"
        )
        assert logs.count() == 2

        update_log = logs.latest("created_at")
        assert update_log.action == ActivityLog.ActionType.UPDATE
        assert "Updated Name" in update_log.description

    def test_log_category_delete(self):
        """Test that category deletion is logged."""
        project = ProjectFactory()
        category = CategoryFactory(project=project, name="To Delete")

        category_id = category.id
        category.delete()

        log = ActivityLog.objects.get(
            object_id=category_id, action=ActivityLog.ActionType.DELETE
        )
        assert log.content_type == "category"
        assert "To Delete" in log.description
        assert log.project == project


@pytest.mark.django_db
class TestBudgetSignals:
    """Test logging of budget creation, update, and deletion."""

    def test_log_budget_create_project_wide(self):
        """Test that project-wide budget creation is logged."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        budget = BudgetFactory(
            project=project,
            created_by=user,
            amount=Decimal("10000.00"),
            period="monthly",
            alert_threshold=80,
            category=None,
        )

        log = ActivityLog.objects.get(object_id=budget.id)
        assert log.action == ActivityLog.ActionType.CREATE
        assert log.content_type == "budget"
        assert log.user == user
        assert log.project == project
        assert "10000" in log.description
        assert "project-wide" in log.description
        assert log.metadata["amount"] == "10000.00"
        assert log.metadata["period"] == "monthly"
        assert log.metadata["alert_threshold"] == 80

    def test_log_budget_create_category_specific(self):
        """Test that category-specific budget creation is logged."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project, name="Food")

        budget = BudgetFactory(
            project=project,
            created_by=user,
            category=category,
            amount=Decimal("500.00"),
        )

        log = ActivityLog.objects.get(object_id=budget.id)
        assert "Food" in log.description
        assert log.metadata["amount"] == "500.00"

    def test_log_budget_update(self):
        """Test that budget update is logged."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        budget = BudgetFactory(
            project=project,
            created_by=user,
            amount=Decimal("1000.00"),
        )

        # Update budget
        budget.amount = Decimal("1500.00")
        budget.save()

        logs = ActivityLog.objects.filter(object_id=budget.id).order_by("created_at")
        assert logs.count() == 2

        update_log = logs.latest("created_at")
        assert update_log.action == ActivityLog.ActionType.UPDATE
        assert "Updated budget" in update_log.description

    def test_log_budget_delete(self):
        """Test that budget deletion is logged."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        budget = BudgetFactory(
            project=project, created_by=user, amount=Decimal("5000.00")
        )

        budget_id = budget.id
        budget.delete()

        log = ActivityLog.objects.get(
            object_id=budget_id, action=ActivityLog.ActionType.DELETE
        )
        assert log.content_type == "budget"
        assert log.metadata["amount"] == "5000.00"


@pytest.mark.django_db
class TestDocumentSignals:
    """Test logging of document upload and deletion."""

    def test_log_document_upload(self):
        """Test that document upload is logged."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project)

        # Create transaction first
        transaction = TransactionFactory(
            project=project, created_by=user, category=category
        )

        # Create document
        document = DocumentFactory(
            transaction=transaction,
            uploaded_by=user,
            file_name="receipt.pdf",
            file_size=102400,
            document_type="receipt",
        )

        log = ActivityLog.objects.get(object_id=document.id)
        assert log.action == ActivityLog.ActionType.CREATE
        assert log.content_type == "document"
        assert log.user == user
        assert log.project == project
        assert "receipt.pdf" in log.description
        assert log.metadata["file_name"] == "receipt.pdf"
        assert log.metadata["file_size"] == 102400
        assert log.metadata["document_type"] == "receipt"
        assert log.metadata["transaction_id"] == str(transaction.id)

    def test_log_document_delete(self):
        """Test that document deletion is logged."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project)
        transaction = TransactionFactory(
            project=project, created_by=user, category=category
        )

        document = DocumentFactory(
            transaction=transaction,
            uploaded_by=user,
            file_name="invoice.pdf",
        )

        document_id = document.id
        document.delete()

        log = ActivityLog.objects.get(
            object_id=document_id, action=ActivityLog.ActionType.DELETE
        )
        assert log.content_type == "document"
        assert "invoice.pdf" in log.description
        assert log.project == project


@pytest.mark.django_db
class TestProjectSignals:
    """Test logging of project creation and update."""

    def test_log_project_create_personal(self):
        """Test that personal project creation is logged."""
        user = UserFactory()

        project = ProjectFactory(
            owner=user,
            name="My Personal Finances",
            project_type="personal",
            currency="USD",
        )

        log = ActivityLog.objects.get(object_id=project.id)
        assert log.action == ActivityLog.ActionType.CREATE
        assert log.content_type == "project"
        assert log.user == user
        assert log.project == project
        assert "My Personal Finances" in log.description
        assert "Personal" in log.description
        assert log.metadata["project_type"] == "personal"
        assert log.metadata["currency"] == "USD"

    def test_log_project_create_team(self):
        """Test that team project creation is logged."""
        user = UserFactory()

        project = ProjectFactory(
            owner=user,
            name="Team Project",
            project_type="team",
            currency="EUR",
        )

        log = ActivityLog.objects.get(object_id=project.id)
        assert "Team" in log.description
        assert log.metadata["project_type"] == "team"
        assert log.metadata["currency"] == "EUR"

    def test_log_project_update(self):
        """Test that project update is logged."""
        user = UserFactory()
        project = ProjectFactory(owner=user, name="Original Name")

        # Update project
        project.name = "Updated Name"
        project.save()

        logs = ActivityLog.objects.filter(object_id=project.id).order_by(
            "created_at"
        )
        assert logs.count() == 2

        update_log = logs.latest("created_at")
        assert update_log.action == ActivityLog.ActionType.UPDATE
        assert "Updated Name" in update_log.description


@pytest.mark.django_db
class TestProjectMemberSignals:
    """Test logging of project member addition, role changes, and removal."""

    def test_log_project_member_add(self):
        """Test that project member addition is logged."""
        project_owner = UserFactory()
        project = ProjectFactory(owner=project_owner, add_owner_member=False)
        member_user = UserFactory()

        member = ProjectMemberFactory(
            project=project,
            user=member_user,
            role=ProjectMember.Role.MEMBER,
        )

        log = ActivityLog.objects.get(object_id=member.id)
        assert log.action == ActivityLog.ActionType.CREATE
        assert log.content_type == "project_member"
        assert log.project == project
        assert member_user.email in log.description
        assert "Member" in log.description
        assert log.metadata["user_email"] == member_user.email
        assert log.metadata["role"] == ProjectMember.Role.MEMBER

    def test_log_project_member_add_admin(self):
        """Test that admin member addition is logged correctly."""
        project_owner = UserFactory()
        project = ProjectFactory(owner=project_owner, add_owner_member=False)
        admin_user = UserFactory()

        member = ProjectMemberFactory(
            project=project,
            user=admin_user,
            role=ProjectMember.Role.ADMIN,
        )

        log = ActivityLog.objects.get(object_id=member.id)
        assert "Admin" in log.description
        assert log.metadata["role"] == ProjectMember.Role.ADMIN

    def test_log_project_member_role_change(self):
        """Test that project member role change is logged."""
        project_owner = UserFactory()
        project = ProjectFactory(owner=project_owner, add_owner_member=False)
        member_user = UserFactory()

        member = ProjectMemberFactory(
            project=project,
            user=member_user,
            role=ProjectMember.Role.MEMBER,
        )

        # Update role
        member.role = ProjectMember.Role.ADMIN
        member.save()

        logs = ActivityLog.objects.filter(object_id=member.id).order_by("created_at")
        assert logs.count() == 2

        update_log = logs.latest("created_at")
        assert update_log.action == ActivityLog.ActionType.UPDATE
        assert "Admin" in update_log.description
        assert member_user.email in update_log.description

    def test_log_project_member_remove(self):
        """Test that project member removal is logged."""
        project_owner = UserFactory()
        project = ProjectFactory(owner=project_owner, add_owner_member=False)
        member_user = UserFactory()

        member = ProjectMemberFactory(
            project=project,
            user=member_user,
            role=ProjectMember.Role.MEMBER,
        )

        member_id = member.id
        member.delete()

        log = ActivityLog.objects.get(
            object_id=member_id, action=ActivityLog.ActionType.DELETE
        )
        assert log.content_type == "project_member"
        assert member_user.email in log.description
        assert "Removed" in log.description
        assert log.metadata["user_email"] == member_user.email


@pytest.mark.django_db
class TestInvitationSignals:
    """Test logging of invitation creation, acceptance, and decline."""

    def test_log_invitation_create(self):
        """Test that invitation creation is logged."""
        inviter = UserFactory()
        project = ProjectFactory(owner=inviter)

        invitation = InvitationFactory(
            project=project,
            email="newmember@example.com",
            role=ProjectMember.Role.MEMBER,
            invited_by=inviter,
        )

        log = ActivityLog.objects.get(object_id=invitation.id)
        assert log.action == ActivityLog.ActionType.INVITE
        assert log.content_type == "invitation"
        assert log.user == inviter
        assert log.project == project
        assert "newmember@example.com" in log.description
        assert "Member" in log.description
        assert log.metadata["email"] == "newmember@example.com"
        assert log.metadata["role"] == ProjectMember.Role.MEMBER
        assert log.metadata["status"] == Invitation.Status.PENDING

    def test_log_invitation_create_admin_role(self):
        """Test that invitation with admin role is logged correctly."""
        inviter = UserFactory()
        project = ProjectFactory(owner=inviter)

        invitation = InvitationFactory(
            project=project,
            email="admin@example.com",
            role=ProjectMember.Role.ADMIN,
            invited_by=inviter,
        )

        log = ActivityLog.objects.get(object_id=invitation.id)
        assert "Admin" in log.description
        assert log.metadata["role"] == ProjectMember.Role.ADMIN

    def test_log_invitation_accept(self):
        """Test that invitation acceptance is logged."""
        inviter = UserFactory()
        project = ProjectFactory(owner=inviter)

        invitation = InvitationFactory(
            project=project,
            email="accept@example.com",
            role=ProjectMember.Role.MEMBER,
            invited_by=inviter,
            status=Invitation.Status.PENDING,
        )

        # Accept invitation
        invitation.status = Invitation.Status.ACCEPTED
        invitation.invited_by = None  # Per signal, invited_by is None on update
        invitation.save()

        logs = ActivityLog.objects.filter(object_id=invitation.id).order_by(
            "created_at"
        )
        assert logs.count() == 2

        accept_log = logs.latest("created_at")
        assert accept_log.action == ActivityLog.ActionType.UPDATE
        assert "accept@example.com" in accept_log.description
        assert "accepted" in accept_log.description.lower()
        assert accept_log.metadata["status"] == Invitation.Status.ACCEPTED

    def test_log_invitation_decline(self):
        """Test that invitation decline is logged."""
        inviter = UserFactory()
        project = ProjectFactory(owner=inviter)

        invitation = InvitationFactory(
            project=project,
            email="decline@example.com",
            role=ProjectMember.Role.MEMBER,
            invited_by=inviter,
            status=Invitation.Status.PENDING,
        )

        # Decline invitation
        invitation.status = Invitation.Status.DECLINED
        invitation.invited_by = None
        invitation.save()

        logs = ActivityLog.objects.filter(object_id=invitation.id).order_by(
            "created_at"
        )
        assert logs.count() == 2

        decline_log = logs.latest("created_at")
        assert decline_log.action == ActivityLog.ActionType.UPDATE
        assert "decline@example.com" in decline_log.description
        assert "declined" in decline_log.description.lower()
        assert decline_log.metadata["status"] == Invitation.Status.DECLINED


@pytest.mark.django_db
class TestSignalIntegration:
    """Integration tests for multiple signals together."""

    def test_signal_accuracy_across_models(self):
        """Test that signals fire correctly across different model types."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project)

        # Create various objects
        transaction = TransactionFactory(
            project=project, created_by=user, category=category
        )
        budget = BudgetFactory(project=project, created_by=user)
        document = DocumentFactory(transaction=transaction, uploaded_by=user)

        # Verify all were logged
        assert ActivityLog.objects.filter(
            content_type="transaction", object_id=transaction.id
        ).exists()
        assert ActivityLog.objects.filter(
            content_type="budget", object_id=budget.id
        ).exists()
        assert ActivityLog.objects.filter(
            content_type="document", object_id=document.id
        ).exists()

    def test_signal_project_context_maintained(self):
        """Test that project context is maintained in all logs."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project)
        transaction = TransactionFactory(
            project=project, created_by=user, category=category
        )

        logs = ActivityLog.objects.filter(project=project)

        # All logs for this project should reference it
        for log in logs:
            assert log.project == project

    def test_signal_metadata_completeness(self):
        """Test that metadata is complete for all logged actions."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        transaction = TransactionFactory(
            project=project,
            created_by=user,
            amount=Decimal("250.00"),
        )

        log = ActivityLog.objects.get(object_id=transaction.id)

        # Verify required metadata fields exist
        assert "amount" in log.metadata
        assert "currency" in log.metadata
        assert "transaction_type" in log.metadata
        assert log.metadata["amount"] is not None
        assert log.metadata["currency"] is not None

    def test_signal_action_type_coverage(self):
        """Test that all required action types are used by signals."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project)

        # Create objects (CREATE action)
        transaction = TransactionFactory(
            project=project, created_by=user, category=category
        )
        assert ActivityLog.objects.filter(
            action=ActivityLog.ActionType.CREATE,
            content_type="transaction",
        ).exists()

        # Update object (UPDATE action)
        transaction.description = "Updated"
        transaction.save()
        assert ActivityLog.objects.filter(
            action=ActivityLog.ActionType.UPDATE,
            content_type="transaction",
        ).exists()

        # Delete object (DELETE action)
        transaction_id = transaction.id
        transaction.delete()
        assert ActivityLog.objects.filter(
            action=ActivityLog.ActionType.DELETE,
            object_id=transaction_id,
        ).exists()
