"""
Load testing script for Expense Tracker API using Locust.

Usage:
    locust -f tests/load_test.py --host=http://localhost:8000

With custom concurrency:
    locust -f tests/load_test.py --host=http://localhost:8000 -u 100 -r 10

WebUI:
    Open http://localhost:8089 in browser
"""
from locust import HttpUser, task, between, events
from locust.contrib.fasthttp import FastHttpUser
import random
import logging

logger = logging.getLogger(__name__)

# Test credentials (adjust for your environment)
TEST_EMAIL = "loadtest@example.com"
TEST_PASSWORD = "TestPassword123!"


class ExpenseTrackerUser(FastHttpUser):
    """
    Load testing user for Expense Tracker API.

    Simulates realistic user behavior:
    - 5x: List projects
    - 3x: List transactions
    - 2x: Create transactions
    - 1x: Generate reports
    """

    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks
    token = None
    project_id = None

    def on_start(self):
        """Called when a user starts."""
        self._login()
        self._get_or_create_project()

    def on_stop(self):
        """Called when a user stops."""
        pass

    def _login(self):
        """Login and get authentication token."""
        response = self.client.post(
            '/api/v1/auth/login/',
            json={
                'email': TEST_EMAIL,
                'password': TEST_PASSWORD
            },
            name='/api/v1/auth/login/'
        )

        if response.status_code == 200:
            try:
                self.token = response.json().get('access')
                logger.info(f"Login successful, token: {self.token[:20]}...")
            except Exception as e:
                logger.error(f"Failed to parse login response: {e}")
        else:
            logger.error(f"Login failed with status {response.status_code}")

    def _get_headers(self):
        """Get request headers with authentication."""
        return {
            'Authorization': f'Bearer {self.token}' if self.token else '',
            'Content-Type': 'application/json'
        }

    def _get_or_create_project(self):
        """Get or create a project for this user."""
        # Try to get existing projects
        response = self.client.get(
            '/api/v1/projects/',
            headers=self._get_headers(),
            name='/api/v1/projects/'
        )

        if response.status_code == 200:
            try:
                projects = response.json().get('results', [])
                if projects:
                    self.project_id = projects[0]['id']
                    logger.info(f"Using project: {self.project_id}")
                else:
                    self._create_project()
            except Exception as e:
                logger.error(f"Failed to parse projects: {e}")
                self._create_project()
        else:
            logger.error(f"Failed to list projects: {response.status_code}")
            self._create_project()

    def _create_project(self):
        """Create a new project."""
        response = self.client.post(
            '/api/v1/projects/',
            json={'name': f'Load Test Project {random.randint(1000, 9999)}'},
            headers=self._get_headers(),
            name='/api/v1/projects/ (POST)'
        )

        if response.status_code == 201:
            try:
                self.project_id = response.json().get('id')
                logger.info(f"Created project: {self.project_id}")
            except Exception as e:
                logger.error(f"Failed to parse project creation: {e}")
        else:
            logger.error(f"Failed to create project: {response.status_code}")

    @task(5)
    def list_projects(self):
        """List user's projects (5x frequency)."""
        self.client.get(
            '/api/v1/projects/',
            headers=self._get_headers(),
            name='/api/v1/projects/'
        )

    @task(3)
    def list_transactions(self):
        """List transactions (3x frequency)."""
        params = {
            'page': random.randint(1, 5),
            'limit': 50
        }
        self.client.get(
            '/api/v1/transactions/',
            headers=self._get_headers(),
            params=params,
            name='/api/v1/transactions/'
        )

    @task(3)
    def filter_transactions(self):
        """Filter transactions by various criteria."""
        categories = ['groceries', 'utilities', 'entertainment', 'transport']
        params = {
            'category': random.choice(categories),
            'date_from': '2026-01-01',
            'date_to': '2026-03-31'
        }
        self.client.get(
            '/api/v1/transactions/',
            headers=self._get_headers(),
            params=params,
            name='/api/v1/transactions/ (filtered)'
        )

    @task(2)
    def create_transaction(self):
        """Create a new transaction (2x frequency)."""
        data = {
            'amount': round(random.uniform(10, 500), 2),
            'category': random.choice(['groceries', 'utilities', 'entertainment']),
            'description': f'Load test transaction {random.randint(1000, 9999)}',
            'transaction_type': 'expense',
            'date': '2026-03-27'
        }

        if self.project_id:
            data['project'] = self.project_id

        self.client.post(
            '/api/v1/transactions/',
            json=data,
            headers=self._get_headers(),
            name='/api/v1/transactions/ (POST)'
        )

    @task(2)
    def list_budgets(self):
        """List budgets."""
        self.client.get(
            '/api/v1/budgets/',
            headers=self._get_headers(),
            name='/api/v1/budgets/'
        )

    @task(1)
    def get_summary_report(self):
        """Generate summary report (1x frequency)."""
        params = {
            'date_from': '2026-01-01',
            'date_to': '2026-03-31'
        }
        self.client.get(
            '/api/v1/reports/summary/',
            headers=self._get_headers(),
            params=params,
            name='/api/v1/reports/summary/'
        )

    @task(1)
    def get_category_breakdown(self):
        """Get category breakdown report."""
        params = {
            'date_from': '2026-01-01',
            'date_to': '2026-03-31'
        }
        self.client.get(
            '/api/v1/reports/category-breakdown/',
            headers=self._get_headers(),
            params=params,
            name='/api/v1/reports/category-breakdown/'
        )

    @task(1)
    def get_trends(self):
        """Get trends report."""
        params = {
            'period': 'daily',
            'date_from': '2026-01-01',
            'date_to': '2026-03-31'
        }
        self.client.get(
            '/api/v1/reports/trends/',
            headers=self._get_headers(),
            params=params,
            name='/api/v1/reports/trends/'
        )


