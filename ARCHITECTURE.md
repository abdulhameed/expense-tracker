# System Architecture Documentation

## Overview

The Expense Tracker API is a scalable, production-ready REST API built with Django and Django REST Framework. It follows clean architecture principles with clear separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Layer                             │
│  (Web, Mobile, Third-party Integrations)                   │
└────────────┬────────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────────┐
│                  API Layer (DRF)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  ViewSets   │  │  Serializers │  │  Permissions │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────┬────────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────────┐
│              Business Logic Layer                           │
│  ┌────────────┐  ┌───────────┐  ┌──────────────┐          │
│  │   Models   │  │  Services │  │  Validators  │          │
│  └────────────┘  └───────────┘  └──────────────┘          │
└────────────┬────────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────────┐
│         Data Access & Integration Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐      │
│  │  ORM Query   │  │ Celery Tasks │  │ Cache Ops   │      │
│  └──────────────┘  └──────────────┘  └─────────────┘      │
└────────────┬────────────────────────────────────────────────┘
             │
     ┌───────┴────────┬──────────────┬──────────────┐
     │                │              │              │
┌────▼────┐  ┌────────▼──┐  ┌──────▼───┐  ┌─────▼──┐
│PostgreSQL│  │   Redis   │  │  Celery  │  │  S3    │
│ Database │  │   Cache   │  │  Queue   │  │Storage │
└──────────┘  └───────────┘  └──────────┘  └────────┘
```

## Technology Stack

### Backend Framework
- **Django 5.1.7**: Web framework
- **Django REST Framework 3.15.2**: API framework
- **Python 3.10+**: Programming language

### Database & Storage
- **PostgreSQL 16**: Relational database
- **Redis 7**: Cache and message broker
- **AWS S3 (optional)**: File storage

### Task Queue
- **Celery 5.4.0**: Asynchronous task processing
- **Celery Beat**: Periodic task scheduling

### Authentication & Security
- **SimpleJWT 5.3.1**: JWT token authentication
- **bcrypt**: Password hashing
- **Bleach 6.1.0**: HTML sanitization

### API Documentation
- **drf-spectacular 0.27.2**: OpenAPI schema generation
- **Swagger UI**: Interactive API documentation

### Testing
- **pytest 7.4**: Test framework
- **pytest-django 4.5**: Django integration
- **Factory Boy 3.3**: Test data generation
- **Locust 2.17**: Load testing

## Directory Structure

```
expense-tracker/
├── apps/                          # Application modules
│   ├── authentication/            # User management & JWT
│   │   ├── models.py             # User model
│   │   ├── serializers.py        # User serializers
│   │   ├── views.py              # Auth endpoints
│   │   ├── permissions.py        # Custom permissions
│   │   └── tests/
│   │
│   ├── projects/                 # Project management
│   │   ├── models.py             # Project model
│   │   ├── serializers.py        # Project serializers
│   │   ├── views.py              # Project viewsets
│   │   ├── filters.py            # Filtering logic
│   │   └── tests/
│   │
│   ├── transactions/             # Transaction tracking
│   │   ├── models.py             # Transaction model
│   │   ├── serializers.py        # Transaction serializers
│   │   ├── views.py              # Transaction viewsets
│   │   ├── filters.py            # Filtering & search
│   │   ├── tasks.py              # Celery tasks
│   │   └── tests/
│   │
│   ├── categories/               # Category management
│   ├── budgets/                  # Budget tracking
│   ├── documents/                # File uploads
│   ├── reports/                  # Financial analytics
│   ├── activity/                 # Audit logging
│   ├── security/                 # Security utilities
│   ├── health/                   # Health checks
│   └── utils/                    # Shared utilities
│
├── config/                        # Project configuration
│   ├── settings/
│   │   ├── base.py               # Base settings
│   │   ├── development.py        # Development settings
│   │   ├── production.py         # Production settings
│   │   └── testing.py            # Test settings
│   ├── urls.py                   # URL routing
│   ├── wsgi.py                   # WSGI application
│   ├── gunicorn.py               # Gunicorn config
│   └── nginx.conf                # Nginx config
│
├── tests/                         # Test suite
│   ├── load_test.py              # Load testing
│   ├── security_test.py          # Security tests
│   └── test_e2e_workflows.py     # E2E tests
│
├── requirements/                  # Dependencies
│   ├── base.txt                  # Base dependencies
│   ├── development.txt           # Development dependencies
│   └── production.txt            # Production dependencies
│
├── docker-compose.yml            # Docker compose
├── Dockerfile                    # Production image
├── manage.py                     # Django management
└── README.md                     # Project documentation
```

## Core Components

### 1. Models (Data Layer)

**Entity Relationship Diagram**

```
┌──────────┐
│   User   │ (Django default)
└────┬─────┘
     │
     │ (1:N)
     │
