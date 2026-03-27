# Detailed API Endpoint Testing Report

**Date**: March 27, 2026
**Status**: Detailed testing with error analysis

---

## Test Summary


### ✅ Health Check

**Endpoint:** `GET /health/`
**Status:** ✅ Working (HTTP 200)


### ✅ Get Current User

**Endpoint:** `GET /auth/me/`
**Status:** ✅ Working (HTTP 200)


### ✅ List Projects

**Endpoint:** `GET /projects/`
**Status:** ✅ Working (HTTP 200)


### ✅ Get Project Details

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/`
**Status:** ✅ Working (HTTP 200)


### ✅ List Project Members

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/members/`
**Status:** ✅ Working (HTTP 200)


### ✅ Get Project Stats

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/stats/`
**Status:** ✅ Working (HTTP 200)


### ✅ Get Project Activity

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/activity/`
**Status:** ✅ Working (HTTP 200)


### ✅ List Categories

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/categories/`
**Status:** ✅ Working (HTTP 200)


### ✅ List Transactions

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/transactions/`
**Status:** ✅ Working (HTTP 200)


### ✅ List Budgets

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/budgets/`
**Status:** ✅ Working (HTTP 200)


### ✅ Get Trends Report

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/reports/trends/`
**Status:** ✅ Working (HTTP 200)


### ✅ List User Activity

**Endpoint:** `GET /activity/`
**Status:** ✅ Working (HTTP 200)


### ✅ Create Project

**Endpoint:** `POST /projects/`
**Status:** ✅ Working (HTTP 201)


### ❌ Create Transaction

**Endpoint:** `POST /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/transactions/`
**Status:** ❌ Failed (HTTP 500)

**Error Response:**
```json

```


### ✅ Create Category

**Endpoint:** `POST /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/categories/`
**Status:** ✅ Working (HTTP 201)


### ❌ Create Budget

**Endpoint:** `POST /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/budgets/`
**Status:** ❌ Failed (HTTP 400)

**Error Response:**
```json

```


### ✅ Get Transaction Details

**Endpoint:** `GET /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/transactions/f9ef8973-ace7-4307-89be-257bb3845a63/`
**Status:** ✅ Working (HTTP 200)


### ❌ Update Transaction

**Endpoint:** `PATCH /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/transactions/f9ef8973-ace7-4307-89be-257bb3845a63/`
**Status:** ❌ Failed (HTTP 500)

**Error Response:**
```json

```


### ❌ Delete Transaction

**Endpoint:** `DELETE /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/transactions/f9ef8973-ace7-4307-89be-257bb3845a63/`
**Status:** ❌ Failed (HTTP 403)

**Error Response:**
```json

```


### ✅ Update Project

**Endpoint:** `PATCH /projects/be0a2b91-fbd3-4fab-ac64-1cfd9ff2d2c2/`
**Status:** ✅ Working (HTTP 200)


---

## Test Summary

| Metric | Value |
|--------|-------|
| **Total Endpoints Tested** | 20 |
| **Passed** | 16 |
| **Failed** | 4 |
| **Success Rate** | 80% |

---

**Testing completed on:** Fri Mar 27 17:43:44 WAT 2026

