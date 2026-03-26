# Expense Tracker - Backend Product Requirements Document (PRD)

**Version:** 1.0  
**Last Updated:** March 12, 2026  
**Project Type:** Web Application (Django Backend)  
**Target:** MVP with incremental feature growth

---

## 1. Executive Summary

### 1.1 Product Overview
A full-featured expense tracking system that supports personal projects, business projects, and team collaborations. The MVP focuses on core expense/income tracking, document management, analytics, and multi-user collaboration.

### 1.2 Goals
- Enable users to track expenses and income across multiple projects
- Support team collaboration with role-based access control
- Provide receipt/document upload and management
- Generate meaningful financial reports and analytics
- Build a scalable foundation for future features

### 1.3 Success Metrics
- User can create and manage projects within 2 minutes
- Expense/income entry takes less than 30 seconds
- Document upload success rate > 99%
- API response time < 500ms for 95% of requests
- Support 100+ concurrent users initially

---

## 2. Technical Stack

### 2.1 Core Technologies
- **Framework:** Django 5.0+
- **Database:** PostgreSQL 15+
- **API:** Django REST Framework (DRF)
- **Authentication:** JWT (Simple JWT)
- **File Storage:** AWS S3 or compatible (e.g., DigitalOcean Spaces)
- **Task Queue:** Celery + Redis
- **Caching:** Redis
- **Server:** Gunicorn + Nginx

### 2.2 Key Libraries
```
django>=5.0
djangorestframework>=3.14
django-cors-headers
djangorestframework-simplejwt
psycopg2-binary
celery>=5.3
redis>=5.0
boto3  # For S3
Pillow  # Image processing
python-decouple  # Environment variables
django-filter
drf-spectacular  # API documentation
```

---

## 3. System Architecture

### 3.1 High-Level Architecture
```
┌─────────────┐
│   Client    │
│  (React/    │
│   Next.js)  │
└──────┬──────┘
       │ HTTPS/REST
       ▼
┌─────────────────────────────────┐
│         Nginx (Reverse Proxy)   │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│      Django + Gunicorn          │
│  ┌──────────────────────────┐   │
│  │  Django REST Framework   │   │
│  │  - Authentication        │   │
│  │  - Business Logic        │   │
│  │  - API Endpoints         │   │
│  └──────────────────────────┘   │
└──────┬───────────────┬──────────┘
       │               │
       ▼               ▼
┌─────────────┐ ┌─────────────┐
│ PostgreSQL  │ │    Redis    │
│  (Primary)  │ │  (Cache +   │
│             │ │   Celery)   │
└─────────────┘ └─────────────┘
       │
       ▼
┌─────────────┐
│  S3/Spaces  │
│   (Files)   │
└─────────────┘
```

### 3.2 Deployment Architecture
- **Containerization:** Docker + Docker Compose
- **CI/CD:** GitHub Actions
- **Hosting:** VPS (DigitalOcean/AWS) or Render
- **Domain:** api.expensetracker.com

---

## 4. Data Models

### 4.1 User Model
```python
class User(AbstractUser):
    """Extended Django User model"""
    id = UUIDField(primary_key=True, default=uuid4)
    email = EmailField(unique=True)
    phone_number = CharField(max_length=20, blank=True)
    avatar = ImageField(upload_to='avatars/', null=True, blank=True)
    timezone = CharField(max_length=50, default='UTC')
    currency_preference = CharField(max_length=3, default='USD')
    is_email_verified = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    # Metadata
    last_login_ip = GenericIPAddressField(null=True, blank=True)
    is_active = BooleanField(default=True)
```

### 4.2 Project Model
```python
class Project(Model):
    """Projects can be personal, business, or team-based"""
    
    class ProjectType(TextChoices):
        PERSONAL = 'personal', 'Personal'
        BUSINESS = 'business', 'Business'
        TEAM = 'team', 'Team'
    
    id = UUIDField(primary_key=True, default=uuid4)
    name = CharField(max_length=255)
    description = TextField(blank=True)
    project_type = CharField(max_length=20, choices=ProjectType.choices)
    owner = ForeignKey(User, on_delete=CASCADE, related_name='owned_projects')
    
    # Settings
    currency = CharField(max_length=3, default='USD')
    budget = DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    start_date = DateField(null=True, blank=True)
    end_date = DateField(null=True, blank=True)
    
    # Status
    is_active = BooleanField(default=True)
    is_archived = BooleanField(default=False)
    
    # Timestamps
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            Index(fields=['owner', 'is_active']),
            Index(fields=['project_type']),
        ]
```

### 4.3 ProjectMember Model
```python
class ProjectMember(Model):
    """Team members and their roles in projects"""
    
    class Role(TextChoices):
        OWNER = 'owner', 'Owner'
        ADMIN = 'admin', 'Admin'
        MEMBER = 'member', 'Member'
        VIEWER = 'viewer', 'Viewer'
    
    id = UUIDField(primary_key=True, default=uuid4)
    project = ForeignKey(Project, on_delete=CASCADE, related_name='members')
    user = ForeignKey(User, on_delete=CASCADE, related_name='project_memberships')
    role = CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    
    # Permissions
    can_create_transactions = BooleanField(default=True)
    can_edit_transactions = BooleanField(default=True)
    can_delete_transactions = BooleanField(default=False)
    can_view_reports = BooleanField(default=True)
    can_invite_members = BooleanField(default=False)
    
    # Metadata
    invited_by = ForeignKey(User, on_delete=SET_NULL, null=True, related_name='invited_members')
    joined_at = DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['project', 'user']
        indexes = [
            Index(fields=['project', 'role']),
        ]
```

### 4.4 Category Model
```python
class Category(Model):
    """Expense and income categories"""
    
    class CategoryType(TextChoices):
        INCOME = 'income', 'Income'
        EXPENSE = 'expense', 'Expense'
    
    id = UUIDField(primary_key=True, default=uuid4)
    name = CharField(max_length=100)
    category_type = CharField(max_length=10, choices=CategoryType.choices)
    icon = CharField(max_length=50, blank=True)  # Icon name/emoji
    color = CharField(max_length=7, default='#000000')  # Hex color
    
    # Ownership
    project = ForeignKey(Project, on_delete=CASCADE, related_name='categories', null=True, blank=True)
    is_default = BooleanField(default=False)  # System-wide default categories
    
    created_at = DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
        indexes = [
            Index(fields=['project', 'category_type']),
        ]
```

### 4.5 Transaction Model
```python
class Transaction(Model):
    """Core expense and income tracking"""
    
    class TransactionType(TextChoices):
        INCOME = 'income', 'Income'
        EXPENSE = 'expense', 'Expense'
    
    class PaymentMethod(TextChoices):
        CASH = 'cash', 'Cash'
        CREDIT_CARD = 'credit_card', 'Credit Card'
        DEBIT_CARD = 'debit_card', 'Debit Card'
        BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
        MOBILE_PAYMENT = 'mobile_payment', 'Mobile Payment'
        OTHER = 'other', 'Other'
    
    id = UUIDField(primary_key=True, default=uuid4)
    project = ForeignKey(Project, on_delete=CASCADE, related_name='transactions')
    
    # Transaction details
    transaction_type = CharField(max_length=10, choices=TransactionType.choices)
    amount = DecimalField(max_digits=15, decimal_places=2)
    currency = CharField(max_length=3, default='USD')
    category = ForeignKey(Category, on_delete=PROTECT, related_name='transactions')
    
    # Description
    title = CharField(max_length=255)
    description = TextField(blank=True)
    
    # Payment
    payment_method = CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    
    # Dates
    transaction_date = DateField()  # When the transaction occurred
    
    # Metadata
    created_by = ForeignKey(User, on_delete=PROTECT, related_name='created_transactions')
    tags = JSONField(default=list, blank=True)  # Flexible tagging system
    
    # Status
    is_recurring = BooleanField(default=False)
    recurring_frequency = CharField(max_length=20, blank=True)  # daily, weekly, monthly, yearly
    
    # Timestamps
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            Index(fields=['project', 'transaction_date']),
            Index(fields=['project', 'transaction_type']),
            Index(fields=['category']),
            Index(fields=['created_by']),
        ]
```

### 4.6 Document Model
```python
class Document(Model):
    """Receipts and supporting documents"""
    
    class DocumentType(TextChoices):
        RECEIPT = 'receipt', 'Receipt'
        INVOICE = 'invoice', 'Invoice'
        CONTRACT = 'contract', 'Contract'
        OTHER = 'other', 'Other'
    
    id = UUIDField(primary_key=True, default=uuid4)
    transaction = ForeignKey(Transaction, on_delete=CASCADE, related_name='documents')
    
    # File details
    file = FileField(upload_to='documents/%Y/%m/')
    file_name = CharField(max_length=255)
    file_size = IntegerField()  # in bytes
    file_type = CharField(max_length=50)  # MIME type
    document_type = CharField(max_length=20, choices=DocumentType.choices, default=DocumentType.RECEIPT)
    
    # Metadata
    uploaded_by = ForeignKey(User, on_delete=PROTECT, related_name='uploaded_documents')
    notes = TextField(blank=True)
    
    # Timestamps
    uploaded_at = DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
```

### 4.7 Budget Model
```python
class Budget(Model):
    """Budget tracking for categories or projects"""
    
    class BudgetPeriod(TextChoices):
        WEEKLY = 'weekly', 'Weekly'
        MONTHLY = 'monthly', 'Monthly'
        QUARTERLY = 'quarterly', 'Quarterly'
        YEARLY = 'yearly', 'Yearly'
        CUSTOM = 'custom', 'Custom'
    
    id = UUIDField(primary_key=True, default=uuid4)
    project = ForeignKey(Project, on_delete=CASCADE, related_name='budgets')
    category = ForeignKey(Category, on_delete=CASCADE, related_name='budgets', null=True, blank=True)
    
    # Budget details
    amount = DecimalField(max_digits=15, decimal_places=2)
    period = CharField(max_length=20, choices=BudgetPeriod.choices)
    start_date = DateField()
    end_date = DateField()
    
    # Alerts
    alert_threshold = IntegerField(default=80)  # Alert at 80% by default
    alert_enabled = BooleanField(default=True)
    
    # Metadata
    created_by = ForeignKey(User, on_delete=PROTECT)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
```

