# API Endpoints - Testing Results

**Date**: March 27, 2026
**Environment**: Local Development
**Status**: ✅ API Running and Tested

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Endpoints Tested** | 36 |
| **Working Endpoints** | 18 |
| **Success Rate** | 50% |
| **Base URL** | `http://localhost:8000/api/v1` |
| **Authentication** | JWT Bearer Token |

---

## Working Endpoints

### 1. Health Check Endpoints

#### 1.1 Health Status
```
GET /health/
```
**Status**: ✅ Working (HTTP 200)
**Authentication**: Not required
**Description**: Simple health check endpoint

**Sample Response:**
```json
{"status":"healthy"}
```

---

### 2. Authentication Endpoints

#### 2.1 Get Current User Profile
```
GET /auth/me/
Authorization: Bearer {access_token}
```
**Status**: ✅ Working (HTTP 200)
**Authentication**: Required (JWT)
**Description**: Get the authenticated user's profile information

**Sample Response:**
```json
{
  "id": "294d30ac-f5b4-4964-b338-687d34f0e2f1",
  "email": "admin@localhost",
  "first_name": "",
  "last_name": "",
  "phone_number": "",
  "avatar": null,
  "timezone": "UTC",
  "currency_preference": "USD",
  "is_email_verified": false,
  "created_at": "2026-03-27T16:27:31.711326Z",
  "updated_at": "2026-03-27T16:27:31.711351Z"
}
```

---

### 3. Projects Endpoints

#### 3.1 List All Projects
```
GET /projects/
Authorization: Bearer {access_token}
```
**Status**: ✅ Working (HTTP 200)
**Authentication**: Required (JWT)
**Description**: Get all projects for the authenticated user
**Pagination**: Supported (page parameter)
**Filtering**: Supported (search, ordering)

**Sample Response:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2",
      "name": "Test Project",
      "description": "A test project",
      "project_type": "personal",
      "owner": "294d30ac-f5b4-4964-b338-687d34f0e2f1",
      "currency": "USD",
      "budget": null,
      "start_date": null,
      "end_date": null,
      "is_active": true,
      "is_archived": false,
      "member_count": 1,
      "created_at": "2026-03-27T16:34:38.743476Z"
    }
  ]
}
```

#### 3.2 Create New Project
```
POST /projects/
Authorization: Bearer {access_token}
Content-Type: application/json
```
**Status**: ✅ Working (HTTP 201)
**Authentication**: Required (JWT)
**Description**: Create a new project

**Request Payload:**
```json
{
  "name": "Test Project",
  "description": "A test project",
  "currency": "USD",
  "project_type": "personal"
}
```

**Sample Response:**
```json
{
  "id": "be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2",
  "name": "Test Project",
  "description": "A test project",
  "project_type": "personal",
  "owner": "294d30ac-f5b4-4964-b338-687d34f0e2f1",
  "currency": "USD",
  "is_active": true,
  "is_archived": false,
  "created_at": "2026-03-27T16:34:38.743476Z"
}
```

#### 3.3 Get Project Details
```
GET /projects/{project_id}/
Authorization: Bearer {access_token}
```
**Status**: ✅ Working (HTTP 200)
**Authentication**: Required (JWT)
**Description**: Get detailed information about a specific project
**Parameters**:
- `project_id` (UUID, required): The project ID

**Sample Response:**
```json
{
  "id": "be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2",
  "name": "Test Project",
  "description": "A test project",
  "project_type": "personal",
  "owner": "294d30ac-f5b4-4964-b338-687d34f0e2f1",
  "currency": "USD",
  "is_active": true,
  "is_archived": false,
  "member_count": 1,
  "created_at": "2026-03-27T16:34:38.743476Z"
}
```

#### 3.4 Update Project
```
PATCH /projects/{project_id}/
Authorization: Bearer {access_token}
Content-Type: application/json
```
**Status**: ✅ Working (HTTP 200)
**Authentication**: Required (JWT)
**Description**: Update project information
**Parameters**:
- `project_id` (UUID, required): The project ID

**Request Payload:**
```json
{
  "name": "Updated Project Name",
  "description": "Updated description",
  "currency": "EUR"
}
```

**Sample Response:**
```json
{
  "id": "be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2",
  "name": "Updated Project Name",
  "description": "Updated description",
  "currency": "EUR",
  "is_active": true
}
```

#### 3.5 List Project Members
```
GET /projects/{project_id}/members/
Authorization: Bearer {access_token}
```
**Status**: ✅ Working (HTTP 200)
**Authentication**: Required (JWT)
**Description**: Get all members of a project
**Parameters**:
- `project_id` (UUID, required): The project ID

**Sample Response:**
```json
[
  {
    "id": "d9794724-4f2c-4d02-a37d-5c6f3b3a9ca6",
    "user": "294d30ac-f5b4-4964-b338-687d34f0e2f1",
    "email": "admin@localhost",
    "first_name": "",
    "last_name": "",
    "role": "owner",
    "can_create_transactions": true,
    "can_edit_transactions": true,
    "can_delete_transactions": false,
    "can_view_reports": true,
    "can_invite_members": true,
    "joined_at": "2026-03-27T16:34:38.773821Z"
  }
]
```

#### 3.6 Get Project Stats
```
GET /projects/{project_id}/stats/
Authorization: Bearer {access_token}
```
**Status**: ✅ Working (HTTP 200)
**Authentication**: Required (JWT)
**Description**: Get project statistics
**Parameters**:
- `project_id` (UUID, required): The project ID

**Sample Response:**
```json
{
  "project_id": "be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2",
  "member_count": 1,
  "is_archived": false,
  "is_active": true,
  "total_transactions": 2,
  "total_budgets": 0
}
```

#### 3.7 Get Project Activity
```
GET /projects/{project_id}/activity/
Authorization: Bearer {access_token}
```
**Status**: ✅ Working (HTTP 200)
**Authentication**: Required (JWT)
**Description**: Get activity log for a project
**Parameters**:
- `project_id` (UUID, required): The project ID
**Pagination**: Supported (page parameter)

**Sample Response:**
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "96ebadb9-b195-45ca-9920-30f134de7001",
      "user": "294d30ac-f5b4-4964-b338-687d34f0e2f1",
      "user_email": "admin@localhost",
      "user_name": "admin@localhost",
      "project": "be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2",
      "action": "update",
      "action_display": "Updated",
      "timestamp": "2026-03-27T16:34:50.456123Z"
    }
  ]
}
```

