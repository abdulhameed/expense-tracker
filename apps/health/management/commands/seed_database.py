"""
Django management command to seed the database with realistic test data.

Usage:
    python manage.py seed_database [--clear] [--volume {light,medium,heavy}]

Examples:
    python manage.py seed_database                    # Medium data, keep existing
    python manage.py seed_database --clear            # Medium data, clear first
    python manage.py seed_database --volume heavy     # Heavy data, keep existing
    python manage.py seed_database --clear --volume light  # Light data, clear first
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List

from django.core.management.base import BaseCommand, CommandError
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


class Command(BaseCommand):
    help = "Seed the database with comprehensive test data"

    def add_arguments(self, parser):
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

    def handle(self, *args, **options):
        clear = options["clear"]
        volume = options["volume"]

        # Define data volumes
        volumes = {
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

        config = volumes[volume]

        if clear:
            self.stdout.write(self.style.WARNING("Clearing existing data..."))
            self._clear_data()
            self.stdout.write(self.style.SUCCESS("Data cleared."))

        self.stdout.write(self.style.SUCCESS(f"\nStarting {volume} seed data generation...\n"))

        with db_transaction.atomic():
            stats = {
                "users": 0,
                "projects": 0,
                "categories": 0,
                "transactions": 0,
                "budgets": 0,
                "documents": 0,
                "project_members": 0,
                "invitations": 0,
            }

            # 1. Create users
            self.stdout.write("Creating users...")
            users = self._create_users(config["users"])
            stats["users"] = len(users)
            self.stdout.write(self.style.SUCCESS(f"✓ Created {len(users)} users"))

            # 2. Create projects and categories
            self.stdout.write("Creating projects...")
            projects = self._create_projects(users, config)
            stats["projects"] = len(projects)
            self.stdout.write(self.style.SUCCESS(f"✓ Created {len(projects)} projects"))

            # 3. Create default categories
            self.stdout.write("Creating categories...")
            categories = self._create_categories(projects)
            stats["categories"] = len(categories)
            self.stdout.write(self.style.SUCCESS(f"✓ Created {len(categories)} categories"))

            # 4. Create transactions
            self.stdout.write("Creating transactions...")
            transactions = self._create_transactions(projects, categories, config)
            stats["transactions"] = len(transactions)
            self.stdout.write(self.style.SUCCESS(f"✓ Created {len(transactions)} transactions"))

            # 5. Create budgets
            self.stdout.write("Creating budgets...")
            budgets = self._create_budgets(projects, categories, config)
            stats["budgets"] = len(budgets)
            self.stdout.write(self.style.SUCCESS(f"✓ Created {len(budgets)} budgets"))

            # 6. Create documents
            self.stdout.write("Creating documents...")
            documents = self._create_documents(transactions, config)
            stats["documents"] = len(documents)
            self.stdout.write(self.style.SUCCESS(f"✓ Created {len(documents)} documents"))

            # 7. Add team members and invitations
            self.stdout.write("Creating project members and invitations...")
            members, invitations = self._create_team_members(projects, users, config)
            stats["project_members"] = len(members)
            stats["invitations"] = len(invitations)
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Created {len(members)} project members and {len(invitations)} invitations"
                )
            )

        # Print summary
        self._print_summary(stats)

    def _clear_data(self):
        """Clear all relevant data from the database."""
        from django.core.management import call_command
        call_command("flush", "--no-input")

    def _create_users(self, count: int) -> List:
        """Create test users."""
        from apps.authentication.models import User

        users = []
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
                    currency_preference=["USD", "EUR", "GBP", "JPY"][i % 4],
                    timezone=["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"][i % 4],
                )
            else:
                user = UserFactory(email=email)
            users.append(user)
        return users

    def _create_projects(self, users: List, config: dict) -> List:
        """Create projects for users."""
        projects = []
        project_types = [Project.ProjectType.PERSONAL, Project.ProjectType.BUSINESS, Project.ProjectType.TEAM]

        for user in users:
            for j in range(config["projects_per_user"]):
                project_type = project_types[(user.id.int + j) % len(project_types)]
                project = ProjectFactory(
                    owner=user,
                    name=f"{user.first_name}'s {project_type.title()} Project {j+1}",
                    project_type=project_type,
                    is_active=True if j < config["projects_per_user"] - 1 else (True if j % 2 == 0 else False),
                    currency=["USD", "EUR", "GBP", "JPY"][(user.id.int + j) % 4],
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
            for name, icon in expense_categories[:3]:  # A few custom ones per project
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
                for _ in range(config["transactions_per_project"]):
                    # Create date scattered across the month
                    days_offset = month_offset * 30 + (hash(str(_)) % 28)
                    transaction_date = (now - timedelta(days=days_offset)).date()

                    transaction_type = Transaction.TransactionType.EXPENSE if _ % 4 != 0 else Transaction.TransactionType.INCOME
                    amount = Decimal(str(10 + (hash(str(_ * month_offset)) % 500)))

                    transaction = TransactionFactory(
                        project=project,
                        category=project_categories[_ % len(project_categories)],
                        transaction_type=transaction_type,
                        amount=amount,
                        date=transaction_date,
                        payment_method=[
                            Transaction.PaymentMethod.CASH,
                            Transaction.PaymentMethod.CARD,
                            Transaction.PaymentMethod.BANK_TRANSFER,
                            Transaction.PaymentMethod.MOBILE_PAYMENT,
                        ][_ % 4],
                        created_by=project.owner,
                        tags=["test", "seed"] if _ % 5 == 0 else ["seed"],
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

    def _create_team_members(self, projects: List, users: List, config: dict) -> tuple:
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

    def _print_summary(self, stats: dict):
        """Print a summary of the seeded data."""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("SEED DATA GENERATION COMPLETE"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"Users created:              {stats['users']}")
        self.stdout.write(f"Projects created:          {stats['projects']}")
        self.stdout.write(f"Categories created:        {stats['categories']}")
        self.stdout.write(f"Transactions created:      {stats['transactions']}")
        self.stdout.write(f"Budgets created:           {stats['budgets']}")
        self.stdout.write(f"Documents created:         {stats['documents']}")
        self.stdout.write(f"Project members created:   {stats['project_members']}")
        self.stdout.write(f"Invitations created:       {stats['invitations']}")
        self.stdout.write("=" * 60)
        self.stdout.write("\nYou can now use the following test users:")
        self.stdout.write("  Email pattern: user{1..N}@testexp.com")
        self.stdout.write("  Password: Str0ngPass!")
        self.stdout.write("=" * 60 + "\n")
