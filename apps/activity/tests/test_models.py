import uuid

import pytest
from decimal import Decimal

from apps.activity.models import ActivityLog
from apps.authentication.tests.factories import UserFactory
from apps.projects.tests.factories import ProjectFactory
from apps.transactions.tests.factories import TransactionFactory, CategoryFactory
from apps.budgets.tests.factories import BudgetFactory
from apps.documents.tests.factories import DocumentFactory


@pytest.mark.django_db
class TestActivityLogModel:
    """Test ActivityLog model functionality."""

    def test_create_activity_log(self):
        """Test creating an activity log entry."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        log = ActivityLog.objects.create(
            user=user,
            project=project,
            action=ActivityLog.ActionType.CREATE,
            content_type="transaction",
            object_id=uuid.uuid4(),
            description="Created transaction",
        )

        assert log.pk is not None
        assert log.user == user
        assert log.project == project
        assert log.action == ActivityLog.ActionType.CREATE

    def test_activity_log_ordering(self):
        """Test that activity logs are ordered by created_at descending."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        log1 = ActivityLog.objects.create(
            user=user,
            project=project,
            action=ActivityLog.ActionType.CREATE,
            content_type="transaction",
            object_id=uuid.uuid4(),
            description="Log 1",
        )
        log2 = ActivityLog.objects.create(
            user=user,
            project=project,
            action=ActivityLog.ActionType.UPDATE,
            content_type="transaction",
            object_id=uuid.uuid4(),
            description="Log 2",
        )

        logs = ActivityLog.objects.filter(project=project)
        assert logs[0].id == log2.id  # Most recent first
        assert logs[1].id == log1.id

    def test_activity_log_uuid_primary_key(self):
        """Test that ActivityLog has UUID primary key."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        log = ActivityLog.objects.create(
            user=user,
            project=project,
            action=ActivityLog.ActionType.CREATE,
            content_type="transaction",
            object_id=uuid.uuid4(),
            description="Test",
        )

        assert isinstance(log.pk, uuid.UUID)

    def test_activity_log_null_user(self):
        """Test that user can be null for system actions."""
        project = ProjectFactory()

        log = ActivityLog.objects.create(
            user=None,
            project=project,
            action=ActivityLog.ActionType.DELETE,
            content_type="transaction",
            object_id=uuid.uuid4(),
            description="System deleted transaction",
        )

        assert log.user is None

    def test_activity_log_with_changes(self):
        """Test storing changes in activity log."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        changes = {
            "amount": {"old": "100.00", "new": "150.00"},
            "description": {"old": "old desc", "new": "new desc"},
        }

        log = ActivityLog.objects.create(
            user=user,
            project=project,
            action=ActivityLog.ActionType.UPDATE,
            content_type="transaction",
            object_id=uuid.uuid4(),
            description="Updated transaction",
            changes=changes,
        )

        assert log.changes == changes

    def test_activity_log_with_metadata(self):
        """Test storing metadata in activity log."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        metadata = {
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0...",
        }

        log = ActivityLog.objects.create(
            user=user,
            project=project,
            action=ActivityLog.ActionType.CREATE,
            content_type="transaction",
            object_id=uuid.uuid4(),
            description="Created transaction",
            metadata=metadata,
        )

        assert log.metadata == metadata

    def test_activity_log_str(self):
        """Test string representation of activity log."""
        user = UserFactory(email="test@example.com")
        project = ProjectFactory(owner=user)

        log = ActivityLog.objects.create(
            user=user,
            project=project,
            action=ActivityLog.ActionType.CREATE,
            content_type="transaction",
            object_id=uuid.uuid4(),
            description="Test",
        )

        assert "Created" in str(log)
        assert "transaction" in str(log)


@pytest.mark.django_db
class TestActivityLogSignals:
    """Test automatic activity logging via signals."""

    def test_transaction_create_logged(self):
        """Test that transaction creation is logged."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        category = CategoryFactory(project=project)

        TransactionFactory(
            project=project,
            category=category,
            amount=Decimal("100.00"),
            created_by=user,
        )

        log = ActivityLog.objects.filter(
            project=project, content_type="transaction"
        ).first()

        assert log is not None
        assert log.action == ActivityLog.ActionType.CREATE
        assert log.user == user

    def test_transaction_delete_logged(self):
        """Test that transaction deletion is logged."""
        user = UserFactory()
        project = ProjectFactory(owner=user)
        transaction = TransactionFactory(project=project, created_by=user)

        transaction_id = transaction.id
        transaction.delete()

        log = ActivityLog.objects.filter(
            project=project,
            content_type="transaction",
            action=ActivityLog.ActionType.DELETE,
        ).first()

        assert log is not None
        assert log.object_id == transaction_id

    def test_budget_create_logged(self):
        """Test that budget creation is logged."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        BudgetFactory(project=project, created_by=user)

        log = ActivityLog.objects.filter(
            project=project, content_type="budget"
        ).first()

        assert log is not None
        assert log.action == ActivityLog.ActionType.CREATE

    def test_category_create_logged(self):
        """Test that category creation is logged."""
        project = ProjectFactory()

        CategoryFactory(project=project)

        log = ActivityLog.objects.filter(
            project=project, content_type="category"
        ).first()

        assert log is not None
        assert log.action == ActivityLog.ActionType.CREATE

    def test_category_delete_logged(self):
        """Test that category deletion is logged."""
        project = ProjectFactory()
        category = CategoryFactory(project=project)

        category_id = category.id
        category.delete()

        log = ActivityLog.objects.filter(
            project=project,
            content_type="category",
            action=ActivityLog.ActionType.DELETE,
        ).first()

        assert log is not None
        assert log.object_id == category_id

    def test_activity_log_filtering_by_action(self):
        """Test filtering activity logs by action type."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        TransactionFactory(project=project, created_by=user)
        TransactionFactory(project=project, created_by=user)

        creates = ActivityLog.objects.filter(
            project=project,
            action=ActivityLog.ActionType.CREATE,
        )

        assert creates.count() >= 2

    def test_activity_log_filtering_by_content_type(self):
        """Test filtering activity logs by content type."""
        user = UserFactory()
        project = ProjectFactory(owner=user)

        TransactionFactory(project=project, created_by=user)
        BudgetFactory(project=project, created_by=user)

        transactions = ActivityLog.objects.filter(
            project=project, content_type="transaction"
        )
        budgets = ActivityLog.objects.filter(project=project, content_type="budget")

        assert transactions.count() >= 1
        assert budgets.count() >= 1

    def test_activity_log_filtering_by_user(self):
        """Test filtering activity logs by user."""
        user1 = UserFactory()
        user2 = UserFactory()
        project = ProjectFactory(owner=user1)

        TransactionFactory(project=project, created_by=user1)
        TransactionFactory(project=project, created_by=user2)

        user1_logs = ActivityLog.objects.filter(project=project, user=user1)
        user2_logs = ActivityLog.objects.filter(project=project, user=user2)

        assert user1_logs.count() >= 1
        assert user2_logs.count() >= 1