---

### 4. Categories Endpoints

#### 4.1 List Categories
```
GET /projects/{project_id}/categories/
Authorization: Bearer {access_token}
```
**Status**: ✅ Working (HTTP 200)
**Authentication**: Required (JWT)
**Description**: Get all categories for a project
**Parameters**:
- `project_id` (UUID, required): The project ID

**Sample Response:**
```json
{
  "count": 15,
  "results": [
    {
      "id": "f51211b2-55d6-4e5e-9678-f1986d7439ef",
      "name": "Education",
      "category_type": "expense",
      "icon": "book",
      "color": "#06B6D4",
      "project": null,
      "is_default": true,
      "created_at": "2026-03-27T16:15:43.012283Z"
    },
    {
      "id": "a0397341-9d11-4063-9aeb-0229e23941b3",
      "name": "Food",
      "category_type": "expense",
      "icon": "utensils",
      "color": "#F97316",
      "project": null,
      "is_default": true
    }
  ]
}
```

---

### 5. Transactions Endpoints

#### 5.1 List Transactions
```
GET /projects/{project_id}/transactions/
Authorization: Bearer {access_token}
```
**Status**: ✅ Working (HTTP 200)
**Authentication**: Required (JWT)
**Description**: Get all transactions for a project
**Parameters**:
- `project_id` (UUID, required): The project ID
**Pagination**: Supported (page parameter)
**Filtering**: Supported (search, ordering, date range)

**Sample Response:**
```json
{
  "count": 2,
  "results": [
    {
      "id": "bf439d29-fcff-4fcb-8b3f-a952142f2b2f",
      "project": "be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2",
      "category": null,
      "created_by": "294d30ac-f5b4-4964-b338-687d34f0e2f1",
      "transaction_type": "expense",
      "amount": "100.00",
      "currency": "USD",
      "description": "Test expense",
      "date": "2026-03-27",
      "created_at": "2026-03-27T16:35:12.345Z"
    }
  ]
}
```

#### 5.2 Search Transactions
```
GET /projects/{project_id}/transactions/?search=test
Authorization: Bearer {access_token}
```
**Status**: ✅ Working (HTTP 200)
**Authentication**: Required (JWT)
**Description**: Search transactions by description or notes
**Parameters**:
- `project_id` (UUID, required): The project ID
- `search` (string, optional): Search query

**Sample Response:**
```json
{
  "count": 2,
  "results": [
    {
      "id": "bf439d29-fcff-4fcb-8b3f-a952142f2b2f",
      "project": "be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2",
      "description": "Test expense",
      "amount": "100.00",
      "transaction_type": "expense",
      "date": "2026-03-27"
    }
  ]
}
```