class AdminUser(FastHttpUser):
    """Admin user performing heavier operations."""

    wait_time = between(2, 8)
    token = None

    def on_start(self):
        """Login as admin."""
        response = self.client.post(
            '/api/v1/auth/login/',
            json={
                'email': 'admin@example.com',
                'password': 'AdminPass123!'
            }
        )
        if response.status_code == 200:
            self.token = response.json().get('access')

    def _get_headers(self):
        """Get request headers with authentication."""
        return {
            'Authorization': f'Bearer {self.token}' if self.token else '',
            'Content-Type': 'application/json'
        }

    @task(3)
    def list_all_projects(self):
        """List all projects (admin view)."""
        self.client.get(
            '/api/v1/projects/',
            headers=self._get_headers(),
            name='/api/v1/projects/ (admin)'
        )

    @task(2)
    def list_activity_logs(self):
        """View activity logs."""
        self.client.get(
            '/api/v1/activity-logs/',
            headers=self._get_headers(),
            name='/api/v1/activity-logs/'
        )

    @task(1)
    def export_transactions(self):
        """Export transactions."""
        params = {'format': 'csv'}
        self.client.get(
            '/api/v1/transactions/export/',
            headers=self._get_headers(),
            params=params,
            name='/api/v1/transactions/export/'
        )


# Event handlers for metrics
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when test starts."""
    logger.info("=" * 50)
    logger.info("Load Test Started")
    logger.info(f"Target: {environment.host}")
    logger.info("=" * 50)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when test stops."""
    logger.info("=" * 50)
    logger.info("Load Test Completed")
    logger.info("=" * 50)

    # Print summary statistics
    stats = environment.stats
    total_requests = stats.total.num_requests
    total_failures = stats.total.num_failures

    if total_requests > 0:
        failure_rate = (total_failures / total_requests) * 100
        logger.info(f"Total Requests: {total_requests}")
        logger.info(f"Total Failures: {total_failures}")
        logger.info(f"Failure Rate: {failure_rate:.2f}%")
        logger.info(f"Average Response Time: {stats.total.avg_response_time:.2f}ms")
        logger.info(f"Min Response Time: {stats.total.min_response_time:.2f}ms")
        logger.info(f"Max Response Time: {stats.total.max_response_time:.2f}ms")
        logger.info(f"RPS: {stats.total.total_rps:.2f}")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    """Called after each request."""
    if exception:
        logger.warning(f"Request failed: {name} - {exception}")


if __name__ == "__main__":
    import sys
    print("Run with: locust -f tests/load_test.py --host=http://localhost:8000")
    sys.exit(0)
