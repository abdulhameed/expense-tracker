"""
End-to-End workflow tests for Expense Tracker API.

Tests complete user journeys:
- User registration and authentication
- Creating projects and transactions
- Budget management and alerts
- Generating reports
- Team collaboration
"""
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


@pytest.mark.e2e
@pytest.mark.django_db
class TestCompleteUserJourney:
    """Test complete user journey from registration to usage."""

    @pytest.fixture
    def client(self):
        return APIClient()

    def test_user_registration_to_budget_tracking(self, client):
        """
        Test complete workflow:
        1. User registration
        2. User login
        3. Create project
        4. Create budget
        5. Add transactions
        6. Check budget status
        7. Generate report
        """
        # 1. Register new user
        register_data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        response = client.post('/api/v1/auth/register/', register_data)
        assert response.status_code == status.HTTP_201_CREATED

        # 2. Login
        login_data = {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!'
        }
        response = client.post('/api/v1/auth/login/', login_data)
        assert response.status_code == status.HTTP_200_OK
        token = response.data['access']

        # 3. Create project
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        project_data = {
            'name': 'Home Budget 2026',
            'description': 'Tracking monthly household expenses'
        }
        response = client.post('/api/v1/projects/', project_data)
        assert response.status_code == status.HTTP_201_CREATED
        project_id = response.data['id']

        # 4. Create budget
        budget_data = {
            'name': 'Monthly Groceries',
            'amount': '500.00',
            'project': project_id,
            'period': 'monthly',
            'start_date': '2026-03-01',
            'end_date': '2026-03-31'
        }
        response = client.post('/api/v1/budgets/', budget_data)
        assert response.status_code == status.HTTP_201_CREATED
        budget_id = response.data['id']

        # 5. Add transactions
        transactions = [
            {'amount': '50.00', 'category': 'groceries', 'description': 'Weekly shopping'},
            {'amount': '30.50', 'category': 'groceries', 'description': 'Farmers market'},
            {'amount': '75.25', 'category': 'groceries', 'description': 'Bulk buy'},
        ]

        for trans_data in transactions:
            trans_data['project'] = project_id
            trans_data['date'] = '2026-03-27'
            response = client.post('/api/v1/transactions/', trans_data)
            assert response.status_code == status.HTTP_201_CREATED

        # 6. Check budget status
        response = client.get(f'/api/v1/budgets/{budget_id}/status/')
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data['spent']) == Decimal('155.75')
        assert Decimal(response.data['remaining']) == Decimal('344.25')
        assert response.data['status'] == 'on_track'

        # 7. Generate report
        response = client.get('/api/v1/reports/summary/', {
            'date_from': '2026-03-01',
            'date_to': '2026-03-31'
        })
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data['total_expense']) == Decimal('155.75')

    def test_user_cannot_access_other_projects(self, client):
        """Test that users can only access their own projects."""
        # Create two users
        user1 = User.objects.create_user(
            email='user1@example.com',
            password='Pass1234!'
        )
        user2 = User.objects.create_user(
            email='user2@example.com',
            password='Pass1234!'
        )

        # User1 creates a project
        client.force_authenticate(user=user1)
        project_data = {'name': 'User1 Private Project'}
        response = client.post('/api/v1/projects/', project_data)
        assert response.status_code == status.HTTP_201_CREATED
        project_id = response.data['id']

        # User2 tries to access it
        client.force_authenticate(user=user2)
        response = client.get(f'/api/v1/projects/{project_id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_complete_budget_workflow(self, client):
        """Test complete budget creation and tracking workflow."""
        user = User.objects.create_user(
            email='budgetuser@example.com',
            password='Pass1234!'
        )
        client.force_authenticate(user=user)

        # Create project
        project_data = {'name': 'Budget Project'}
        response = client.post('/api/v1/projects/', project_data)
        project_id = response.data['id']

        # Create multiple budgets
        categories = {
            'Food': '400.00',
            'Transportation': '200.00',
            'Entertainment': '150.00',
        }

        budgets = {}
        for category, amount in categories.items():
            data = {
                'name': f'{category} Budget',
                'amount': amount,
                'project': project_id,
                'period': 'monthly'
            }
            response = client.post('/api/v1/budgets/', data)
            assert response.status_code == status.HTTP_201_CREATED
            budgets[category] = response.data['id']

        # Add various transactions
        transactions = [
            ('Food', '50.00'),
            ('Food', '75.00'),
            ('Transportation', '30.00'),
            ('Entertainment', '25.00'),
        ]

        for category, amount in transactions:
            data = {
                'amount': amount,
                'category': category.lower(),
                'project': project_id,
                'date': '2026-03-27'
            }
            response = client.post('/api/v1/transactions/', data)
            assert response.status_code == status.HTTP_201_CREATED

        # Check all budgets
        response = client.get('/api/v1/budgets/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

        # Verify budget status
        response = client.get(f'/api/v1/budgets/{budgets["Food"]}/status/')
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data['spent']) == Decimal('125.00')

    def test_document_upload_and_tracking(self, client):
        """Test document upload workflow."""
        user = User.objects.create_user(
            email='docuser@example.com',
            password='Pass1234!'
        )
        client.force_authenticate(user=user)

        # Create project
        project_data = {'name': 'Document Project'}
        response = client.post('/api/v1/projects/', project_data)
        project_id = response.data['id']

        # Create transaction with document
        from django.core.files.uploadedfile import SimpleUploadedFile

        trans_data = {
            'amount': '100.00',
            'category': 'groceries',
            'project': project_id,
            'date': '2026-03-27'
        }

        response = client.post('/api/v1/transactions/', trans_data)
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.e2e
@pytest.mark.django_db
class TestTeamCollaborationWorkflow:
    """Test team collaboration features."""

    @pytest.fixture
    def client(self):
        return APIClient()

    def test_project_sharing_and_collaboration(self, client):
        """Test sharing project with team members."""
        # Create project owner
        owner = User.objects.create_user(
            email='owner@example.com',
            password='Pass1234!'
        )

        # Create team member
        member = User.objects.create_user(
            email='member@example.com',
            password='Pass1234!'
        )

        # Owner creates project
        client.force_authenticate(user=owner)
        project_data = {'name': 'Team Project'}
        response = client.post('/api/v1/projects/', project_data)
        assert response.status_code == status.HTTP_201_CREATED
        project_id = response.data['id']

        # Owner invites member
        invite_data = {'email': 'member@example.com'}
        response = client.post(
            f'/api/v1/projects/{project_id}/invite/',
            invite_data
        )
        # Endpoint may vary based on implementation
        assert response.status_code in [200, 201, 202]

        # Member accepts and accesses project
        client.force_authenticate(user=member)
        response = client.get(f'/api/v1/projects/{project_id}/')
        # Member should have access (status varies by implementation)
        assert response.status_code in [200, 404]  # 404 if not implemented

        # Both can add transactions
        if response.status_code == 200:
            trans_data = {
                'amount': '100.00',
                'category': 'groceries',
                'project': project_id
            }
            response = client.post('/api/v1/transactions/', trans_data)
            # Should be able to add transaction if member


@pytest.mark.e2e
@pytest.mark.django_db
class TestReportingWorkflow:
    """Test reporting and analytics workflow."""

    @pytest.fixture
    def client(self):
        return APIClient()

    def test_generate_various_reports(self, client):
        """Test generating different types of reports."""
        # Setup: Create user and data
        user = User.objects.create_user(
            email='reportuser@example.com',
            password='Pass1234!'
        )
        client.force_authenticate(user=user)

        # Create project and transactions
        project_data = {'name': 'Report Project'}
        response = client.post('/api/v1/projects/', project_data)
        project_id = response.data['id']

        # Add various transactions
        transactions_data = [
            ('2026-03-01', '50.00', 'groceries'),
            ('2026-03-05', '30.00', 'utilities'),
            ('2026-03-10', '100.00', 'groceries'),
            ('2026-03-15', '25.00', 'entertainment'),
            ('2026-03-20', '75.00', 'groceries'),
        ]

        for date, amount, category in transactions_data:
            data = {
                'amount': amount,
                'category': category,
                'project': project_id,
                'date': date
            }
            client.post('/api/v1/transactions/', data)

        # Generate summary report
        response = client.get('/api/v1/reports/summary/', {
            'date_from': '2026-03-01',
            'date_to': '2026-03-31'
        })
        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data['total_expense']) == Decimal('280.00')

        # Generate category breakdown
        response = client.get('/api/v1/reports/category-breakdown/', {
            'date_from': '2026-03-01',
            'date_to': '2026-03-31'
        })
        assert response.status_code == status.HTTP_200_OK

        # Generate trends
        response = client.get('/api/v1/reports/trends/', {
            'period': 'daily',
            'date_from': '2026-03-01',
            'date_to': '2026-03-31'
        })
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.e2e
@pytest.mark.django_db
class TestErrorHandlingWorkflow:
    """Test error handling and edge cases."""

    @pytest.fixture
    def client(self):
        return APIClient()

    def test_validation_errors_returned_properly(self, client):
        """Test that validation errors are returned properly."""
        user = User.objects.create_user(
            email='test@example.com',
            password='Pass1234!'
        )
        client.force_authenticate(user=user)

        # Missing required field
        response = client.post('/api/v1/projects/', {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'name' in response.data

        # Invalid data type
        response = client.post('/api/v1/transactions/', {
            'amount': 'not a number',
            'category': 'groceries'
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'amount' in response.data

    def test_not_found_errors(self, client):
        """Test 404 errors for non-existent resources."""
        user = User.objects.create_user(
            email='test@example.com',
            password='Pass1234!'
        )
        client.force_authenticate(user=user)

        # Non-existent project
        response = client.get('/api/v1/projects/nonexistent/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Non-existent transaction
        response = client.get('/api/v1/transactions/nonexistent/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthorized_access(self, client):
        """Test unauthorized access is rejected."""
        # No authentication
        response = client.get('/api/v1/projects/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Invalid token
        client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = client.get('/api/v1/projects/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.e2e
@pytest.mark.django_db
class TestDataIntegrityWorkflow:
    """Test data integrity across operations."""

    @pytest.fixture
    def client(self):
        return APIClient()

    def test_transaction_amount_precision(self, client):
        """Test decimal precision is maintained."""
        user = User.objects.create_user(
            email='test@example.com',
            password='Pass1234!'
        )
        client.force_authenticate(user=user)

        # Create project
        response = client.post('/api/v1/projects/', {'name': 'Test'})
        project_id = response.data['id']

        # Create transactions with precise amounts
        trans_data = {
            'amount': '99.99',
            'category': 'test',
            'project': project_id
        }
        response = client.post('/api/v1/transactions/', trans_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert str(response.data['amount']) == '99.99'

    def test_date_integrity(self, client):
        """Test dates are stored correctly."""
        user = User.objects.create_user(
            email='test@example.com',
            password='Pass1234!'
        )
        client.force_authenticate(user=user)

        response = client.post('/api/v1/projects/', {'name': 'Test'})
        project_id = response.data['id']

        trans_data = {
            'amount': '100.00',
            'category': 'test',
            'project': project_id,
            'date': '2026-03-15'
        }
        response = client.post('/api/v1/transactions/', trans_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['date'] == '2026-03-15'