### 4.8 Invitation Model
```python
class Invitation(Model):
    """Project invitations for team members"""
    
    class Status(TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        DECLINED = 'declined', 'Declined'
        EXPIRED = 'expired', 'Expired'
    
    id = UUIDField(primary_key=True, default=uuid4)
    project = ForeignKey(Project, on_delete=CASCADE, related_name='invitations')
    email = EmailField()
    role = CharField(max_length=20, choices=ProjectMember.Role.choices, default=ProjectMember.Role.MEMBER)
    
    # Invitation details
    invited_by = ForeignKey(User, on_delete=CASCADE, related_name='sent_invitations')
    token = CharField(max_length=100, unique=True)
    status = CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    
    # Timestamps
    created_at = DateTimeField(auto_now_add=True)
    expires_at = DateTimeField()  # 7 days default
    accepted_at = DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['project', 'email', 'status']
```

### 4.9 ActivityLog Model
```python
class ActivityLog(Model):
    """Audit trail for important actions"""
    
    class ActionType(TextChoices):
        CREATE = 'create', 'Create'
        UPDATE = 'update', 'Update'
        DELETE = 'delete', 'Delete'
        INVITE = 'invite', 'Invite'
        JOIN = 'join', 'Join'
        LEAVE = 'leave', 'Leave'
    
    id = UUIDField(primary_key=True, default=uuid4)
    project = ForeignKey(Project, on_delete=CASCADE, related_name='activity_logs')
    user = ForeignKey(User, on_delete=SET_NULL, null=True)
    
    # Action details
    action_type = CharField(max_length=20, choices=ActionType.choices)
    resource_type = CharField(max_length=50)  # 'transaction', 'document', 'member', etc.
    resource_id = UUIDField()
    description = TextField()
    
    # Metadata
    ip_address = GenericIPAddressField(null=True, blank=True)
    user_agent = CharField(max_length=255, blank=True)
    
    created_at = DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            Index(fields=['project', 'created_at']),
            Index(fields=['user']),
        ]
```

---

## 5. API Endpoints

### 5.1 Authentication
```
POST   /api/v1/auth/register/           # User registration
POST   /api/v1/auth/login/              # Login (returns JWT)
POST   /api/v1/auth/refresh/            # Refresh JWT token
POST   /api/v1/auth/logout/             # Logout (blacklist token)
POST   /api/v1/auth/password/reset/     # Request password reset
POST   /api/v1/auth/password/confirm/   # Confirm password reset
GET    /api/v1/auth/me/                 # Get current user
PATCH  /api/v1/auth/me/                 # Update current user
POST   /api/v1/auth/verify-email/       # Verify email address
```

### 5.2 Projects
```
GET    /api/v1/projects/                # List user's projects
POST   /api/v1/projects/                # Create project
GET    /api/v1/projects/{id}/           # Get project details
PATCH  /api/v1/projects/{id}/           # Update project
DELETE /api/v1/projects/{id}/           # Delete project
POST   /api/v1/projects/{id}/archive/   # Archive project
GET    /api/v1/projects/{id}/stats/     # Project statistics
GET    /api/v1/projects/{id}/summary/   # Financial summary
```

### 5.3 Project Members
```
GET    /api/v1/projects/{id}/members/                # List members
POST   /api/v1/projects/{id}/members/invite/         # Invite member
PATCH  /api/v1/projects/{id}/members/{member_id}/    # Update member role
DELETE /api/v1/projects/{id}/members/{member_id}/    # Remove member
POST   /api/v1/projects/{id}/members/leave/          # Leave project
```

### 5.4 Invitations
```
GET    /api/v1/invitations/             # List user's invitations
POST   /api/v1/invitations/{token}/accept/    # Accept invitation
POST   /api/v1/invitations/{token}/decline/   # Decline invitation
```

### 5.5 Transactions
```
GET    /api/v1/projects/{id}/transactions/              # List transactions
POST   /api/v1/projects/{id}/transactions/              # Create transaction
GET    /api/v1/projects/{id}/transactions/{txn_id}/     # Get transaction
PATCH  /api/v1/projects/{id}/transactions/{txn_id}/     # Update transaction
DELETE /api/v1/projects/{id}/transactions/{txn_id}/     # Delete transaction
GET    /api/v1/projects/{id}/transactions/export/       # Export (CSV/Excel)
POST   /api/v1/projects/{id}/transactions/bulk-create/  # Bulk import
```

### 5.6 Categories
```
GET    /api/v1/projects/{id}/categories/           # List categories
POST   /api/v1/projects/{id}/categories/           # Create category
PATCH  /api/v1/projects/{id}/categories/{cat_id}/  # Update category
DELETE /api/v1/projects/{id}/categories/{cat_id}/  # Delete category
GET    /api/v1/categories/defaults/                # Get default categories
```

### 5.7 Documents
```
GET    /api/v1/transactions/{id}/documents/           # List documents
POST   /api/v1/transactions/{id}/documents/           # Upload document
GET    /api/v1/transactions/{id}/documents/{doc_id}/  # Get document
DELETE /api/v1/transactions/{id}/documents/{doc_id}/  # Delete document
GET    /api/v1/transactions/{id}/documents/{doc_id}/download/  # Download
```

### 5.8 Budgets
```
GET    /api/v1/projects/{id}/budgets/           # List budgets
POST   /api/v1/projects/{id}/budgets/           # Create budget
PATCH  /api/v1/projects/{id}/budgets/{bud_id}/  # Update budget
DELETE /api/v1/projects/{id}/budgets/{bud_id}/  # Delete budget
GET    /api/v1/projects/{id}/budgets/status/    # Budget status summary
```

### 5.9 Reports & Analytics
```
GET    /api/v1/projects/{id}/reports/summary/           # Financial summary
GET    /api/v1/projects/{id}/reports/trends/            # Spending trends
GET    /api/v1/projects/{id}/reports/category-breakdown/ # Category analysis
GET    /api/v1/projects/{id}/reports/monthly/           # Monthly report
GET    /api/v1/projects/{id}/reports/comparison/        # Period comparison
GET    /api/v1/projects/{id}/reports/export/            # Export report (PDF)
```

### 5.10 Activity Logs
```
GET    /api/v1/projects/{id}/activity/  # Project activity log
```

---

## 6. Request/Response Examples

### 6.1 Create Transaction
**Request:**
```json
POST /api/v1/projects/123e4567-e89b-12d3-a456-426614174000/transactions/
Content-Type: application/json
Authorization: Bearer <jwt_token>

{
  "transaction_type": "expense",
  "amount": "45.99",
  "currency": "USD",
  "category": "987fcdeb-51a2-12d3-a456-426614174000",
  "title": "Office supplies",
  "description": "Printer paper and ink cartridges",
  "payment_method": "credit_card",
  "transaction_date": "2026-03-12",
  "tags": ["office", "supplies", "tax-deductible"]
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "project": "123e4567-e89b-12d3-a456-426614174000",
  "transaction_type": "expense",
  "amount": "45.99",
  "currency": "USD",
  "category": {
    "id": "987fcdeb-51a2-12d3-a456-426614174000",
    "name": "Office Supplies",
    "icon": "📎",
    "color": "#3B82F6"
  },
  "title": "Office supplies",
  "description": "Printer paper and ink cartridges",
  "payment_method": "credit_card",
  "transaction_date": "2026-03-12",
  "tags": ["office", "supplies", "tax-deductible"],
  "is_recurring": false,
  "created_by": {
    "id": "user-uuid",
    "email": "user@example.com",
    "first_name": "John"
  },
  "documents": [],
  "created_at": "2026-03-12T10:30:00Z",
  "updated_at": "2026-03-12T10:30:00Z"
}
```

### 6.2 Get Project Summary
**Request:**
```json
GET /api/v1/projects/123e4567-e89b-12d3-a456-426614174000/summary/?period=month
Authorization: Bearer <jwt_token>
```

**Response:**
```json
{
  "project": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "Marketing Campaign Q1",
    "currency": "USD"
  },
  "period": {
    "start": "2026-03-01",
    "end": "2026-03-31"
  },
  "summary": {
    "total_income": "5000.00",
    "total_expenses": "3245.67",
    "net": "1754.33",
    "transaction_count": 45
  },
  "by_category": [
    {
      "category": "Advertising",
      "amount": "1200.00",
      "percentage": 37.0,
      "count": 12
    },
    {
      "category": "Software",
      "amount": "899.99",
      "percentage": 27.7,
      "count": 5
    }
  ],
  "budget_status": {
    "allocated": "5000.00",
    "spent": "3245.67",
    "remaining": "1754.33",
    "percentage_used": 64.9
  },
  "trends": {
    "vs_last_period": {
      "income_change": "+12.5",
      "expense_change": "-5.3"
    }
  }
}
```

### 6.3 Upload Document
**Request:**
```http
POST /api/v1/transactions/550e8400-e29b-41d4-a716-446655440000/documents/
Content-Type: multipart/form-data
Authorization: Bearer <jwt_token>

file: [binary data]
document_type: receipt
notes: "Receipt for office supplies from Staples"
```

**Response:**
```json
{
  "id": "doc-uuid-here",
  "transaction": "550e8400-e29b-41d4-a716-446655440000",
  "file": "https://s3.amazonaws.com/bucket/documents/2026/03/receipt_12345.pdf",
  "file_name": "receipt_12345.pdf",
  "file_size": 245678,
  "file_type": "application/pdf",
  "document_type": "receipt",
  "notes": "Receipt for office supplies from Staples",
  "uploaded_by": {
    "id": "user-uuid",
    "email": "user@example.com"
  },
  "uploaded_at": "2026-03-12T10:35:00Z"
}
```

---

## 7. Business Logic & Features

### 7.1 Permission System

**Project Roles:**
- **Owner:** Full control, can delete project
- **Admin:** Can manage members, edit settings, full CRUD on transactions
- **Member:** Can create/edit own transactions, view reports
- **Viewer:** Read-only access to transactions and reports

**Permission Checks:**
```python
# Example permission logic
def can_edit_transaction(user, transaction):
    member = ProjectMember.objects.get(user=user, project=transaction.project)
    
    if member.role in ['owner', 'admin']:
        return True
    
    if member.role == 'member' and member.can_edit_transactions:
        # Members can only edit their own transactions
        return transaction.created_by == user
    
    return False
```

### 7.2 Budget Tracking & Alerts