┌────▼──────────┐     (1:N)    ┌─────────────┐
│   Project    │◄────────────────┤ Transaction │
└────┬──────────┘                └─────────────┘
     │                                  │
     │ (1:N)                            │ (M:1)
     │                                  │
┌────▼──────────┐     (1:N)    ┌───────▼────────┐
│   Budget     │◄────────────────┤   Category    │
└────┬──────────┘                └───────────────┘
     │
     │ (1:N)
     │
┌────▼──────────┐
│  Document    │
└──────────────┘

┌──────────────┐     (M:N)     ┌──────────────┐
│ ProjectMember│◄────────────────┤  Invitation  │
└──────────────┘                 └──────────────┘

┌──────────────┐     (1:N)     ┌──────────────┐
│  ActivityLog │◄────────────────┤   Any Model  │
└──────────────┘                 └──────────────┘
```

### 2. API Layer (ViewSets & Serializers)

**Request/Response Flow**

```
Request
   ↓
URL Router (urls.py)
   ↓
ViewSet/View
   ↓
Serializer (Validation & Transformation)
   ↓
Permission Checks
   ↓
Business Logic
   ↓
Database Query (ORM)
   ↓
Response Serializer
   ↓
Response
```

### 3. Middleware & Utilities

**Request Processing Pipeline**

```
┌─────────────┐
│   Request   │
└──────┬──────┘
       │
┌──────▼──────────────────────────┐
│  Django Middleware               │
│  - Security Headers              │
│  - CORS                          │
│  - Session Management            │
└──────┬──────────────────────────┘
       │
┌──────▼──────────────────────────┐
│  DRF Middleware                 │
│  - Authentication                │
│  - Throttling/Rate Limiting      │
│  - Versioning                    │
└──────┬──────────────────────────┘
       │
┌──────▼──────────────────────────┐
│  View Processing                │
│  - Deserialization               │
│  - Validation                    │
│  - Permission Checks             │
│  - Business Logic                │
└──────┬──────────────────────────┘
       │
┌──────▼──────────────────────────┐
│  Serialization                  │
│  - Model to JSON                 │
│  - Field Formatting              │
└──────┬──────────────────────────┘
       │
┌──────▼──────────────────────────┐
│  Response                       │
└─────────────────────────────────┘
```

## Authentication & Authorization

### Authentication Flow

```
1. User Registration
   POST /api/v1/auth/register/
   {email, password}
        ↓
   Create User (bcrypt hash)
        ↓
   Return {id, email}

2. User Login
   POST /api/v1/auth/login/
   {email, password}
        ↓
   Verify Password
        ↓
   Generate JWT Tokens
        ↓
   Return {access, refresh}

3. API Request
   GET /api/v1/projects/
   Header: Authorization: Bearer {access_token}
        ↓
   Verify JWT Signature
        ↓
   Check Token Expiration
        ↓
   Set request.user
        ↓
   Process Request

4. Token Refresh
   POST /api/v1/auth/refresh/
   {refresh_token}
        ↓
   Verify Refresh Token
        ↓
   Generate New Access Token
        ↓
   Blacklist Old Token
        ↓
   Return {access}
```

### Authorization Levels

```
1. Authentication Required
   - Most endpoints require valid JWT token
   - Exceptions: register, login, health checks

2. Object-Level Permissions
   - Users can only access their own projects
   - Users can only access shared/collaborative projects
   - Team members have project-specific permissions

3. Resource Ownership
   - Projects owned by creator
   - Transactions belong to project
   - Budgets belong to project
   - Documents linked to transactions
```

## Data Flow Architecture

### Transaction Creation Flow

```
Client Request
     ↓
POST /api/v1/transactions/
{amount, category, date, description, project}
     ↓
TransactionSerializer.validate()
- Check decimal precision
- Validate category
- Verify project ownership
     ↓
Transaction.objects.create()
- Insert into database
- Trigger signals
     ↓
ActivityLog Signal Handler
- Create activity log entry
- Record change details
     ↓
