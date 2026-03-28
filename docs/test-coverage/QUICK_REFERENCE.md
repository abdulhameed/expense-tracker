# Quick Reference: Test Coverage Gaps

## Current State
- Total Production Code: 5,470 LOC
- Total Test Methods: 394
- Current Estimated Coverage: 50-60%
- Target: 80%

## Critical Gaps (Must Add First)

### 1. Security App (970 LOC)
Files without ANY tests:
- `authentication.py` (236 LOC) - JWT, token validation
- `validators.py` (182 LOC) - Custom validators
- `middleware.py` (130 LOC) - Security headers, IP whitelisting
- `throttling.py` (69 LOC) - Rate limiting

**Need: 60-80 new tests**

### 2. Activity App - Signals (274 LOC)
- `signals.py` - 8+ signal handlers tracking all model changes
- Signal types: transaction, category, budget, document, project, member, invitation

**Need: 25-35 new tests**

### 3. Utils App (424 LOC - ZERO TESTS)
- `monitoring.py` (217 LOC) - Performance metrics
- `caching.py` (171 LOC) - Cache decorators

**Need: 20-30 new tests**

### 4. Health App (225 LOC - ZERO TESTS)
- `views.py` (194 LOC) - 12 health check methods

**Need: 15-20 new tests**

## High-Impact Second Priority

### 5. Celery Tasks (Missing from 3 apps)
- `authentication/tasks.py` (64 LOC) - Email verification & password reset
- `budgets/tasks.py` (110 LOC) - Budget alerts (only 15 tests exist, need +10)
- `projects/tasks.py` (28 LOC) - Invitation emails

**Need: 20-25 new tests**

### 6. Serializers (Missing from 6 apps)
- `reports/serializers.py` (82 LOC)
- `budgets/serializers.py` (97 LOC)
- `transactions/serializers.py` (77 LOC)
- `documents/serializers.py` (79 LOC)
- `projects/serializers.py` (69 LOC)
- `authentication/serializers.py` (64 LOC)

**Need: 30-40 new tests**

## Test Files to Create

### CRITICAL (Phase 1)
```
apps/security/tests/
  ├── test_authentication.py (NEW - 8 tests)
  ├── test_validators.py (NEW - 10 tests)
  ├── test_middleware.py (NEW - 7 tests)
  └── test_throttling.py (NEW - 5 tests)

apps/activity/tests/
  └── test_signals.py (NEW - 30 tests)

apps/utils/tests/
  ├── test_monitoring.py (NEW)
  └── test_caching.py (NEW)

apps/health/tests/
  └── test_api.py (NEW - 18 tests)
```

### IMPORTANT (Phase 2)
```
apps/authentication/tests/
  └── test_tasks.py (NEW - 8 tests)

apps/budgets/tests/
  └── EXPAND test_tasks.py (+10 tests)

apps/projects/tests/
  ├── test_tasks.py (NEW - 6 tests)
  └── test_permissions.py (NEW - 12 tests)

apps/transactions/tests/
  ├── test_filters.py (NEW - 8 tests)
  └── test_serializers.py (NEW - 10 tests)
```

### POLISH (Phase 3)
```
apps/reports/tests/
  └── test_serializers.py (NEW - 8 tests)

apps/documents/tests/
  └── test_serializers.py (NEW - 8 tests)

apps/budgets/tests/
  └── test_serializers.py (NEW - 8 tests)

apps/projects/tests/
  └── test_serializers.py (NEW - 8 tests)

apps/authentication/tests/
  └── test_serializers.py (NEW - 8 tests)

(Admin tests for each app - lower priority)
```

## Effort Estimate

| Phase | Tests | Estimated Time |
|-------|-------|-----------------|
| Phase 1 (Critical) | 40-50 | 4-5 days |
| Phase 2 (Important) | 40-50 | 4-5 days |
| Phase 3 (Polish) | 30-40 | 3-4 days |
| **Total** | **110-140** | **10-14 days** |

## Expected Impact per Phase

- **After Phase 1:** 60-65% coverage
- **After Phase 2:** 70-75% coverage
- **After Phase 3:** 80%+ coverage

## Most Undertested Components

1. Signal handlers (activity) - 274 LOC, 0 tests
2. Security utils (security) - 617 LOC, 27 tests only
3. Caching/monitoring (utils) - 388 LOC, 0 tests
4. Health checks (health) - 194 LOC, 0 tests
5. Celery tasks (multiple) - 202 LOC, 15 tests