**Budget Monitoring:**
- Calculate spent amount for budget period
- Compare against budget limit
- Trigger alerts at threshold (80% by default)
- Send notifications via Celery tasks

**Alert Triggers:**
```python
# Celery task
@shared_task
def check_budget_alerts():
    active_budgets = Budget.objects.filter(
        alert_enabled=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    )
    
    for budget in active_budgets:
        spent = calculate_budget_spent(budget)
        percentage = (spent / budget.amount) * 100
        
        if percentage >= budget.alert_threshold:
            send_budget_alert_notification(budget, percentage)
```

### 7.3 Currency Handling

**Multi-Currency Support:**
- Each project has a base currency
- Transactions can be in different currencies
- Store original currency and amount
- Convert to project currency for reports (future feature: use exchange rate API)

**For MVP:**
- Store currency with each transaction
- Reports show amounts in project's base currency
- Manual currency selection (no auto-conversion yet)

### 7.4 Document Management

**File Upload Flow:**
1. Validate file type and size (max 10MB)
2. Generate unique filename
3. Upload to S3/storage
4. Create Document record with metadata
5. Return signed URL for access

**Allowed File Types:**
- Images: JPG, PNG, HEIC, WebP
- Documents: PDF
- Spreadsheets: XLSX, CSV (for future import feature)

### 7.5 Analytics & Reports

**Summary Calculations:**
```python
def get_project_summary(project, start_date, end_date):
    transactions = project.transactions.filter(
        transaction_date__range=[start_date, end_date]
    )
    
    income = transactions.filter(
        transaction_type='income'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    expenses = transactions.filter(
        transaction_type='expense'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    return {
        'total_income': income,
        'total_expenses': expenses,
        'net': income - expenses,
        'transaction_count': transactions.count()
    }
```

**Category Breakdown:**
- Group transactions by category
- Calculate totals and percentages
- Sort by amount (descending)
- Include transaction count

**Trend Analysis:**
- Compare current period vs previous period
- Calculate percentage changes
- Identify spending patterns
- Monthly/weekly aggregations

### 7.6 Activity Logging

**Logged Actions:**
- Transaction CRUD operations
- Member additions/removals
- Project settings changes
- Document uploads/deletions
- Budget modifications

**Log Entry Creation:**
```python
def log_activity(project, user, action_type, resource_type, resource_id, description):
    ActivityLog.objects.create(
        project=project,
        user=user,
        action_type=action_type,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
```

---

## 8. Authentication & Security

### 8.1 JWT Authentication

**Token Configuration:**
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
```

**Token Structure:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 8.2 Security Best Practices

**Required Security Measures:**
1. **HTTPS only** in production
2. **CORS** configuration for frontend domain
3. **Rate limiting** on authentication endpoints
4. **Password requirements:** Min 8 chars, complexity rules
5. **Email verification** before full account access
6. **File upload validation:** Type, size, malware scanning
7. **SQL injection protection:** Use ORM, parameterized queries
8. **XSS protection:** Sanitize user inputs
9. **CSRF protection:** Django's built-in middleware
10. **Sensitive data:** Never log passwords, tokens, or card data

**Environment Variables:**
```bash
# Required environment variables
SECRET_KEY=<django-secret-key>
DEBUG=False
ALLOWED_HOSTS=api.expensetracker.com

DATABASE_URL=postgresql://user:pass@host:5432/dbname

AWS_ACCESS_KEY_ID=<s3-key>
AWS_SECRET_ACCESS_KEY=<s3-secret>
AWS_STORAGE_BUCKET_NAME=expense-tracker-files
AWS_S3_REGION_NAME=us-east-1

REDIS_URL=redis://localhost:6379/0

CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

CORS_ALLOWED_ORIGINS=https://expensetracker.com

# Email settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<email>
EMAIL_HOST_PASSWORD=<password>
```

### 8.3 Rate Limiting

**Implement rate limiting for:**
- Authentication endpoints: 5 attempts per 15 minutes
- API endpoints: 100 requests per minute per user
- File uploads: 20 uploads per hour per user

**Using Django-ratelimit:**
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/15m', method='POST')
def login_view(request):
    # Login logic
    pass
```

---

## 9. Testing Requirements

### 9.1 Unit Tests

**Required Test Coverage: >80%**

**Test Categories:**
1. **Model Tests:**
   - Field validations
   - Model methods
   - Constraints (unique, foreign keys)
   - Default values

2. **API Tests:**
   - Authentication
   - CRUD operations
   - Permission checks
   - Input validation
   - Error handling

3. **Business Logic Tests:**
   - Budget calculations
   - Report generation
   - Permission system
   - Currency handling

**Example Test Structure:**
```python
class TransactionAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(...)
        self.project = Project.objects.create(...)
        self.client.force_authenticate(user=self.user)
    
    def test_create_transaction_success(self):
        # Test successful transaction creation
        pass
    
    def test_create_transaction_invalid_amount(self):
        # Test validation
        pass
    
    def test_create_transaction_unauthorized(self):
        # Test permissions
        pass
```

### 9.2 Integration Tests

**Test Scenarios:**
- Complete user workflow: Register → Create project → Add transaction → Upload receipt → View report
- Multi-user collaboration: Invite member → Member accepts → Member creates transaction
- Budget alerts: Create budget → Add transactions → Check alert triggered

### 9.3 Performance Tests

**Load Testing:**
- 100 concurrent users
- Average response time < 500ms
- 95th percentile < 1000ms
- Database query optimization (N+1 prevention)

---

## 10. Deployment & DevOps

### 10.1 Docker Configuration

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: expense_tracker
      POSTGRES_USER: expense_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    env_file:
      - .env

  celery:
    build: .
    command: celery -A config worker -l info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    env_file:
      - .env

  celery-beat:
    build: .
    command: celery -A config beat -l info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    env_file:
      - .env

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - web

volumes:
  postgres_data:
```

### 10.2 CI/CD Pipeline

**GitHub Actions Workflow:**
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run migrations
        run: python manage.py migrate
      
      - name: Run tests
        run: |
          pytest --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Deploy to production
        run: |
          # SSH into server and pull latest code
          # Run migrations
          # Restart services
```

### 10.3 Monitoring & Logging

**Required Monitoring:**
1. **Application Performance:**
   - Response times
   - Error rates
   - Database query performance

2. **Infrastructure:**
   - CPU/Memory usage
   - Disk space
   - Network traffic

3. **Business Metrics:**
   - User registrations
   - Active projects
   - Transaction volume
   - File uploads

**Logging Setup:**
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

**Tools:**
- **Sentry:** Error tracking and monitoring
- **New Relic/DataDog:** APM (Application Performance Monitoring)
- **Prometheus + Grafana:** Metrics and dashboards
- **ELK Stack:** Log aggregation and analysis

---

## 11. Database Optimization

### 11.1 Indexing Strategy

**Key Indexes:**
```python
# Already defined in models, but highlighting critical ones:

# Transaction lookups by project and date
Index(fields=['project', 'transaction_date'])

# Category filtering
Index(fields=['project', 'category', 'transaction_type'])

# User's projects
Index(fields=['owner', 'is_active'])

# Activity logs
Index(fields=['project', 'created_at'])
```

### 11.2 Query Optimization

**Use select_related and prefetch_related:**
```python
# Bad - N+1 queries
transactions = Transaction.objects.filter(project=project)
for t in transactions:
    print(t.category.name)  # N additional queries

# Good - Single query with JOIN
transactions = Transaction.objects.filter(
    project=project
).select_related('category', 'created_by')
```

**Pagination:**
```python
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100
```

### 11.3 Caching Strategy

**Cache Frequently Accessed Data:**
```python
from django.core.cache import cache

def get_project_summary(project_id, start_date, end_date):
    cache_key = f'summary_{project_id}_{start_date}_{end_date}'
    result = cache.get(cache_key)
    
    if result is None:
        result = calculate_summary(project_id, start_date, end_date)
        cache.set(cache_key, result, 300)  # Cache for 5 minutes
    
    return result
```

**Cache Invalidation:**
- Invalidate project summary cache when transactions are added/modified
- Invalidate budget status cache when budgets or transactions change

---

## 12. API Documentation

### 12.1 Auto-Generated Documentation

**Use drf-spectacular for OpenAPI/Swagger:**
```python
# settings.py
INSTALLED_APPS += ['drf_spectacular']

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Expense Tracker API',
    'DESCRIPTION': 'RESTful API for expense tracking and project management',
    'VERSION': '1.0.0',
}

# urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

**Access Documentation:**
- OpenAPI Schema: `https://api.expensetracker.com/api/schema/`
- Swagger UI: `https://api.expensetracker.com/api/docs/`

---

## 13. Future Enhancements (Post-MVP)

### Phase 2 Features
1. **Recurring Transactions:**
   - Automatic transaction creation
   - Customizable schedules
   - Skip/modify future occurrences

2. **Currency Conversion:**
   - Real-time exchange rates API
   - Automatic conversion to base currency
   - Historical rate tracking

3. **Advanced Analytics:**
   - Predictive spending patterns
   - Budget forecasting
   - Anomaly detection

4. **Integrations:**
   - Bank account linking (Plaid API)
   - Accounting software export (QuickBooks, Xero)
   - Receipt OCR (extract data from images)

5. **Mobile Features:**
   - Native mobile apps (iOS/Android)
   - Offline mode
   - Push notifications

6. **Advanced Permissions:**
   - Custom roles
   - Granular permissions
   - Approval workflows

7. **Tax Features:**
   - Tax category tagging
   - Tax report generation
   - Export for accountants

---

## 14. Development Checklist

> **Testing Policy:** After completing each feature section below, you must complete both unit tests and API tests before moving to the next feature. Mark tests as complete only when coverage is >80% for that module.

### Phase 1: Project Setup & Foundation

#### 1.1 Initial Setup
- [x] Create Django project structure
- [x] Configure PostgreSQL database
- [x] Set up Redis for caching
- [x] Configure environment variables (.env)
- [x] Set up logging configuration
- [x] Create requirements.txt files
- [x] Initialize Git repository
- [x] Create .gitignore file
- [ ] Set up pre-commit hooks
- [ ] **Testing:**
  - [ ] Write tests for settings configuration
  - [ ] Test database connectivity
  - [ ] Test Redis connectivity

