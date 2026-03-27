# Expense Tracker API Documentation

## Overview

The Expense Tracker API is a comprehensive REST API for managing expenses, budgets, and financial reports. It provides functionality for project management, transaction tracking, document management, budget planning, and financial analysis.

**API Version:** 1.0.0
**Base URL:** `https://api.expensetracker.com/api/v1/`
**Authentication:** JWT Bearer Token

## Table of Contents

1. [Authentication](#authentication)
2. [Projects](#projects)
3. [Transactions & Categories](#transactions--categories)
4. [Budgets](#budgets)
5. [Documents](#documents)
6. [Reports & Analytics](#reports--analytics)
7. [Activity Logs](#activity-logs)
8. [Error Handling](#error-handling)

---

## Authentication

### Login

```http
POST /auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Register

```http
POST /auth/register/
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Refresh Token

```http
POST /auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Get Current User

```http
GET /auth/me/
Authorization: Bearer {access_token}
```

---

## Projects

### List Projects

```http
GET /projects/
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `project_type` - Filter by type: `personal`, `business`, `team`
- `is_active` - Filter by active status: `true`, `false`
- `search` - Search in project name and description
- `page` - Page number (default: 1)
- `page_size` - Results per page (default: 50)

**Response:**
```json
{
  "count": 15,
  "next": "https://api.expensetracker.com/api/v1/projects/?page=2",
  "previous": null,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "My Budget",
      "description": "Personal budget tracker",
      "project_type": "personal",
      "owner": "550e8400-e29b-41d4-a716-446655440000",
      "currency": "USD",
      "budget": "5000.00",
      "start_date": "2026-01-01",
      "end_date": "2026-12-31",
      "is_active": true,
      "is_archived": false,
      "created_at": "2026-03-27T10:30:00Z",
      "updated_at": "2026-03-27T10:30:00Z"
    }
  ]
}
```

### Create Project

```http
POST /projects/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Q1 Marketing Budget",
  "description": "Marketing expenses for Q1 2026",
  "project_type": "business",
  "currency": "USD",
  "budget": "10000.00",
  "start_date": "2026-01-01",
  "end_date": "2026-03-31"
}
```

### Get Project Details

```http
GET /projects/{project_id}/
Authorization: Bearer {access_token}
```

### Update Project

```http
PATCH /projects/{project_id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Updated Project Name",
  "budget": "15000.00"
}
```

### Delete Project

```http
DELETE /projects/{project_id}/
Authorization: Bearer {access_token}
```

### Archive Project

```http
POST /projects/{project_id}/archive/
Authorization: Bearer {access_token}
```

---

## Transactions & Categories

### List Categories

```http
GET /projects/{project_id}/categories/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "count": 12,
  "results": [
    {
      "id": "987fcdeb-51a2-12d3-a456-426614174000",
      "name": "Food & Dining",
      "category_type": "expense",
      "icon": "🍽️",
      "color": "#FF6B6B",
      "is_default": false,
      "created_at": "2026-03-27T10:30:00Z"
    }
  ]
}
```

### Create Transaction

```http
POST /projects/{project_id}/transactions/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "transaction_type": "expense",
  "amount": "45.99",
  "currency": "USD",
  "category": "987fcdeb-51a2-12d3-a456-426614174000",
  "title": "Lunch",
  "description": "Lunch with team",
  "payment_method": "credit_card",
  "date": "2026-03-27",
  "tags": ["meal", "team"]
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
    "name": "Food & Dining",
    "icon": "🍽️",
    "color": "#FF6B6B"
  },
  "title": "Lunch",
  "description": "Lunch with team",
  "payment_method": "credit_card",
  "date": "2026-03-27",
  "tags": ["meal", "team"],
  "created_by": {
    "id": "user-uuid",
    "email": "user@example.com",
    "first_name": "John"
  },
  "documents": [],
  "created_at": "2026-03-27T10:30:00Z",
  "updated_at": "2026-03-27T10:30:00Z"
}
```

### List Transactions

```http
GET /projects/{project_id}/transactions/
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `start_date` - Filter from date (YYYY-MM-DD)
- `end_date` - Filter to date (YYYY-MM-DD)
- `category` - Filter by category ID
- `transaction_type` - Filter by type: `expense`, `income`
- `payment_method` - Filter by payment method
- `search` - Search in title and description
- `ordering` - Order by field (e.g., `-date`, `amount`)

### Export Transactions

```http
GET /projects/{project_id}/transactions/export/?format=csv
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `format` - Export format: `csv`, `excel`

**Response:** CSV or Excel file

### Bulk Import Transactions

```http
POST /projects/{project_id}/transactions/bulk-create/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "transactions": [
    {
      "transaction_type": "expense",
      "amount": "100.00",
      "category": "cat-id-1",
      "title": "Transaction 1",
      "date": "2026-03-27"
    },
    {
      "transaction_type": "income",
      "amount": "500.00",
      "category": "cat-id-2",
      "title": "Income 1",
      "date": "2026-03-26"
    }
  ]
}
```

---

## Budgets

### List Budgets

```http
GET /projects/{project_id}/budgets/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "count": 3,
  "results": [
    {
      "id": "budget-uuid",
      "project": "project-uuid",
      "project_name": "Q1 Budget",
      "project_currency": "USD",
      "category": "category-uuid",
      "category_name": "Food",
      "amount": "500.00",
      "period": "monthly",
      "start_date": "2026-03-01",
      "end_date": "2026-03-31",
      "alert_threshold": 80,
      "alert_enabled": true,
      "created_by": "user-uuid",
      "created_at": "2026-03-27T10:30:00Z",
      "updated_at": "2026-03-27T10:30:00Z"
    }
  ]
}
```

### Create Budget

```http
POST /projects/{project_id}/budgets/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "amount": "500.00",
  "category": "category-uuid",
  "period": "monthly",
  "start_date": "2026-03-01",
  "end_date": "2026-03-31",
  "alert_threshold": 80,
  "alert_enabled": true
}
```

### Get Budget Status

```http
GET /projects/{project_id}/budgets/status/
Authorization: Bearer {access_token}
```

**Response:**
```json
[
  {
    "budget_id": "budget-uuid",
    "allocated": 500.00,
    "spent": 320.50,
    "remaining": 179.50,
    "percentage_used": 64.1,
    "alert_triggered": false,
    "period": "monthly",
    "category_name": "Food"
  }
]
```

### Get Budget Summary

```http
GET /projects/{project_id}/budgets/summary/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "project_id": "project-uuid",
  "total_allocated": 2000.00,
  "total_spent": 1250.75,
  "total_remaining": 749.25,
  "budget_count": 4,
  "alerts_triggered": 1
}
```

---

## Documents

### Upload Document

```http
POST /projects/{project_id}/transactions/{transaction_id}/documents/
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

file: [binary file data]
document_type: receipt
notes: Receipt for office supplies
```

**Response:**
```json
{
  "id": "doc-uuid",
  "transaction": "transaction-uuid",
  "file": "https://s3.amazonaws.com/bucket/documents/2026/03/receipt.pdf",
  "file_name": "receipt.pdf",
  "file_size": 245678,
  "file_type": "application/pdf",
  "document_type": "receipt",
  "notes": "Receipt for office supplies",
  "uploaded_by": {
    "id": "user-uuid",
    "email": "user@example.com"
  },
  "uploaded_at": "2026-03-27T10:30:00Z"
}
```

### List Documents

```http
GET /projects/{project_id}/transactions/{transaction_id}/documents/
Authorization: Bearer {access_token}
```

### Download Document

```http
GET /projects/{project_id}/transactions/{transaction_id}/documents/{doc_id}/download/
Authorization: Bearer {access_token}
```

### Delete Document

```http
DELETE /projects/{project_id}/transactions/{transaction_id}/documents/{doc_id}/
Authorization: Bearer {access_token}
```

---

## Reports & Analytics

### Financial Summary

```http
GET /projects/{project_id}/reports/summary/
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `start_date` - Start date (YYYY-MM-DD)
- `end_date` - End date (YYYY-MM-DD)

**Response:**
```json
{
  "period": {
    "start": "2026-03-01",
    "end": "2026-03-27"
  },
  "summary": {
    "total_income": "5000.00",
    "total_expenses": "2345.67",
    "net": "2654.33",
    "transaction_count": 45
  }
}
```

### Category Breakdown

```http
GET /projects/{project_id}/reports/category-breakdown/
Authorization: Bearer {access_token}
```

### Spending Trends

```http
GET /projects/{project_id}/reports/trends/
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `start_date` - Start date
- `end_date` - End date
- `granularity` - `day`, `week`, or `month`

### Monthly Report

```http
GET /projects/{project_id}/reports/monthly/
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `year` - Year (default: current)
- `month` - Month 1-12 (default: current)

### Period Comparison

```http
GET /projects/{project_id}/reports/comparison/
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `start_date1` - First period start
- `end_date1` - First period end
- `start_date2` - Second period start
- `end_date2` - Second period end

---

## Activity Logs

### Project Activity Log

```http
GET /projects/{project_id}/activity/
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `action` - Filter by action: `create`, `update`, `delete`, `view`, etc.
- `content_type` - Filter by type: `transaction`, `budget`, `document`, etc.
- `user` - Filter by user ID
- `search` - Search in description
- `page` - Page number

**Response:**
```json
{
  "count": 142,
  "results": [
    {
      "id": "log-uuid",
      "user": "user-uuid",
      "user_email": "user@example.com",
      "user_name": "John Doe",
      "project": "project-uuid",
      "action": "create",
      "action_display": "Created",
      "content_type": "transaction",
      "object_id": "transaction-uuid",
      "description": "Created transaction 'Lunch' for 45.99 USD",
      "changes": {},
      "metadata": {
        "transaction_type": "expense",
        "amount": "45.99",
        "currency": "USD"
      },
      "created_at": "2026-03-27T10:30:00Z"
    }
  ]
}
```

### User Activity Log

```http
GET /activity/
Authorization: Bearer {access_token}
```

Lists all activities performed by the current user across all projects.

### Object Activity Log

```http
GET /projects/{project_id}/activity/{content_type}/{object_id}/
Authorization: Bearer {access_token}
```

Lists all activities related to a specific object (e.g., a transaction).

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Codes

| Status Code | Meaning |
|---|---|
| 400 | Bad Request - Invalid input data |
| 401 | Unauthorized - Missing or invalid authentication |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Duplicate or conflicting data |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server error |

### Example Error Response

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "detail": "Budget amount must be greater than zero."
}
```

---

## Rate Limiting

Currently, rate limiting is not enforced, but may be added in future versions. Clients should implement reasonable request throttling.

## Pagination

All list endpoints support pagination with the following parameters:

- `page` - Page number (default: 1)
- `page_size` - Results per page (default: 50, max: 100)

Response includes:
```json
{
  "count": 150,
  "next": "https://api.expensetracker.com/api/v1/endpoint/?page=2",
  "previous": null,
  "results": [...]
}
```

## Filtering & Search

- Use query parameters for filtering (e.g., `?category=uuid&action=create`)
- Use `search` parameter for text search
- Use `ordering` parameter for sorting (prefix with `-` for descending)

## Documentation Access

- **Swagger UI**: `/api/v1/docs/`
- **ReDoc**: `/api/v1/redoc/`
- **OpenAPI Schema**: `/api/v1/schema/`

---

## Support

For API support, contact: support@expensetracker.com