Cache Invalidation
- Invalidate project cache
- Invalidate report cache
     ↓
Response Serializer
- Format transaction data
- Include computed fields
     ↓
Return 201 Created
```

### Report Generation Flow

```
Client Request
     ↓
GET /api/v1/reports/summary/?date_from=...&date_to=...
     ↓
Check Cache
- Cache hit? Return cached data
- Cache miss? Continue
     ↓
ReportCalculator.get_summary()
- Aggregate transactions
  SELECT SUM(amount) WHERE type='income'
  SELECT SUM(amount) WHERE type='expense'
- Calculate net
     ↓
Cache Result
- Set in Redis
- TTL: 1 hour
     ↓
Response Serializer
     ↓
Return 200 OK
```

## Asynchronous Task Architecture

### Celery Task Flow

```
Trigger Event
     ↓
Queue Task (Celery)
     ↓
Worker Receives Task
     ↓
Execute Task
- Send email
- Import transactions
- Generate report
- Calculate alerts
     ↓
Store Result
(Redis result backend)
     ↓
Cleanup
```

### Scheduled Tasks (Celery Beat)

```
Celery Beat Scheduler
     ↓
Check Schedule
     ↓
Trigger Task
     ↓
check_budget_alerts (daily at 9 AM)
- Get all budgets
- Calculate spent vs limit
- Send alert emails if threshold exceeded
     ↓
Queue Results
     ↓
Log Activity
```

## Database Schema

### Key Tables

**users**
- id (UUID)
- email (unique)
- password (bcrypted)
- first_name, last_name
- is_active, is_staff
- created_at, updated_at

**projects**
- id (UUID)
- name, description
- owner_id (FK to User)
- slug (auto-generated)
- created_at, updated_at

**transactions**
- id (UUID)
- amount (Decimal)
- category (CharField)
- description (TextField)
- date (DateField)
- project_id (FK)
- created_by_id (FK to User)
- created_at, updated_at

**budgets**
- id (UUID)
- name, amount (Decimal)
- period (monthly, quarterly, yearly)
- project_id (FK)
- alert_threshold (int)
- created_at, updated_at

**activity_logs**
- id (UUID)
- user_id (FK)
- action (CREATE, UPDATE, DELETE, etc.)
- content_type (ContentType)
- object_id (GenericForeignKey)
- changes (JSONField)
- metadata (JSONField)
- ip_address, user_agent
- created_at

**Indexes**
- (project_id, date) on transactions
- (project_id, category) on transactions
- (user_id) on projects
- (user_id) on activity_logs

## Caching Strategy

### Cache Layers

```
1. Database Query Cache (ORM-level)
   - select_related() - JOIN optimization
   - prefetch_related() - Batch queries
   - only()/defer() - Limit fields

2. Application Cache (Redis)
   - Report results (1 hour)
   - Category lists (24 hours)
   - User permissions (1 hour)

3. HTTP Cache (Browser/CDN)
   - Static files (30 days)
   - Media files (7 days)
   - API responses (configurable)
```

### Cache Invalidation

```
On Update
     ↓
Signal Handler Triggered
     ↓
Identify Affected Caches
- Report cache for project
- Project summary cache
- Activity log cache
     ↓
Delete Cache Keys
     ↓
Next request rebuilds cache
```

## Security Architecture

### Authentication & Authorization

```
JWT Token Structure
┌────────────────────────────────────────────┐
│  Header.Payload.Signature                  │
├────────────────────────────────────────────┤
│  alg: HS256                               │
│  typ: JWT                                  │
├────────────────────────────────────────────┤
│  user_id: 123                             │
│  email: user@example.com                  │
│  exp: 1711530000                          │
│  iat: 1711526400                          │
├────────────────────────────────────────────┤
│  Signature (HMAC-SHA256)                  │
└────────────────────────────────────────────┘
```

### Security Layers

```
1. Transport Security
   - HTTPS/TLS 1.2+
   - Secure cookies
   - HSTS headers

2. Authentication
   - JWT tokens
   - Token rotation
   - Token blacklist
   - Password hashing (bcrypt)

3. Authorization
   - Permission classes
   - Object-level checks
   - Scope validation

4. Input Validation
   - Serializer validation
   - Type checking
   - SQL injection prevention
   - XSS prevention

5. Output Encoding
   - JSON serialization
   - HTML escaping
   - Safe templates

6. Rate Limiting
   - Request throttling
   - Per-user limits
   - Per-endpoint limits