#### 1.2 Docker Configuration
- [x] Create Dockerfile
- [x] Create docker-compose.yml
- [x] Configure PostgreSQL service
- [x] Configure Redis service
- [x] Configure web service (Gunicorn)
- [x] Configure Celery worker service
- [x] Configure Celery beat service
- [ ] Configure Nginx service
- [ ] Test Docker build
- [ ] Test docker-compose up
- [ ] **Testing:**
  - [ ] Test all services start successfully
  - [ ] Test service communication
  - [ ] Test volume persistence

---

### Phase 2: Authentication & User Management

#### 2.1 User Model
- [x] Create custom User model (extend AbstractUser)
- [x] Add UUID primary key
- [x] Add email field (unique)
- [x] Add phone_number field
- [x] Add avatar field
- [x] Add timezone field
- [x] Add currency_preference field
- [x] Add is_email_verified field
- [x] Add timestamps (created_at, updated_at)
- [x] Add last_login_ip field
- [x] Create and run migrations
- [x] **Unit Testing:**
  - [x] Test user creation
  - [x] Test field validations
  - [x] Test unique email constraint
  - [x] Test default values
  - [x] Test string representation
  - [ ] Coverage: >80%

#### 2.2 Authentication Endpoints
- [x] Install djangorestframework-simplejwt
- [x] Configure JWT settings
- [x] Create UserSerializer
- [x] Create registration endpoint (POST /api/v1/auth/register/)
- [x] Create login endpoint (POST /api/v1/auth/login/)
- [x] Create token refresh endpoint (POST /api/v1/auth/refresh/)
- [x] Create logout endpoint (POST /api/v1/auth/logout/)
- [x] Create get current user endpoint (GET /api/v1/auth/me/)
- [x] Create update user endpoint (PATCH /api/v1/auth/me/)
- [x] Implement password validation
- [x] **Unit Testing:**
  - [x] Test serializer validations
  - [x] Test password hashing
  - [x] Test email format validation
  - [ ] Coverage: >80%
- [x] **API Testing:**
  - [x] Test user registration (valid data)
  - [x] Test registration with duplicate email (expect 400)
  - [x] Test registration with weak password (expect 400)
  - [x] Test login with valid credentials (expect 200 + tokens)
  - [x] Test login with invalid credentials (expect 401)
  - [x] Test token refresh (expect new access token)
  - [x] Test logout (expect token blacklist)
  - [x] Test get current user (authenticated)
  - [x] Test get current user (unauthenticated - expect 401)
  - [x] Test update user profile
  - [ ] **Edge Cases:**
    - [x] Test registration with malformed email (missing @, invalid domain)
    - [x] Test registration with empty fields
    - [ ] Test registration with SQL injection in fields
    - [ ] Test registration with extremely long email (>254 chars)
    - [ ] Test registration with special characters in name
    - [ ] Test login with correct email but wrong case
    - [ ] Test login after multiple failed attempts (rate limiting)
    - [ ] Test token refresh with expired refresh token
    - [x] Test token refresh with invalid token format
    - [x] Test using revoked/blacklisted token
    - [ ] Test concurrent login sessions
    - [ ] Test update profile with taken email
    - [ ] Test update profile with XSS in fields
  - [ ] Coverage: >80%

#### 2.3 Email Verification
- [x] Create email verification token model
- [x] Create send verification email function
- [x] Create verify email endpoint (POST /api/v1/auth/verify-email/)
- [x] Set up email backend (SMTP)
- [ ] Create email templates
- [x] Implement token expiration (24 hours)
- [x] **Unit Testing:**
  - [x] Test token generation
  - [x] Test token expiration
  - [ ] Test email sending
  - [ ] Coverage: >80%
- [x] **API Testing:**
  - [x] Test email verification success
  - [x] Test with invalid token (expect 400)
  - [x] Test with expired token (expect 400)
  - [ ] **Edge Cases:**
    - [x] Test with malformed token (random string)
    - [ ] Test with already verified email
    - [ ] Test with deleted user account
    - [x] Test token reuse after successful verification
    - [ ] Test with tampered token payload
  - [ ] Coverage: >80%

#### 2.4 Password Reset
- [x] Create password reset token model
- [x] Create request password reset endpoint
- [x] Create confirm password reset endpoint
- [x] Send password reset email
- [x] Implement token expiration (1 hour)
- [x] **Unit Testing:**
  - [x] Test token generation
  - [x] Test password validation
  - [ ] Coverage: >80%
- [x] **API Testing:**
  - [x] Test password reset request
  - [x] Test password reset confirmation
  - [x] Test with invalid token
  - [ ] **Edge Cases:**
    - [x] Test password reset for non-existent email
    - [x] Test multiple password reset requests (should invalidate old tokens)
    - [ ] Test with token from different user
    - [ ] Test setting same password as current
    - [x] Test with weak new password
    - [x] Test password reset after token expiration
    - [ ] Test rapid successive reset requests (rate limiting)
  - [ ] Coverage: >80%

---

### Phase 3: Projects Module

#### 3.1 Project Model
- [x] Create Project model
- [x] Add UUID primary key
- [x] Add name field
- [x] Add description field
- [x] Add project_type field (personal/business/team)
- [x] Add owner ForeignKey
- [x] Add currency field
- [x] Add budget field
- [x] Add start_date and end_date fields
- [x] Add is_active and is_archived fields
- [x] Add timestamps
- [x] Create indexes (owner, project_type)
- [x] Create and run migrations
- [x] **Unit Testing:**
  - [x] Test project creation
  - [x] Test field validations
  - [x] Test owner relationship
  - [x] Test default values
  - [x] Test string representation
  - [x] Coverage: >80%

#### 3.2 Project CRUD Endpoints
- [x] Create ProjectSerializer
- [x] Create list projects endpoint (GET /api/v1/projects/)
- [x] Create create project endpoint (POST /api/v1/projects/)
- [x] Create get project endpoint (GET /api/v1/projects/{id}/)
- [x] Create update project endpoint (PATCH /api/v1/projects/{id}/)
- [x] Create delete project endpoint (DELETE /api/v1/projects/{id}/)
- [x] Create archive project endpoint (POST /api/v1/projects/{id}/archive/)
- [x] Implement pagination
- [x] Implement filtering (project_type, is_active)
- [x] **Unit Testing:**
  - [x] Test serializer validations
  - [x] Test budget validation (positive number)
  - [x] Test date validations
  - [x] Coverage: >80%
- [x] **API Testing:**
  - [x] Test create project (authenticated user)
  - [x] Test create project (unauthenticated - expect 401)
  - [x] Test list user's projects
  - [x] Test get project details (owner)
  - [x] Test get project details (non-member - expect 403)
  - [x] Test update project (owner)
  - [x] Test update project (non-owner - expect 403)
  - [x] Test delete project (owner)
  - [x] Test delete project (non-owner - expect 403)
  - [x] Test archive project
  - [x] Test project filtering
  - [x] Test pagination
  - [ ] **Edge Cases:**
    - [x] Test create project with empty name
    - [ ] Test create project with extremely long name (>255 chars)
    - [x] Test create project with negative budget
    - [x] Test create project with end_date before start_date
    - [ ] Test create project with invalid currency code
    - [ ] Test create project with SQL injection in fields
    - [ ] Test update archived project
    - [ ] Test delete project with active members (should cascade or prevent?)
    - [ ] Test delete project with transactions (should prevent or cascade?)
    - [x] Test accessing deleted/non-existent project (expect 404)
    - [ ] Test list projects with invalid pagination params
    - [ ] Test filter with invalid project_type
    - [ ] Test concurrent project updates (race condition)
    - [ ] Test creating 100+ projects (performance)
  - [x] Coverage: >80%

#### 3.3 Project Members & Permissions
- [x] Create ProjectMember model
- [x] Add role field (owner/admin/member/viewer)
- [x] Add permission fields (can_create_transactions, etc.)
- [x] Add invited_by field
- [x] Add unique constraint (project, user)
- [x] Create and run migrations
- [x] Create custom permission classes
- [x] **Unit Testing:**
  - [x] Test member creation
  - [x] Test unique constraint
  - [x] Test role validation
  - [x] Test permission defaults
  - [x] Coverage: >80%

#### 3.4 Project Member Management Endpoints
- [x] Create ProjectMemberSerializer
- [x] Create list members endpoint (GET /api/v1/projects/{id}/members/)
- [x] Create update member role endpoint (PATCH /api/v1/projects/{id}/members/{member_id}/)
- [x] Create remove member endpoint (DELETE /api/v1/projects/{id}/members/{member_id}/)
- [x] Create leave project endpoint (POST /api/v1/projects/{id}/members/leave/)
- [x] Implement permission checks
- [x] **Unit Testing:**
  - [x] Test permission check functions
  - [x] Test role validation
  - [x] Coverage: >80%
- [x] **API Testing:**
  - [x] Test list members (project member)
  - [x] Test list members (non-member - expect 403)
  - [x] Test update member role (admin/owner only)
  - [x] Test update member role (member - expect 403)
  - [x] Test remove member (admin/owner only)
  - [x] Test leave project
  - [x] Test owner cannot leave project (expect 400)
  - [ ] **Edge Cases:**
    - [x] Test update non-existent member (expect 404)
    - [ ] Test update member with invalid role
    - [x] Test remove project owner (should fail)
    - [ ] Test remove last admin (should warn or prevent?)
    - [ ] Test member leaving project with pending transactions
    - [ ] Test concurrent member updates
    - [ ] Test downgrading own role (owner → member)
    - [ ] Test updating member to same role (idempotent)
    - [ ] Test removing already removed member
    - [ ] Test member with UUID that's not a valid user
  - [x] Coverage: >80%

---

### Phase 4: Invitations Module

#### 4.1 Invitation Model
- [x] Create Invitation model
- [x] Add project ForeignKey
- [x] Add email field
- [x] Add role field
- [x] Add invited_by ForeignKey
- [x] Add token field (unique)
- [x] Add status field (pending/accepted/declined/expired)
- [x] Add expires_at field
- [x] Add unique constraint (project, email, status)
- [x] Create and run migrations
- [x] **Unit Testing:**
  - [x] Test invitation creation
  - [x] Test token generation
  - [x] Test expiration logic
  - [x] Coverage: >80%

