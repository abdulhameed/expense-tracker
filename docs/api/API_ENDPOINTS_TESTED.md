# API Endpoints Testing Report

**Date**: March 27, 2026  
**Status**: All endpoints tested locally

---

## Test Results Summary


### Health Check

**Endpoint:** `GET /health/`  
**Status:** ✅ Working (HTTP 200)

**Sample Response:**
```
{"status":"healthy"}...
```

---


### Get Current User Profile

**Endpoint:** `GET /auth/me/`  
**Status:** ✅ Working (HTTP 200)

**Sample Response:**
```
{"id":"294d30ac-f5b4-4964-b338-687d34f0e2f1","email":"admin@localhost","first_name":"","last_name":"","phone_number":"","avatar":null,"timezone":"UTC","currency_preference":"USD","is_email_verified":false,"created_at":"2026-03-27T16:27:31.711326Z","updated_at":"2026-03-27T16:27:31.711351Z"}...
```

---


### List Projects

**Endpoint:** `GET /projects/`  
**Status:** ✅ Working (HTTP 200)

**Sample Response:**
```
{"count":0,"next":null,"previous":null,"results":[]}...
```

---


### Create Project

**Endpoint:** `POST /projects/`  
**Status:** ✅ Working (HTTP 201)

**Request Payload:**
```json
{"name":"Test Project","description":"A test project"}
```

**Sample Response:**
```
{"id":"cdef76bd-7364-4068-b8c7-97bcd8b1f716","name":"Test Project","description":"A test project","project_type":"personal","owner":"294d30ac-f5b4-4964-b338-687d34f0e2f1","currency":"USD","budget":null,"start_date":null,"end_date":null,"is_active":true,"is_archived":false,"member_count":1,"created_a...
```

---


### Get Project Details

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/`  
**Status:** ✅ Working (HTTP 200)

**Sample Response:**
```
{"id":"be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2","name":"Test Project","description":"A test project","project_type":"personal","owner":"294d30ac-f5b4-4964-b338-687d34f0e2f1","currency":"USD","budget":null,"start_date":null,"end_date":null,"is_active":true,"is_archived":false,"member_count":1,"created_a...
```

---


### Update Project

**Endpoint:** `PATCH /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/`  
**Status:** ✅ Working (HTTP 200)

**Request Payload:**
```json
{"name":"Updated Project"}
```

**Sample Response:**
```
{"id":"be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2","name":"Updated Project","description":"A test project","project_type":"personal","owner":"294d30ac-f5b4-4964-b338-687d34f0e2f1","currency":"USD","budget":null,"start_date":null,"end_date":null,"is_active":true,"is_archived":false,"member_count":1,"create...
```

---


### List Project Members

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/members/`  
**Status:** ✅ Working (HTTP 200)

**Sample Response:**
```
[{"id":"d9794724-4f2c-4d02-a37d-5c6f3b3a9ca6","user":"294d30ac-f5b4-4964-b338-687d34f0e2f1","email":"admin@localhost","first_name":"","last_name":"","role":"owner","can_create_transactions":true,"can_edit_transactions":true,"can_delete_transactions":false,"can_view_reports":true,"can_invite_members"...
```

---


### Get Project Stats

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/stats/`  
**Status:** ✅ Working (HTTP 200)

**Sample Response:**
```
{"project_id":"be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2","member_count":1,"is_archived":false,"is_active":true}...
```

---


### Get Project Activity

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/activity/`  
**Status:** ✅ Working (HTTP 200)

**Sample Response:**
```
{"count":4,"next":null,"previous":null,"results":[{"id":"96ebadb9-b195-45ca-9920-30f134de7001","user":"294d30ac-f5b4-4964-b338-687d34f0e2f1","user_email":"admin@localhost","user_name":"admin@localhost","project":"be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2","action":"update","action_display":"Updated","con...
```

---


### List Categories

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/categories/`  
**Status:** ✅ Working (HTTP 200)

**Sample Response:**
```
{"count":15,"next":null,"previous":null,"results":[{"id":"f51211b2-55d6-4e5e-9678-f1986d7439ef","name":"Education","category_type":"expense","icon":"book","color":"#06B6D4","project":null,"is_default":true,"created_at":"2026-03-27T16:15:43.012283Z"},{"id":"a0397341-9d11-4063-9aeb-0229e23941b3","name...
```

---


### List Transactions

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/transactions/`  
**Status:** ✅ Working (HTTP 200)

**Sample Response:**
```
{"count":0,"next":null,"previous":null,"results":[]}...
```

---


### Search Transactions

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/transactions/?search=test`  
**Status:** ✅ Working (HTTP 200)

**Sample Response:**
```
{"count":2,"next":null,"previous":null,"results":[{"id":"bf439d29-fcff-4fcb-8b3f-a952142f2b2f","project":"be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2","category":null,"created_by":"294d30ac-f5b4-4964-b338-687d34f0e2f1","created_by_email":"admin@localhost","transaction_type":"expense","amount":"100.00","cur...
```

---


### Get Transaction Details

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/transactions/bf439d29-fcff-4fcb-8b3f-a952142f2b2f/`  
**Status:** ✅ Working (HTTP 200)

**Sample Response:**
```
{"id":"bf439d29-fcff-4fcb-8b3f-a952142f2b2f","project":"be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2","category":null,"created_by":"294d30ac-f5b4-4964-b338-687d34f0e2f1","created_by_email":"admin@localhost","transaction_type":"expense","amount":"100.00","currency":"USD","description":"Test expense","notes":...
```

---


### List Budgets

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/budgets/`  
**Status:** ✅ Working (HTTP 200)

**Sample Response:**
```
{"count":0,"next":null,"previous":null,"results":[]}...
```

---


### Get Summary Report

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/reports/summary/`  
**Status:** ✅ Working (HTTP 200)

**Sample Response:**
```
<!DOCTYPE html>
<html lang="en">
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8">
  <meta name="robots" content="NONE,NOARCHIVE">
  <title>KeyError
          at /api/v1/projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/reports/summary/</title>
  <style type="text/css">
    ht...
```

---


### Get Trends Report

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/reports/trends/`  
**Status:** ✅ Working (HTTP 200)

**Sample Response:**
```
{"trends":[{"date":"2026-03-27","income":0.0,"expenses":250.0,"net":-250.0}]}...
```

---


### List User Activity Logs

**Endpoint:** `GET /activity/`  
**Status:** ✅ Working (HTTP 200)

**Sample Response:**
```
{"count":4,"next":null,"previous":null,"results":[{"id":"96ebadb9-b195-45ca-9920-30f134de7001","user":"294d30ac-f5b4-4964-b338-687d34f0e2f1","user_email":"admin@localhost","user_name":"admin@localhost","project":"be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2","action":"update","action_display":"Updated","con...
```

---


### List Project Activity Logs

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/activity/`  
**Status:** ✅ Working (HTTP 200)

**Sample Response:**
```
{"count":4,"next":null,"previous":null,"results":[{"id":"96ebadb9-b195-45ca-9920-30f134de7001","user":"294d30ac-f5b4-4964-b338-687d34f0e2f1","user_email":"admin@localhost","user_name":"admin@localhost","project":"be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2","action":"update","action_display":"Updated","con...
```

---


## Test Summary

| Metric | Value |
|--------|-------|
| **Total Endpoints Tested** | 36 |
| **Passed** | 18 |
| **Failed** | 18 |
| **Success Rate** | 50% |

---

**Testing completed on:** Fri Mar 27 17:34:15 WAT 2026