```

## Deployment Architecture

### Development Environment

```
┌─────────────┐
│   Django    │ (Development Server)
│ runserver   │
└──────┬──────┘
       │
┌──────▼──────────┐
│   SQLite DB    │ (In-memory)
└────────────────┘

┌──────┬──────────┐
│Redis │Celery    │
│Cache │Worker    │
└──────┴──────────┘
```

### Production Environment

```
┌──────────────────────────────────────────┐
│  Load Balancer (ALB/NLB)                │
└──────────────┬───────────────────────────┘
               │
     ┌─────────┼─────────┐
     │         │         │
┌────▼──┐ ┌───▼──┐ ┌───▼──┐
│ App 1 │ │ App2 │ │ App 3│ (Gunicorn)
└────┬──┘ └───┬──┘ └───┬──┘
     └────────┼────────┘
              │
     ┌────────▼────────┐
     │    Nginx        │
     │ Reverse Proxy   │
     └────────┬────────┘
              │
     ┌────────┼────────┐
     │        │        │
┌────▼──┐ ┌──▼───┐ ┌──▼────┐
│PostgreSQL│ Redis │ S3      │
│Database  │ Cache │ Storage │
└──────────┴──────┴─────────┘

Async Tasks
┌──────────────────────────┐
│  Celery Worker Pool      │
│  - Email sending         │
│  - Report generation     │
│  - Data import/export    │
└──────────────────────────┘

Scheduled Tasks
┌──────────────────────────┐
│  Celery Beat Scheduler   │
│  - Daily budget checks   │
│  - Cache cleanup         │
└──────────────────────────┘
```

### Kubernetes Deployment

```
┌──────────────────────────────────────────────┐
│         Kubernetes Cluster                  │
├──────────────────────────────────────────────┤
│  ┌────────────────────────────────────────┐ │
│  │    Service (Load Balancer)             │ │
│  └────┬───────────────────────────────────┘ │
│       │                                     │
│  ┌────▼─────────────────────────────────┐  │
│  │    Deployment (App Pods)             │  │
│  │  - Replicas: 3                       │  │
│  │  - Liveness Probe: /readiness/       │  │
│  │  - Readiness Probe: /liveness/       │  │
│  │  - Resource Limits: 256MB mem        │  │
│  └────┬─────────────────────────────────┘  │
│       │                                     │
│  ┌────▼────────┐  ┌──────────┐  ┌─────┐  │
│  │ PostgreSQL  │  │  Redis   │  │ S3  │  │
│  │ StatefulSet │  │ Pod      │  │     │  │
│  └─────────────┘  └──────────┘  └─────┘  │
└──────────────────────────────────────────────┘
```

## Scalability Considerations

### Horizontal Scaling

**Web Application**
- Stateless design
- Load balancer distributes requests
- Multiple app instances
- Session stored in database/cache

**Database**
- Read replicas for reporting
- Connection pooling
- Query optimization
- Partitioning for large tables

**Caching**
- Redis cluster
- Cache warming
- Cache invalidation strategy

**Task Queue**
- Multiple worker instances
- Priority queues
- Task routing

### Vertical Scaling

- Increase instance size
- More CPU cores
- More memory
- Better I/O performance

## Monitoring & Observability

### Metrics Collected

- API response times
- Request rates
- Error rates
- Database query times
- Cache hit rates
- Task queue length
- Memory usage
- CPU usage

### Logging

- Application logs
- Security logs
- Access logs
- Error tracking (Sentry)
- Audit logs

### Health Checks

- `/api/v1/health/` - Simple health
- `/api/v1/readiness/` - Readiness check
- `/api/v1/liveness/` - Liveness check
- `/api/v1/metrics/` - Basic metrics

## Future Architecture Considerations

1. **Microservices**
   - Split into domain services
   - Independent scaling
   - Decoupled deployments

2. **Event-Driven**
   - Event streaming (Kafka)
   - Event sourcing
   - CQRS pattern

3. **Caching Layer Upgrade**
   - Distributed caching
   - Cache coherence
   - Multi-level caching

4. **Search Optimization**
   - Elasticsearch
   - Full-text search
   - Advanced filtering

5. **Real-time Features**
   - WebSocket support
   - Server-sent events
   - Real-time notifications

---

For more information, see the [Developer Guide](DEVELOPER_GUIDE.md) and [Deployment Guide](DEPLOYMENT.md).