#### 4.2 Invitation Endpoints
- [x] Create InvitationSerializer
- [x] Create invite member endpoint (POST /api/v1/projects/{id}/members/invite/)
- [x] Create list user invitations endpoint (GET /api/v1/invitations/)
- [x] Create accept invitation endpoint (POST /api/v1/invitations/{token}/accept/)
- [x] Create decline invitation endpoint (POST /api/v1/invitations/{token}/decline/)
- [x] Send invitation email
- [x] Implement token expiration check (7 days)
- [ ] **Unit Testing:**
  - [ ] Test invitation email sending
  - [ ] Test token validation
  - [ ] Coverage: >80%
- [x] **API Testing:**
  - [x] Test send invitation (admin/owner)
  - [x] Test send invitation (member - expect 403)
  - [ ] Test duplicate invitation (expect 400)
  - [x] Test list user invitations
  - [x] Test accept invitation (creates ProjectMember)
  - [x] Test accept expired invitation (expect 400)
  - [x] Test decline invitation
  - [x] Test invalid token (expect 404)
  - [ ] **Edge Cases:**
    - [x] Test invite existing project member
    - [x] Test invite with invalid email format
    - [x] Test invite user who's already in the project
    - [x] Test accept invitation when already a member
    - [ ] Test accept invitation for deleted project
    - [ ] Test accept invitation after being removed from project
    - [x] Test multiple pending invitations to same email
    - [ ] Test invitation token collision (extremely rare)
    - [x] Test accepting invitation while unauthenticated
    - [ ] Test inviting 100+ users at once (performance)
    - [ ] Test invitation expiration boundary (exactly 7 days)
    - [x] Test resend invitation (should invalidate old token)
    - [ ] Test invitation to non-registered email
  - [x] Coverage: >80%

---

### Phase 5: Categories Module

#### 5.1 Category Model
- [ ] Create Category model
- [ ] Add name field
- [ ] Add category_type field (income/expense)
- [ ] Add icon field
- [ ] Add color field
- [ ] Add project ForeignKey (nullable for defaults)
- [ ] Add is_default field
- [ ] Create indexes
- [ ] Create and run migrations
- [ ] Create default categories migration
- [ ] **Unit Testing:**
  - [ ] Test category creation
  - [ ] Test category_type validation
  - [ ] Test default categories
  - [ ] Coverage: >80%

#### 5.2 Category Endpoints
- [ ] Create CategorySerializer
- [ ] Create list categories endpoint (GET /api/v1/projects/{id}/categories/)
- [ ] Create create category endpoint (POST /api/v1/projects/{id}/categories/)
- [ ] Create update category endpoint (PATCH /api/v1/projects/{id}/categories/{cat_id}/)
- [ ] Create delete category endpoint (DELETE /api/v1/projects/{id}/categories/{cat_id}/)
- [ ] Create get default categories endpoint (GET /api/v1/categories/defaults/)
- [ ] Prevent deletion of categories with transactions
- [ ] **Unit Testing:**
  - [ ] Test serializer validations
  - [ ] Test color format validation
  - [ ] Coverage: >80%
- [ ] **API Testing:**
  - [ ] Test list project categories
  - [ ] Test create category (project member)
  - [ ] Test create category (non-member - expect 403)
  - [ ] Test update category
  - [ ] Test delete category (no transactions)
  - [ ] Test delete category with transactions (expect 400)
  - [ ] Test get default categories
  - [ ] **Edge Cases:**
    - [ ] Test create category with empty name
    - [ ] Test create category with duplicate name in same project
    - [ ] Test create category with invalid color format
    - [ ] Test create category with invalid category_type
    - [ ] Test create category with extremely long name (>100 chars)
    - [ ] Test update default category (should fail)
    - [ ] Test delete default category (should fail)
    - [ ] Test category with special characters in name
    - [ ] Test category with emoji in name/icon
    - [ ] Test list categories for non-existent project
    - [ ] Test assigning transaction to deleted category
  - [ ] Coverage: >80%

---

### Phase 6: Transactions Module

#### 6.1 Transaction Model
- [ ] Create Transaction model
- [ ] Add UUID primary key
- [ ] Add project ForeignKey
- [ ] Add transaction_type field (income/expense)
- [ ] Add amount field (DecimalField)
- [ ] Add currency field
- [ ] Add category ForeignKey
- [ ] Add title and description fields
- [ ] Add payment_method field
- [ ] Add transaction_date field
- [ ] Add created_by ForeignKey
- [ ] Add tags field (JSONField)
- [ ] Add is_recurring and recurring_frequency fields
- [ ] Add timestamps
- [ ] Create indexes
- [ ] Create and run migrations
- [ ] **Unit Testing:**
  - [ ] Test transaction creation
  - [ ] Test amount validation (positive)
  - [ ] Test decimal places (2)
  - [ ] Test field validations
  - [ ] Coverage: >80%

#### 6.2 Transaction CRUD Endpoints
- [ ] Create TransactionSerializer
- [ ] Create list transactions endpoint (GET /api/v1/projects/{id}/transactions/)
- [ ] Create create transaction endpoint (POST /api/v1/projects/{id}/transactions/)
- [ ] Create get transaction endpoint (GET /api/v1/projects/{id}/transactions/{txn_id}/)
- [ ] Create update transaction endpoint (PATCH /api/v1/projects/{id}/transactions/{txn_id}/)
- [ ] Create delete transaction endpoint (DELETE /api/v1/projects/{id}/transactions/{txn_id}/)
- [ ] Implement pagination
- [ ] Implement filtering (date range, category, type, payment_method)
- [ ] Implement search (title, description)
- [ ] Implement sorting (date, amount)
- [ ] **Unit Testing:**
  - [ ] Test serializer validations
  - [ ] Test amount validation
  - [ ] Test date validation
  - [ ] Test category relationship
  - [ ] Coverage: >80%
- [ ] **API Testing:**
  - [ ] Test create transaction (authorized member)
  - [ ] Test create transaction (viewer - expect 403)
  - [ ] Test create transaction (non-member - expect 403)
  - [ ] Test create with invalid amount (expect 400)
  - [ ] Test create with future date (allow or reject based on requirements)
  - [ ] Test list transactions (project member)
  - [ ] Test list transactions (non-member - expect 403)
  - [ ] Test get transaction details
  - [ ] Test update transaction (owner of transaction)
  - [ ] Test update transaction (different user - check permissions)
  - [ ] Test delete transaction (owner/admin)
  - [ ] Test delete transaction (member - expect 403)
  - [ ] Test filtering by date range
  - [ ] Test filtering by category
  - [ ] Test filtering by transaction type
  - [ ] Test search functionality
  - [ ] Test sorting
  - [ ] Test pagination
  - [ ] **Edge Cases:**
    - [ ] Test create transaction with zero amount (should fail?)
    - [ ] Test create transaction with negative amount (should fail)
    - [ ] Test create transaction with amount > 15 digits
    - [ ] Test create transaction with more than 2 decimal places
    - [ ] Test create transaction with invalid currency code
    - [ ] Test create transaction with non-existent category
    - [ ] Test create transaction with category from different project
    - [ ] Test create transaction with empty title
    - [ ] Test create transaction with extremely long title (>255 chars)
    - [ ] Test create transaction with SQL injection in description
    - [ ] Test create transaction with XSS in title/description
    - [ ] Test create transaction with invalid payment_method
    - [ ] Test create transaction with date far in past (e.g., year 1900)
    - [ ] Test create transaction with date far in future (e.g., year 3000)
    - [ ] Test create transaction with malformed tags (not a list)
    - [ ] Test create transaction with 1000+ tags
    - [ ] Test create transaction with is_recurring but no frequency
    - [ ] Test update transaction to different project (should fail)
    - [ ] Test update transaction category to incompatible type
    - [ ] Test concurrent transaction updates (race condition)
    - [ ] Test delete transaction that has documents attached
    - [ ] Test filtering with invalid date format
    - [ ] Test filtering with start_date > end_date
    - [ ] Test search with SQL injection
    - [ ] Test sorting with invalid field
    - [ ] Test pagination with page=0 or negative
    - [ ] Test pagination with extremely large page number
    - [ ] Test list with 10,000+ transactions (performance)
    - [ ] Test transaction with currency different from project currency
    - [ ] Test bulk operations (create/update/delete multiple)
  - [ ] Coverage: >80%

#### 6.3 Transaction Import/Export
- [ ] Create export endpoint (GET /api/v1/projects/{id}/transactions/export/)
- [ ] Support CSV format
- [ ] Support Excel format
- [ ] Create bulk import endpoint (POST /api/v1/projects/{id}/transactions/bulk-create/)
- [ ] Validate import data
- [ ] Handle import errors gracefully
- [ ] **Unit Testing:**
  - [ ] Test CSV generation
  - [ ] Test Excel generation
  - [ ] Test import validation
  - [ ] Coverage: >80%
- [ ] **API Testing:**
  - [ ] Test export to CSV
  - [ ] Test export to Excel
  - [ ] Test export with filters
  - [ ] Test bulk import (valid data)
  - [ ] Test bulk import (invalid data - expect partial success or rollback)
  - [ ] **Edge Cases:**
    - [ ] Test export with zero transactions
    - [ ] Test export with 10,000+ transactions (performance)
    - [ ] Test export with special characters in data
    - [ ] Test export with unicode characters
    - [ ] Test import with empty file
    - [ ] Test import with malformed CSV (missing columns)
    - [ ] Test import with wrong column headers
    - [ ] Test import with duplicate transactions
    - [ ] Test import with invalid date formats
    - [ ] Test import with invalid amount formats
    - [ ] Test import with missing required fields
    - [ ] Test import with non-existent categories
    - [ ] Test import file size limits (large file)
    - [ ] Test import with mixed valid/invalid rows
    - [ ] Test concurrent exports
    - [ ] Test export while transactions are being created
  - [ ] Coverage: >80%

---

### Phase 7: Documents Module

#### 7.1 Document Model
- [ ] Create Document model
- [ ] Add UUID primary key
- [ ] Add transaction ForeignKey
- [ ] Add file field (FileField)
- [ ] Add file_name field
- [ ] Add file_size field
- [ ] Add file_type field (MIME type)
- [ ] Add document_type field (receipt/invoice/contract/other)
- [ ] Add uploaded_by ForeignKey
- [ ] Add notes field
- [ ] Add uploaded_at timestamp
- [ ] Create and run migrations
- [ ] **Unit Testing:**
  - [ ] Test document creation
  - [ ] Test field validations
  - [ ] Coverage: >80%

