#!/usr/bin/env python
"""
Standalone seed data generation script for the Expense Tracker application.

This script can be run independently without Django management commands.

Usage:
    python seed_data.py [--clear] [--volume {light,medium,heavy}]

Examples:
    python seed_data.py                    # Generate medium data
    python seed_data.py --clear            # Clear and generate medium data
    python seed_data.py --volume heavy     # Generate heavy data
    python seed_data.py --clear --volume light  # Clear and generate light data
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Tuple

# Setup Django before importing models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

# Now import Django dependencies
from django.utils import timezone
from django.db import transaction as db_transaction

from apps.authentication.tests.factories import UserFactory, VerifiedUserFactory
from apps.projects.tests.factories import ProjectFactory, ProjectMemberFactory, InvitationFactory
from apps.transactions.tests.factories import CategoryFactory, TransactionFactory
from apps.budgets.tests.factories import BudgetFactory, BudgetWithCategoryFactory
from apps.documents.tests.factories import DocumentFactory

from apps.projects.models import Project, ProjectMember, Invitation
from apps.transactions.models import Category, Transaction
from apps.budgets.models import Budget
from apps.documents.models import Document


class SeedDataGenerator:
    """Generate comprehensive seed data for testing."""

    def __init__(self, clear: bool = False, volume: str = "medium"):
        self.clear = clear
        self.volume = volume
        self.stats = {
            "users": 0,
            "projects": 0,
            "categories": 0,
            "transactions": 0,
            "budgets": 0,
            "documents": 0,
            "project_members": 0,
            "invitations": 0,
        }

        # Define data volumes
        self.volumes = {
            "light": {
                "users": 5,
                "projects_per_user": 2,
                "transactions_per_project": 15,
                "team_members": 1,
                "budgets_per_project": 2,
                "documents_ratio": 0.3,
            },
            "medium": {
                "users": 15,
                "projects_per_user": 2,
                "transactions_per_project": 20,
                "team_members": 2,
                "budgets_per_project": 3,
                "documents_ratio": 0.4,
            },
            "heavy": {
                "users": 50,
                "projects_per_user": 3,
                "transactions_per_project": 25,
                "team_members": 3,
                "budgets_per_project": 4,
                "documents_ratio": 0.5,
            },
        }

        self.config = self.volumes[volume]

    def run(self):
        """Execute the seed data generation."""
        print(f"\n{'=' * 60}")
        print(f"Seed Data Generation - {self.volume.upper()} Volume")
        print(f"{'=' * 60}\n")

        if self.clear:
            print("⚠️  Clearing existing data...")
            self._clear_data()
            print("✓ Data cleared.\n")

        print(f"Starting {self.volume} seed data generation...\n")

        with db_transaction.atomic():
            # 1. Create users
            print("→ Creating users...")
            users = self._create_users(self.config["users"])
            self.stats["users"] = len(users)
            print(f"✓ Created {len(users)} users\n")

            # 2. Create projects
            print("→ Creating projects...")
            projects = self._create_projects(users, self.config)
            self.stats["projects"] = len(projects)
            print(f"✓ Created {len(projects)} projects\n")

            # 3. Create categories
            print("→ Creating categories...")
            categories = self._create_categories(projects)
            self.stats["categories"] = len(categories)
            print(f"✓ Created {len(categories)} categories\n")

            # 4. Create transactions
            print("→ Creating transactions...")
            transactions = self._create_transactions(projects, categories, self.config)
            self.stats["transactions"] = len(transactions)
            print(f"✓ Created {len(transactions)} transactions\n")

            # 5. Create budgets
            print("→ Creating budgets...")
            budgets = self._create_budgets(projects, categories, self.config)
            self.stats["budgets"] = len(budgets)
            print(f"✓ Created {len(budgets)} budgets\n")

            # 6. Create documents
            print("→ Creating documents...")
            documents = self._create_documents(transactions, self.config)
            self.stats["documents"] = len(documents)
            print(f"✓ Created {len(documents)} documents\n")

            # 7. Create project members and invitations
            print("→ Creating project members and invitations...")
            members, invitations = self._create_team_members(projects, users, self.config)
            self.stats["project_members"] = len(members)
            self.stats["invitations"] = len(invitations)
            print(f"✓ Created {len(members)} project members and {len(invitations)} invitations\n")

        self._print_summary()

    def _clear_data(self):
        """Clear all relevant data."""
        from django.core.management import call_command
        call_command("flush", "--no-input", verbosity=0)

    def _create_users(self, count: int) -> List:
        """Create test users."""
        from apps.authentication.models import User

        users = []
        timezones = ["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"]
        currencies = ["USD", "EUR", "GBP", "JPY"]

        for i in range(count):
            email = f"user{i+1}@testexp.com"

            # Check if user already exists
            existing_user = User.objects.filter(email=email).first()
            if existing_user:
                users.append(existing_user)
                continue

            if i < count * 0.7:  # 70% verified
                user = VerifiedUserFactory(
                    email=email,
                    first_name=f"User{i+1}",
                    currency_preference=currencies[i % len(currencies)],
                    timezone=timezones[i % len(timezones)],
                )
            else:
                user = UserFactory(email=email)
            users.append(user)

        return users

    def _create_projects(self, users: List, config: dict) -> List:
        """Create projects for users."""
        projects = []
        project_types = [Project.ProjectType.PERSONAL, Project.ProjectType.BUSINESS, Project.ProjectType.TEAM]
        currencies = ["USD", "EUR", "GBP", "JPY"]

        for user in users:
            for j in range(config["projects_per_user"]):
                project_type = project_types[(hash(str(user.id) + str(j)) % len(project_types))]
                project = ProjectFactory(
                    owner=user,
                    name=f"{user.first_name}'s {project_type.title()} Project {j+1}",
                    project_type=project_type,
                    is_active=True if j < config["projects_per_user"] - 1 else (True if j % 2 == 0 else False),
                    currency=currencies[(hash(str(user.id) + str(j)) % len(currencies))],
                    budget=Decimal(str(1000 + (j * 500))) if project_type != Project.ProjectType.PERSONAL else None,
                )
                projects.append(project)

        return projects

    def _create_categories(self, projects: List) -> List:
        """Create categories for projects."""
        categories = []

        # Default expense categories
        expense_categories = [
            ("Groceries", "shopping-bag"),
            ("Transport", "car"),
            ("Utilities", "zap"),
            ("Entertainment", "film"),
            ("Dining Out", "utensils"),
            ("Shopping", "shopping-cart"),
            ("Healthcare", "heart"),
            ("Insurance", "shield"),
            ("Rent/Mortgage", "home"),
            ("Gym", "activity"),
        ]

        # Default income categories
        income_categories = [
            ("Salary", "briefcase"),
            ("Freelance", "code"),
            ("Investment", "trending-up"),
            ("Bonus", "gift"),
        ]

        # Create default categories (not tied to projects)
        for name, icon in expense_categories + income_categories:
            cat_type = Category.CategoryType.INCOME if name in [c[0] for c in income_categories] else Category.CategoryType.EXPENSE
            category = CategoryFactory(
                name=name,
                icon=icon,
                category_type=cat_type,
                project=None,
                is_default=True,
            )
            categories.append(category)

        # Create project-specific categories
        for project in projects[:len(projects) // 2]:  # Only some projects get custom categories
            for idx, (name, icon) in enumerate(expense_categories[:3]):  # A few custom ones per project
                category = CategoryFactory(
                    name=f"{name} ({project.name[:10]})",
                    icon=icon,
                    category_type=Category.CategoryType.EXPENSE,
                    project=project,
                    is_default=False,
                )
                categories.append(category)

        return categories

    def _create_transactions(self, projects: List, categories: List, config: dict) -> List:
        """Create transactions with realistic data spread across months."""
        transactions = []
        now = timezone.now()
        months_back = 6

        for project in projects:
            project_categories = [c for c in categories if c.project_id is None or c.project_id == project.id]

            for month_offset in range(months_back):
                for idx in range(config["transactions_per_project"]):
                    # Create date scattered across the month
                    days_offset = month_offset * 30 + (hash(str(idx)) % 28)
                    transaction_date = (now - timedelta(days=days_offset)).date()

                    transaction_type = Transaction.TransactionType.EXPENSE if idx % 4 != 0 else Transaction.TransactionType.INCOME
                    amount = Decimal(str(10 + (hash(str(idx * month_offset)) % 500)))

                    transaction = TransactionFactory(
                        project=project,
                        category=project_categories[idx % len(project_categories)],
                        transaction_type=transaction_type,
                        amount=amount,
                        date=transaction_date,
                        payment_method=[
                            Transaction.PaymentMethod.CASH,
                            Transaction.PaymentMethod.CARD,
                            Transaction.PaymentMethod.BANK_TRANSFER,
                            Transaction.PaymentMethod.MOBILE_PAYMENT,
                        ][idx % 4],
                        created_by=project.owner,
                        tags=["test", "seed"] if idx % 5 == 0 else ["seed"],
                    )
                    transactions.append(transaction)

        return transactions

    def _create_budgets(self, projects: List, categories: List, config: dict) -> List:
        """Create budgets with realistic periods and alert thresholds."""
        budgets = []
        now = timezone.now()

        periods = [Budget.Period.WEEKLY, Budget.Period.MONTHLY, Budget.Period.QUARTERLY, Budget.Period.YEARLY]

        for project in projects:
            project_categories = [c for c in categories if c.project_id == project.id]

            for idx in range(config["budgets_per_project"]):
                period = periods[idx % len(periods)]

                if period == Budget.Period.WEEKLY:
                    days = 7
                elif period == Budget.Period.MONTHLY:
                    days = 30
                elif period == Budget.Period.QUARTERLY:
                    days = 90
                else:
                    days = 365

                # Some budgets for all categories, some for specific categories
                if idx % 2 == 0 and project_categories:
                    budget = BudgetWithCategoryFactory(
                        project=project,
                        category=project_categories[idx % len(project_categories)],
                        amount=Decimal(str(500 + idx * 100)),
                        period=period,
                        start_date=now.date(),
                        end_date=(now + timedelta(days=days)).date(),
                        alert_threshold=[70, 80, 90][idx % 3],
                        created_by=project.owner,
                    )
                else:
                    budget = BudgetFactory(
                        project=project,
                        amount=Decimal(str(2000 + idx * 500)),
                        period=period,
                        start_date=now.date(),
                        end_date=(now + timedelta(days=days)).date(),
                        alert_threshold=[70, 80, 90][idx % 3],
                        created_by=project.owner,
                    )
                budgets.append(budget)

        return budgets

    def _create_documents(self, transactions: List, config: dict) -> List:
        """Create documents for some transactions."""
        documents = []
        doc_count = int(len(transactions) * config["documents_ratio"])

        for transaction in transactions[:doc_count]:
            doc_types = [
                Document.DocumentType.RECEIPT,
                Document.DocumentType.INVOICE,
                Document.DocumentType.CONTRACT,
            ]
            document = DocumentFactory(
                transaction=transaction,
                document_type=doc_types[hash(str(transaction.id)) % len(doc_types)],
                uploaded_by=transaction.created_by,
            )
            documents.append(document)

        return documents

    def _create_team_members(self, projects: List, users: List, config: dict) -> Tuple[List, List]:
        """Create team members and invitations for projects."""
        members = []
        invitations = []

        # Filter for team projects
        team_projects = [p for p in projects if p.project_type == Project.ProjectType.TEAM]

        for project in team_projects:
            # Add some users as members
            available_users = [u for u in users if u.id != project.owner.id]
            for i in range(min(config["team_members"], len(available_users))):
                roles = [ProjectMember.Role.ADMIN, ProjectMember.Role.MEMBER, ProjectMember.Role.VIEWER]
                member = ProjectMemberFactory(
                    project=project,
                    user=available_users[i],
                    role=roles[i % len(roles)],
                )
                members.append(member)

            # Create some pending invitations
            for i in range(config["team_members"]):
                invitation = InvitationFactory(
                    project=project,
                    email=f"invited{i}+{project.id}@testexp.com",
                    role=ProjectMember.Role.MEMBER,
                    invited_by=project.owner,
                    status=[Invitation.Status.PENDING, Invitation.Status.ACCEPTED][i % 2],
                    expires_at=timezone.now() + timedelta(days=7 if i % 2 == 0 else -1),
                )
                invitations.append(invitation)

        return members, invitations

    def _print_summary(self):
        """Print a summary of the seeded data."""
        print("=" * 60)
        print("SEED DATA GENERATION COMPLETE")
        print("=" * 60)
        print(f"Users created:              {self.stats['users']}")
        print(f"Projects created:           {self.stats['projects']}")
        print(f"Categories created:         {self.stats['categories']}")
        print(f"Transactions created:       {self.stats['transactions']}")
        print(f"Budgets created:            {self.stats['budgets']}")
        print(f"Documents created:          {self.stats['documents']}")
        print(f"Project members created:    {self.stats['project_members']}")
        print(f"Invitations created:        {self.stats['invitations']}")
        print("=" * 60)
        print("\nYou can now use the following test users:")
        print("  Email pattern: user{1..N}@testexp.com")
        print("  Password: Str0ngPass!")
        print("=" * 60 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Seed the expense tracker database with test data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python seed_data.py                         # Generate medium volume data
  python seed_data.py --clear                 # Clear and generate medium data
  python seed_data.py --volume heavy          # Generate heavy volume data
  python seed_data.py --clear --volume light  # Clear and generate light data
        """,
    )

    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear all existing data before seeding",
    )
    parser.add_argument(
        "--volume",
        type=str,
        choices=["light", "medium", "heavy"],
        default="medium",
        help="Volume of data to generate (default: medium)",
    )

    args = parser.parse_args()

    generator = SeedDataGenerator(clear=args.clear, volume=args.volume)
    try:
        generator.run()
    except Exception as e:
        print(f"\n❌ Error during seed generation: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