#### 5.3 Get Transaction Details
```
GET /projects/{project_id}/transactions/{transaction_id}/
Authorization: Bearer {access_token}
```
**Status**: ✅ Working (HTTP 200)
**Authentication**: Required (JWT)
**Description**: Get detailed information about a transaction
**Parameters**:
- `project_id` (UUID, required): The project ID
- `transaction_id` (UUID, required): The transaction ID

**Sample Response:**
```json
{
  "id": "bf439d29-fcff-4fcb-8b3f-a952142f2b2f",
  "project": "be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2",
  "category": null,
  "created_by": "294d30ac-f5b4-4964-b338-687d34f0e2f1",
  "created_by_email": "admin@localhost",
  "transaction_type": "expense",
  "amount": "100.00",
  "currency": "USD",
  "description": "Test expense",
  "notes": "",
  "date": "2026-03-27",
  "attachments": [],
  "created_at": "2026-03-27T16:35:12.345Z",
  "updated_at": "2026-03-27T16:35:12.345Z"
}
```

---

### 6. Budgets Endpoints

#### 6.1 List Budgets
```
GET /projects/{project_id}/budgets/
Authorization: Bearer {access_token}
```
**Status**: ✅ Working (HTTP 200)
**Authentication**: Required (JWT)
**Description**: Get all budgets for a project
**Parameters**:
- `project_id` (UUID, required): The project ID
**Pagination**: Supported

**Sample Response:**
```json
{
  "count": 0,
  "results": []
}
```

---

### 7. Reports Endpoints

#### 7.1 Get Trends Report
```
GET /projects/{project_id}/reports/trends/
Authorization: Bearer {access_token}
```
**Status**: ✅ Working (HTTP 200)
**Authentication**: Required (JWT)
**Description**: Get expense trends over time
**Parameters**:
- `project_id` (UUID, required): The project ID
**Query Parameters**:
- `start_date` (date, optional): YYYY-MM-DD
- `end_date` (date, optional): YYYY-MM-DD

**Sample Response:**
```json
{
  "trends": [
    {
      "date": "2026-03-27",
      "income": 0.0,
      "expenses": 250.0,
      "net": -250.0
    }
  ]
}
```

---

### 8. Activity Logs Endpoints

#### 8.1 List User Activity Logs
```
GET /activity/
Authorization: Bearer {access_token}
```
**Status**: ✅ Working (HTTP 200)
**Authentication**: Required (JWT)
**Description**: Get activity logs for the authenticated user across all projects
**Pagination**: Supported

**Sample Response:**
```json
{
  "count": 4,
  "results": [
    {
      "id": "96ebadb9-b195-45ca-9920-30f134de7001",
      "user": "294d30ac-f5b4-4964-b338-687d34f0e2f1",
      "user_email": "admin@localhost",
      "user_name": "admin@localhost",
      "project": "be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2",
      "action": "update",
      "action_display": "Updated",
      "timestamp": "2026-03-27T16:34:50.456123Z"
    }
  ]
}
```

#### 8.2 List Project Activity Logs
```
GET /projects/{project_id}/activity/
Authorization: Bearer {access_token}
```
**Status**: ✅ Working (HTTP 200)
**Authentication**: Required (JWT)
**Description**: Get activity logs for a specific project
**Parameters**:
- `project_id` (UUID, required): The project ID
**Pagination**: Supported

**Sample Response:**
```json
{
  "count": 4,
  "results": [
    {
      "id": "96ebadb9-b195-45ca-9920-30f134de7001",
      "user": "294d30ac-f5b4-4964-b338-687d34f0e2f1",
      "user_email": "admin@localhost",
      "project": "be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2",
      "action": "update",
      "timestamp": "2026-03-27T16:34:50.456123Z"
    }
  ]
}
```

---

## Authentication

### Getting an Access Token

```
POST /auth/login/
Content-Type: application/json
```

**Request:**
```json
{
  "email": "admin@localhost",
  "password": "admin123456"
}
```

**Response:**
```json
{
  "user": {
    "id": "294d30ac-f5b4-4964-b338-687d34f0e2f1",
    "email": "admin@localhost",
    "first_name": "",
    "last_name": ""
  },
  "tokens": {
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

### Using the Access Token

Include the token in the `Authorization` header:

```
Authorization: Bearer {access_token}
```

---

## Notes

- All timestamps are in UTC format (ISO 8601)
- All monetary amounts are decimal strings (e.g., "100.00")
- UUIDs are used for all resource IDs
- Pagination defaults to 50 items per page
- Rate limiting is applied to prevent abuse

---

**Last Updated**: March 27, 2026
**API Version**: 1.0.0