#### 7.2 File Storage Configuration
- [ ] Configure AWS S3 or compatible storage
- [ ] Set up boto3
- [ ] Configure storage backend in settings
- [ ] Set up file upload path structure (documents/%Y/%m/)
- [ ] Configure file size limits (10MB max)
- [ ] Configure allowed file types
- [ ] **Unit Testing:**
  - [ ] Test storage configuration
  - [ ] Test file path generation
  - [ ] Coverage: >80%

#### 7.3 Document Endpoints
- [ ] Create DocumentSerializer
- [ ] Create list documents endpoint (GET /api/v1/transactions/{id}/documents/)
- [ ] Create upload document endpoint (POST /api/v1/transactions/{id}/documents/)
- [ ] Create get document endpoint (GET /api/v1/transactions/{id}/documents/{doc_id}/)
- [ ] Create delete document endpoint (DELETE /api/v1/transactions/{id}/documents/{doc_id}/)
- [ ] Create download endpoint (GET /api/v1/transactions/{id}/documents/{doc_id}/download/)
- [ ] Implement file type validation
- [ ] Implement file size validation
- [ ] Generate signed URLs for downloads
- [ ] **Unit Testing:**
  - [ ] Test file type validation
  - [ ] Test file size validation
  - [ ] Test serializer validations
  - [ ] Coverage: >80%
- [ ] **API Testing:**
  - [ ] Test upload document (valid file)
  - [ ] Test upload with invalid file type (expect 400)
  - [ ] Test upload with oversized file (expect 400)
  - [ ] Test list documents (transaction owner)
  - [ ] Test list documents (non-member - expect 403)
  - [ ] Test get document details
  - [ ] Test download document (signed URL)
  - [ ] Test delete document (owner/admin)
  - [ ] Test delete document (non-owner - expect 403)
  - [ ] **Edge Cases:**
    - [ ] Test upload zero-byte file
    - [ ] Test upload file exactly at size limit (10MB)
    - [ ] Test upload file slightly over limit (10MB + 1 byte)
    - [ ] Test upload with missing file
    - [ ] Test upload with corrupted file
    - [ ] Test upload executable file (.exe, .sh)
    - [ ] Test upload file with no extension
    - [ ] Test upload file with double extension (.pdf.exe)
    - [ ] Test upload with malicious file name (../../../etc/passwd)
    - [ ] Test upload with extremely long filename (>255 chars)
    - [ ] Test upload with unicode characters in filename
    - [ ] Test upload with special characters in filename
    - [ ] Test upload multiple documents simultaneously
    - [ ] Test upload document for non-existent transaction
    - [ ] Test upload document for deleted transaction
    - [ ] Test upload 100+ documents to one transaction
    - [ ] Test download with expired signed URL
    - [ ] Test download with tampered signed URL
    - [ ] Test delete document while it's being downloaded
    - [ ] Test concurrent document uploads
    - [ ] Test S3 connection failure during upload
    - [ ] Test disk space full scenario
    - [ ] Test upload with wrong content-type header
    - [ ] Test upload image disguised as PDF (content-type mismatch)
    - [ ] Test document orphaning (transaction deleted but document remains)
  - [ ] Coverage: >80%

---

### Phase 8: Budgets Module

#### 8.1 Budget Model
- [ ] Create Budget model
- [ ] Add UUID primary key
- [ ] Add project ForeignKey
- [ ] Add category ForeignKey (nullable)
- [ ] Add amount field
- [ ] Add period field (weekly/monthly/quarterly/yearly/custom)
- [ ] Add start_date and end_date fields
- [ ] Add alert_threshold field (default 80)
- [ ] Add alert_enabled field
- [ ] Add created_by ForeignKey
- [ ] Add timestamps
- [ ] Create and run migrations
- [ ] **Unit Testing:**
  - [ ] Test budget creation
  - [ ] Test date validations
  - [ ] Test amount validation
  - [ ] Coverage: >80%

#### 8.2 Budget Endpoints
- [ ] Create BudgetSerializer
- [ ] Create list budgets endpoint (GET /api/v1/projects/{id}/budgets/)
- [ ] Create create budget endpoint (POST /api/v1/projects/{id}/budgets/)
- [ ] Create update budget endpoint (PATCH /api/v1/projects/{id}/budgets/{bud_id}/)
- [ ] Create delete budget endpoint (DELETE /api/v1/projects/{id}/budgets/{bud_id}/)
- [ ] Create budget status endpoint (GET /api/v1/projects/{id}/budgets/status/)
- [ ] Implement budget calculation logic
- [ ] **Unit Testing:**
  - [ ] Test budget calculation
  - [ ] Test serializer validations
  - [ ] Coverage: >80%
- [ ] **API Testing:**
  - [ ] Test create budget (admin/owner)
  - [ ] Test create budget (member - expect 403)
  - [ ] Test list budgets
  - [ ] Test update budget
  - [ ] Test delete budget
  - [ ] Test budget status (shows spent vs allocated)
  - [ ] **Edge Cases:**
    - [ ] Test create budget with zero amount
    - [ ] Test create budget with negative amount
    - [ ] Test create budget with end_date before start_date
    - [ ] Test create budget with past dates
    - [ ] Test create overlapping budgets for same category
    - [ ] Test create budget for non-existent category
    - [ ] Test create budget with invalid period
    - [ ] Test create budget with alert_threshold > 100
    - [ ] Test create budget with alert_threshold < 0
    - [ ] Test update budget while transactions are being added
    - [ ] Test delete budget that has triggered alerts
    - [ ] Test budget status with zero transactions
    - [ ] Test budget status at exactly 100% spent
    - [ ] Test budget status with spending exceeding budget
    - [ ] Test multiple budgets for same time period
    - [ ] Test budget with no category (project-wide budget)
    - [ ] Test budget calculations with different currencies
    - [ ] Test budget expiration boundary conditions
  - [ ] Coverage: >80%

#### 8.3 Budget Alerts (Celery)
- [ ] Configure Celery
- [ ] Configure Celery Beat
- [ ] Create budget alert Celery task
- [ ] Implement budget threshold checking
- [ ] Send email alerts when threshold exceeded
- [ ] Schedule periodic task (daily)
- [ ] **Unit Testing:**
  - [ ] Test budget alert logic
  - [ ] Test threshold calculation
  - [ ] Test email sending
  - [ ] Coverage: >80%
- [ ] **Integration Testing:**
  - [ ] Test Celery task execution
  - [ ] Test periodic scheduling
  - [ ] Test alert email delivery
  - [ ] Coverage: >80%

---

### Phase 9: Reports & Analytics Module

#### 9.1 Reports Utilities
- [ ] Create summary calculation function
- [ ] Create category breakdown function
- [ ] Create trend analysis function
- [ ] Create period comparison function
- [ ] Implement caching for reports
- [ ] **Unit Testing:**
  - [ ] Test summary calculations
  - [ ] Test category breakdown
  - [ ] Test trend analysis
  - [ ] Test period comparison
  - [ ] Test with various date ranges
  - [ ] Coverage: >80%

#### 9.2 Reports Endpoints
- [ ] Create summary endpoint (GET /api/v1/projects/{id}/reports/summary/)
- [ ] Create trends endpoint (GET /api/v1/projects/{id}/reports/trends/)
- [ ] Create category breakdown endpoint (GET /api/v1/projects/{id}/reports/category-breakdown/)
- [ ] Create monthly report endpoint (GET /api/v1/projects/{id}/reports/monthly/)
- [ ] Create comparison endpoint (GET /api/v1/projects/{id}/reports/comparison/)
- [ ] Support date range filtering
- [ ] Implement cache invalidation on transaction changes
- [ ] **Unit Testing:**
  - [ ] Test report serializers
  - [ ] Test date range validation
  - [ ] Coverage: >80%
- [ ] **API Testing:**
  - [ ] Test get summary (project member)
  - [ ] Test get summary (non-member - expect 403)
  - [ ] Test summary with date range
  - [ ] Test trends report
  - [ ] Test category breakdown
  - [ ] Test monthly report
  - [ ] Test period comparison
  - [ ] Test caching (verify cache hit)
  - [ ] **Edge Cases:**
    - [ ] Test reports with zero transactions
    - [ ] Test reports with only income (no expenses)
    - [ ] Test reports with only expenses (no income)
    - [ ] Test reports with invalid date range (end before start)
    - [ ] Test reports with extremely wide date range (10+ years)
    - [ ] Test reports with future dates
    - [ ] Test reports with date range containing no data
    - [ ] Test category breakdown with uncategorized transactions
    - [ ] Test trends with insufficient data (< 2 periods)
    - [ ] Test comparison with non-existent previous period
    - [ ] Test reports with 10,000+ transactions (performance)
    - [ ] Test reports during transaction creation
    - [ ] Test cache invalidation timing
    - [ ] Test concurrent report generation
    - [ ] Test reports with mixed currencies
    - [ ] Test monthly report across year boundary (Dec-Jan)
    - [ ] Test reports with deleted categories
    - [ ] Test division by zero scenarios (100% increase, etc.)
  - [ ] Coverage: >80%

#### 9.3 Project Statistics
- [ ] Create project stats endpoint (GET /api/v1/projects/{id}/stats/)
- [ ] Include total transactions
- [ ] Include total income/expenses
- [ ] Include member count
- [ ] Include document count
- [ ] Include budget utilization
- [ ] **Unit Testing:**
  - [ ] Test stats calculation
  - [ ] Coverage: >80%
- [ ] **API Testing:**
  - [ ] Test get project stats
  - [ ] Verify all metrics are accurate
  - [ ] Coverage: >80%

---

### Phase 10: Activity Logs Module

#### 10.1 Activity Log Model
- [ ] Create ActivityLog model
- [ ] Add UUID primary key
- [ ] Add project ForeignKey
- [ ] Add user ForeignKey
- [ ] Add action_type field
- [ ] Add resource_type field
- [ ] Add resource_id field
- [ ] Add description field
- [ ] Add ip_address field
- [ ] Add user_agent field
- [ ] Add created_at timestamp
- [ ] Create indexes
- [ ] Create and run migrations
- [ ] **Unit Testing:**
  - [ ] Test log creation
  - [ ] Test field validations
  - [ ] Coverage: >80%

#### 10.2 Activity Logging Implementation
- [ ] Create log_activity helper function
- [ ] Integrate logging in transaction CRUD
- [ ] Integrate logging in member management
- [ ] Integrate logging in document operations
- [ ] Integrate logging in budget operations
- [ ] **Unit Testing:**
  - [ ] Test log creation on each action
  - [ ] Test log data accuracy
  - [ ] Coverage: >80%

#### 10.3 Activity Log Endpoints
- [ ] Create ActivityLogSerializer
- [ ] Create list activity logs endpoint (GET /api/v1/projects/{id}/activity/)
- [ ] Implement pagination
- [ ] Implement filtering (action_type, resource_type, date range)
- [ ] **API Testing:**
  - [ ] Test list activity logs (project member)
  - [ ] Test list activity logs (non-member - expect 403)
  - [ ] Test filtering by action type
  - [ ] Test filtering by date range
  - [ ] Test pagination
  - [ ] **Edge Cases:**
    - [ ] Test activity logs for deleted resources
    - [ ] Test activity logs for deleted users
    - [ ] Test activity logs with null user (system actions)
    - [ ] Test filtering with invalid action_type
    - [ ] Test filtering with invalid date format
    - [ ] Test pagination with extremely large datasets
    - [ ] Test log retention (old logs cleanup)
    - [ ] Test concurrent log creation
    - [ ] Test activity logs during mass deletion
    - [ ] Test activity logs with special characters in description
  - [ ] Coverage: >80%

---

### Phase 11: API Documentation

#### 11.1 OpenAPI/Swagger Setup
- [ ] Install drf-spectacular
- [ ] Configure drf-spectacular settings
- [ ] Add schema generation endpoint
- [ ] Add Swagger UI endpoint
- [ ] Add ReDoc endpoint (optional)
- [ ] **Testing:**
  - [ ] Verify schema generation works
  - [ ] Verify Swagger UI loads
  - [ ] Test API calls from Swagger UI

#### 11.2 Documentation Enhancement
- [ ] Add docstrings to all API views
- [ ] Add schema examples for requests
- [ ] Add schema examples for responses
- [ ] Document error responses
- [ ] Document authentication requirements
- [ ] Add API overview documentation
- [ ] **Testing:**
  - [ ] Review all endpoint documentation
  - [ ] Verify examples are accurate
  - [ ] Test example requests

---

### Phase 12: Performance & Optimization

#### 12.1 Database Optimization
- [ ] Review and optimize indexes
- [ ] Implement select_related where needed
- [ ] Implement prefetch_related where needed
- [ ] Add database query logging
- [ ] Identify and fix N+1 queries
- [ ] **Testing:**
  - [ ] Run Django Debug Toolbar
  - [ ] Measure query counts per endpoint
  - [ ] Verify no N+1 queries

#### 12.2 Caching Implementation
- [ ] Configure Redis caching
- [ ] Cache project summaries
- [ ] Cache budget status
- [ ] Cache category lists
- [ ] Implement cache invalidation
- [ ] **Testing:**
  - [ ] Test cache hit/miss
  - [ ] Test cache invalidation
  - [ ] Measure performance improvement

#### 12.3 Rate Limiting
- [ ] Install django-ratelimit
- [ ] Add rate limiting to auth endpoints
- [ ] Add rate limiting to API endpoints
- [ ] Add rate limiting to file uploads
- [ ] **Testing:**
  - [ ] Test rate limit enforcement
  - [ ] Test rate limit headers
  - [ ] Test rate limit reset

---

### Phase 13: Security Hardening

#### 13.1 Security Configuration
- [ ] Configure HTTPS enforcement
- [ ] Configure CORS settings
- [ ] Configure CSRF protection
- [ ] Set secure cookie settings
- [ ] Configure password validators
- [ ] Set up security headers
- [ ] **Testing:**
  - [ ] Run Django security check
  - [ ] Test CORS configuration
  - [ ] Test CSRF protection

#### 13.2 Input Validation & Sanitization
- [ ] Review all serializer validations
- [ ] Add custom validators where needed
- [ ] Sanitize file uploads
- [ ] Validate file types strictly
- [ ] Implement file size limits
- [ ] **Testing:**
  - [ ] Test malicious file upload attempts
  - [ ] Test SQL injection attempts
  - [ ] Test XSS attempts

#### 13.3 Permission Testing
- [ ] Audit all permission checks
- [ ] Test unauthorized access attempts
- [ ] Test privilege escalation attempts
- [ ] Test cross-project access attempts
- [ ] **Testing:**
  - [ ] Comprehensive permission tests
  - [ ] Test every endpoint with wrong user
  - [ ] Test every endpoint without auth

---

### Phase 14: Deployment & DevOps

#### 14.1 Production Configuration
- [ ] Create production settings file
- [ ] Configure production database
- [ ] Configure production Redis
- [ ] Configure production S3/storage
- [ ] Set up production environment variables
- [ ] Configure Gunicorn
- [ ] Configure Nginx
- [ ] Set up SSL certificates
- [ ] **Testing:**
  - [ ] Test production build
  - [ ] Test production settings
  - [ ] Test all services in production mode

#### 14.2 CI/CD Pipeline
- [ ] Create GitHub Actions workflow
- [ ] Configure test job
- [ ] Configure PostgreSQL service
- [ ] Configure Redis service
- [ ] Run tests on push
- [ ] Run tests on pull request
- [ ] Configure code coverage reporting
- [ ] Configure deploy job (production)
- [ ] **Testing:**
  - [ ] Test workflow execution
  - [ ] Verify all tests pass in CI
  - [ ] Test deployment process

#### 14.3 Monitoring & Logging
- [ ] Set up application logging
- [ ] Configure log rotation
- [ ] Set up error tracking (Sentry optional)
- [ ] Configure monitoring (optional)
- [ ] Set up database backup automation
- [ ] **Testing:**
  - [ ] Verify logs are being written
  - [ ] Test log rotation
  - [ ] Test error notifications

---

### Phase 15: Final Testing & QA

#### 15.1 Comprehensive Testing
- [ ] Run full test suite
- [ ] Verify >80% code coverage
- [ ] Fix all failing tests
- [ ] Review test quality
- [ ] **Overall Coverage Check:**
  - [ ] Authentication module: >80%
  - [ ] Projects module: >80%
  - [ ] Transactions module: >80%
  - [ ] Documents module: >80%
  - [ ] Budgets module: >80%
  - [ ] Reports module: >80%
  - [ ] Activity logs module: >80%
  - [ ] Overall project: >80%

#### 15.2 Integration Testing
- [ ] Test complete user workflows
- [ ] Test multi-user collaboration
- [ ] Test file upload/download flow
- [ ] Test budget alert system
- [ ] Test report generation
- [ ] **Workflow Tests:**
  - [ ] User registration → email verification → login
  - [ ] Create project → invite member → member joins
  - [ ] Create transaction → upload receipt → view in report
  - [ ] Set budget → exceed threshold → receive alert
  - [ ] Export transactions → import to new project

#### 15.3 Performance Testing
- [ ] Load test API endpoints
- [ ] Test with 100+ concurrent users
- [ ] Measure response times (target <500ms)
- [ ] Test database under load
- [ ] Test file upload under load
- [ ] **Performance Checks:**
  - [ ] List transactions: <500ms
  - [ ] Create transaction: <300ms
  - [ ] Generate report: <2s
  - [ ] Upload document: <3s

#### 15.4 Security Audit
- [ ] Run security vulnerability scan
- [ ] Test all authentication flows
- [ ] Test all authorization checks
- [ ] Review sensitive data handling
- [ ] Test rate limiting
- [ ] **Security Checklist:**
  - [ ] No exposed credentials
  - [ ] No SQL injection vulnerabilities
  - [ ] No XSS vulnerabilities
  - [ ] No CSRF vulnerabilities
  - [ ] Secure file upload handling
  - [ ] Proper permission checks everywhere

#### 15.5 Edge Case & Boundary Testing
- [ ] **Data Validation Edge Cases:**
  - [ ] Test all numeric fields with: zero, negative, max value, min value, decimal precision
  - [ ] Test all string fields with: empty, whitespace only, max length, max length + 1, unicode, special characters
  - [ ] Test all date fields with: today, past, future, invalid format, leap year dates, timezone boundaries
  - [ ] Test all enum fields with: valid values, invalid values, null, empty string
  - [ ] Test all optional fields with: null, undefined, empty
  - [ ] Test all UUID fields with: valid UUID, invalid UUID, malformed UUID, empty string
  
- [ ] **Relationship & Constraint Edge Cases:**
  - [ ] Test foreign key constraints: delete parent with children, update cascades, orphaned records
  - [ ] Test unique constraints: duplicate entries, case sensitivity, concurrent creates
  - [ ] Test check constraints: boundary values, validation rules
  - [ ] Test composite unique constraints: all combinations
  
- [ ] **Concurrency & Race Conditions:**
  - [ ] Test simultaneous user registrations with same email
  - [ ] Test concurrent transaction updates to same record
  - [ ] Test concurrent project deletions
  - [ ] Test concurrent budget threshold checks
  - [ ] Test concurrent document uploads to same transaction
  - [ ] Test race conditions in invitation acceptance
  - [ ] Test race conditions in member role updates
  
- [ ] **State Transition Edge Cases:**
  - [ ] Test invalid state transitions (e.g., archived → active → archived)
  - [ ] Test operations on deleted records
  - [ ] Test operations on archived projects
  - [ ] Test operations after user account deletion
  - [ ] Test operations during background job processing
  
- [ ] **Pagination & Listing Edge Cases:**
  - [ ] Test page=0, page=-1, page=999999
  - [ ] Test page_size=0, page_size=-1, page_size=10000
  - [ ] Test empty result sets
  - [ ] Test single item result sets
  - [ ] Test result sets at exact page boundaries
  
- [ ] **API Request Edge Cases:**
  - [ ] Test with missing required headers
  - [ ] Test with invalid content-type
  - [ ] Test with malformed JSON
  - [ ] Test with extremely large payloads (>1MB)
  - [ ] Test with empty request body when data expected
  - [ ] Test with extra unexpected fields in payload
  - [ ] Test with null values in required fields
  
- [ ] **File Operations Edge Cases:**
  - [ ] Test file operations with network interruption
  - [ ] Test file operations with storage quota exceeded
  - [ ] Test file operations with invalid permissions
  - [ ] Test file operations with read-only storage
  - [ ] Test simultaneous upload/download of same file
  - [ ] Test file deletion while download in progress
  
- [ ] **Database Edge Cases:**
  - [ ] Test with database connection lost
  - [ ] Test with database at max connections
  - [ ] Test with slow database queries (timeout scenarios)
  - [ ] Test with database in read-only mode
  - [ ] Test transaction rollback scenarios
  - [ ] Test deadlock scenarios
  
- [ ] **Cache Edge Cases:**
  - [ ] Test with cache unavailable (Redis down)
  - [ ] Test with cache full
  - [ ] Test cache eviction scenarios
  - [ ] Test stale cache data
  - [ ] Test cache key collisions
  
- [ ] **Email Edge Cases:**
  - [ ] Test email sending when SMTP server down
  - [ ] Test email with invalid recipient address
  - [ ] Test email rate limiting
  - [ ] Test email template rendering errors
  - [ ] Test extremely long email content
  
- [ ] **Background Job Edge Cases:**
  - [ ] Test Celery worker failure during task
  - [ ] Test task retry logic (max retries)
  - [ ] Test task timeout scenarios
  - [ ] Test task result expiration
  - [ ] Test scheduled tasks at DST boundaries
  
- [ ] **Authentication Edge Cases:**
  - [ ] Test with expired tokens at exact expiration time
  - [ ] Test with token refresh during user deletion
  - [ ] Test with token blacklist cleanup
  - [ ] Test with multiple active sessions
  - [ ] Test with token issued before password change
  
- [ ] **Permission Edge Cases:**
  - [ ] Test permission changes while user has active request
  - [ ] Test resource access after permission revoked
  - [ ] Test permission inheritance scenarios
  - [ ] Test conflicting permissions (if any)
  
- [ ] **Business Logic Edge Cases:**
  - [ ] Test budget alerts at exactly threshold (80%)
  - [ ] Test budget alerts when multiple budgets trigger simultaneously
  - [ ] Test report generation with mixed timezones
  - [ ] Test currency calculations with extreme precision
  - [ ] Test negative net income scenarios
  - [ ] Test zero-transaction projects in reports
  
- [ ] **Error Handling Edge Cases:**
  - [ ] Test graceful degradation when external services fail
  - [ ] Test error messages don't leak sensitive information
  - [ ] Test consistent error response format
  - [ ] Test error logging without sensitive data
  - [ ] Test 500 errors return appropriate responses
  
- [ ] **Localization & Internationalization Edge Cases:**
  - [ ] Test with non-English characters in all text fields
  - [ ] Test with right-to-left languages
  - [ ] Test with emoji in text fields
  - [ ] Test timezone edge cases (UTC boundaries)
  - [ ] Test date formatting across different locales
  
- [ ] **Security Edge Cases:**
  - [ ] Test with manipulated JWT payloads
  - [ ] Test with SQL injection in every input field
  - [ ] Test with XSS payloads in every text field
  - [ ] Test with CSRF token manipulation
  - [ ] Test with session fixation attempts
  - [ ] Test with header injection attempts
  - [ ] Test with path traversal attempts
  - [ ] Test with XXE (XML External Entity) attacks if XML used
  - [ ] Test with timing attacks on authentication
  
- [ ] **Network & Infrastructure Edge Cases:**
  - [ ] Test with slow network connections
  - [ ] Test with interrupted connections
  - [ ] Test with proxy servers
  - [ ] Test with various user agents
  - [ ] Test with IPv4 and IPv6
  - [ ] Test with load balancer scenarios
  
- [ ] **Data Migration Edge Cases:**
  - [ ] Test with existing data during schema changes
  - [ ] Test rollback scenarios
  - [ ] Test data integrity after migration
  - [ ] Test with large datasets during migration

---

### Phase 16: Documentation & Launch

#### 16.1 Documentation
- [ ] Write README.md
- [ ] Document installation steps
- [ ] Document environment variables
- [ ] Document deployment process
- [ ] Create API usage examples
- [ ] Document testing procedures
- [ ] Create troubleshooting guide

#### 16.2 Launch Checklist
- [ ] All tests passing
- [ ] Code coverage >80%
- [ ] API documentation complete
- [ ] Production environment configured
- [ ] Database migrations applied
- [ ] SSL certificates installed
- [ ] Monitoring configured
- [ ] Backup system configured
- [ ] CI/CD pipeline working
- [ ] Security hardening complete

---

## 15. Overall Acceptance Criteria

### MVP Must Have (Summary):
- [ ] User authentication system (registration, login, email verification, password reset)
- [ ] Project management (create, update, delete, archive)
- [ ] Team collaboration (invite members, assign roles, manage permissions)
- [ ] Transaction tracking (income and expenses with categories)
- [ ] Document management (upload, download, delete receipts)
- [ ] Financial reports and analytics
- [ ] Budget tracking with alerts
- [ ] Activity logging
- [ ] API documentation (Swagger)
- [ ] Test coverage >80%
- [ ] Production deployment ready
- [ ] CI/CD pipeline functional

### Quality Gates:
- [ ] **All unit tests passing** (>80% coverage per module)
- [ ] **All API tests passing** (>80% coverage per module)
- [ ] **No critical security vulnerabilities**
- [ ] **Performance targets met** (<500ms response time)
- [ ] **Code review completed**
- [ ] **Documentation complete**

---

## Testing Strategy Summary

### Testing Approach:
1. **Test-After-Feature:** Complete unit tests and API tests immediately after implementing each feature
2. **Coverage Target:** >80% for each module before moving to next module
3. **Test Types:**
   - Unit tests for models, serializers, utilities
   - API tests for all endpoints
   - Integration tests for workflows
   - Performance tests for load handling
4. **Quality Assurance:** No feature is considered complete until tests are written and passing

### Test Execution Commands:
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run specific module tests
pytest apps/authentication/tests.py
pytest apps/projects/tests.py

# Run API tests only
pytest -k "API"

# Run with verbose output
pytest -v
```

---

## 15. Project Structure

```
expense-tracker-backend/
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── authentication/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── projects/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── permissions.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── transactions/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── filters.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── documents/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── utils.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── budgets/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── tasks.py  # Celery tasks
│   │   ├── urls.py
│   │   └── tests.py
│   ├── reports/
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── utils.py
│   │   ├── urls.py
│   │   └── tests.py
│   └── common/
│       ├── models.py  # ActivityLog, etc.
│       ├── permissions.py
│       ├── pagination.py
│       ├── exceptions.py
│       └── utils.py
├── media/  # Local development only
├── static/
├── logs/
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx/
│       └── nginx.conf
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── manage.py
├── pytest.ini
├── .env.example
├── .gitignore
└── README.md
```

---

## 16. Development Timeline

### Sprint 1 (Week 1-2): Foundation
- Project setup (Django, PostgreSQL, Redis)
- User authentication (registration, login, JWT)
- Basic project CRUD
- Docker configuration

### Sprint 2 (Week 3-4): Core Features
- Transaction CRUD
- Categories management
- Project members and invitations
- Permission system

### Sprint 3 (Week 5-6): Documents & Reports
- Document upload/download
- File storage (S3)
- Basic reports (summary, category breakdown)
- Budget tracking

### Sprint 4 (Week 7-8): Polish & Testing
- Activity logs
- Comprehensive testing
- API documentation
- Bug fixes and optimization
- Deployment setup

### Total Duration: 8 weeks for MVP

---

## 17. Success Metrics

### Technical Metrics
- API uptime: 99.9%
- Average response time: < 500ms
- Test coverage: > 80%
- Zero critical security vulnerabilities

### Business Metrics
- User registration: Track daily signups
- Project creation: Average per user
- Transaction volume: Daily/monthly totals
- Document uploads: Success rate
- User retention: 30-day active users

### User Experience Metrics
- API error rate: < 1%
- Average transaction creation time: < 30 seconds
- Report generation time: < 2 seconds
- File upload success rate: > 99%

---

## 18. Risk Mitigation

### Technical Risks
1. **File Storage Costs:**
   - Mitigation: Set file size limits, implement cleanup for deleted transactions
   
2. **Database Performance:**
   - Mitigation: Proper indexing, query optimization, caching
   
3. **API Rate Limiting:**
   - Mitigation: Implement rate limiting, monitor usage patterns

### Security Risks
1. **Unauthorized Access:**
   - Mitigation: Strong JWT implementation, permission checks on every endpoint
   
2. **File Upload Vulnerabilities:**
   - Mitigation: File type validation, size limits, malware scanning
   
3. **Data Breaches:**
   - Mitigation: Encryption at rest and in transit, regular security audits

### Business Risks
1. **User Adoption:**
   - Mitigation: Focus on UX, comprehensive documentation, tutorials
   
2. **Scalability:**
   - Mitigation: Cloud infrastructure, horizontal scaling capability

---

## 19. Support & Maintenance

### Ongoing Tasks
- Monitor error logs daily
- Review security patches weekly
- Database backups (daily)
- Performance optimization (monthly)
- Dependency updates (monthly)
- User feedback review (weekly)

### Backup Strategy
- **Database:** Daily automated backups, 30-day retention
- **Files:** S3 versioning enabled, lifecycle policies
- **Code:** Git repository with tagged releases

---

## 20. Conclusion

This PRD provides a comprehensive blueprint for building the Expense Tracker MVP backend. The focus is on creating a robust, scalable foundation that supports the core features while allowing for incremental feature additions in future phases.

**Key Deliverables:**
1. RESTful API with full CRUD operations
2. Multi-user collaboration with role-based permissions
3. Document upload and management
4. Financial reports and analytics
5. Budget tracking with alerts
6. Comprehensive API documentation
7. Test coverage > 80%
8. Production-ready Docker deployment

**Next Steps:**
1. Review and approve PRD
2. Set up development environment
3. Initialize Django project structure
4. Begin Sprint 1 development
5. Regular sprint reviews and iterations

---

**Document Version Control:**
- v1.0 - March 12, 2026 - Initial PRD creation
- Future updates will be tracked here

**Prepared for:** Claude Code Development  
**Prepared by:** Backend Architecture Team
