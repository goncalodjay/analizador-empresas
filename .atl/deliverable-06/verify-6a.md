# Verification Report -- deliverable-06 PR 6a (Backend)

## Change
deliverable-06 -- Strategy Management Module, PR slice 6a (backend)
Branch: deliverable-06a-backend
Scope: tasks 6a.1--6a.6 only. 6b.x are out of scope / pending.

## Mode
Strict TDD (test runner: python -m pytest from backend/)

---

## Test Results

109 passed, 0 failures, 0 skips, 70 warnings (28.48s)

All 109 tests pass (81 pre-existing + 13 service + 15 API). No regressions.
Warnings are httpx DeprecationWarning -- not test failures.

---

## Task Completeness

| Task | Status | Evidence |
|------|--------|----------|
| 6a.1 schemas/strategies.py | COMPLETE | All required classes present |
| 6a.2 services/strategy_service.py | COMPLETE | 7 functions + StrategyNotFoundError |
| 6a.3 api/strategies.py | COMPLETE | 7 endpoints on /strategies prefix |
| 6a.4 main.py wiring | COMPLETE | strategies router included at line 34 |
| 6a.5 test_strategy_service.py | COMPLETE | 13 tests, all pass |
| 6a.6 test_strategies_api.py | COMPLETE | 15 tests, all pass |

---

## Spec Compliance Matrix

### R1 -- Strategy CRUD

| Req | Status | Evidence |
|-----|--------|----------|
| R1.1 POST /strategies 201 | PASS | api:25 HTTP_201_CREATED; test_create_strategy_201 |
| R1.2 GET ordered by created_at DESC | WARNING | service orders is_primary DESC then created_at DESC; spec says created_at DESC only |
| R1.3 GET /{id} 404 on mismatch | PASS | api:41-43; test_get_strategy_foreign_404 |
| R1.4 PUT preserves flags | PASS | partial update_strategy; test_update_strategy_preserves_flags |
| R1.5 DELETE 204 cascades | PASS | api:61-69; model cascade=all,delete-orphan |
| R1.6 JWT required | PASS | All 7 endpoints Depends(get_current_user); test_unauthenticated_all_routes_401 |

### R2 -- Active/Inactive Toggle

| Req | Status | Evidence |
|-----|--------|----------|
| R2.1 PATCH /activate | PASS | api:72-84, ActivateRequest schema |
| R2.2 Deactivating primary does NOT clear is_primary | PASS | service:129; test_set_active_false_keeps_primary |
| R2.3 Full resource in response | PASS | response_model=StrategyOut |

### R3 -- Single-Primary Enforcement

| Req | Status | Evidence |
|-----|--------|----------|
| R3.1 PATCH /primary sets is_primary=true | PASS | api:87-96 |
| R3.2 Atomic bulk UPDATE + commit | PASS | service:153-166 single db.commit(); test_set_primary_clears_others |
| R3.3 Clear leaves 0 primaries allowed | WARNING | No unset endpoint; PATCH /primary always promotes; zero-primary state not achievable directly |
| R3.4 is_primary not settable via PUT | PASS | StrategyUpdate excludes is_primary (schemas:70-80) |

### R4 -- Rules and Style Validation

| Req | Status | Evidence |
|-----|--------|----------|
| R4.1 style enum | PASS | StrategyStyle:22-27; test_create_strategy_invalid_style_422 |
| R4.2 Known rule keys | WARNING | 12 fields (DD2 superset) vs spec 8; rsi_exit_min not rsi_entry_min; min_free_cash_flow_ttm dropped |
| R4.3 Non-negative constraints | PASS | max_pe gt=0, ge=0 on applicable fields |
| R4.4 Extra keys rejected | PASS | extra=forbid; test_create_strategy_extra_rules_key_422 |
| R4.5 is_training_ready read-only | PASS | Excluded from all request schemas |

### R5 -- Ownership Scoping

| Req | Status | Evidence |
|-----|--------|----------|
| R5.1 Every query filters by user_id | PASS | All service functions include user_id predicate |
| R5.2 StrategyNotFoundError to 404 | PASS | Generic detail; test_get_strategy_foreign_404 |

### R6 -- API Schema Contracts

| Req | Status | Evidence |
|-----|--------|----------|
| R6.1 StrategyCreateRequest | PASS | StrategyCreate inherits StrategyBase (name/style/rules required) |
| R6.2 StrategyUpdateRequest | WARNING | Spec: all required. Impl: all optional/partial. Resolved design decision. |
| R6.3 StrategyResponse | PASS | StrategyOut:83-99 excludes user_id, all three flags present |
| R6.4 ActivateRequest | PASS | schemas:102-103 |
| R6.5 PrimaryRequest schema | WARNING | Class absent; PATCH /primary is bodyless. Design decision documented. |

### R10 -- Test Coverage

| Req | Status | Evidence |
|-----|--------|----------|
| R10.1 service tests | PASS | 13 tests, all required scenarios |
| R10.2 API tests | PASS | 15 tests; 422/404/auth cases |
| R10.3 pytest passes | PASS | 109 passed, 0 failures, 0 skips |

### Scenarios

| Scenario | Status | Covering Test |
|----------|--------|---------------|
| S1 Create defaults | PASS | test_create_strategy_201, test_create_strategy_defaults |
| S2 List own only | PASS | test_get_strategies_own_only |
| S3 Invalid style 422 | PASS | test_create_strategy_invalid_style_422 |
| S4 Single-primary | PASS | test_set_primary_clears_others, test_set_primary_clears_previous |
| S5 Deactivate keeps primary | PASS | test_set_active_false_keeps_primary, test_activate_strategy_false |
| S6 Foreign 404 | PASS | test_delete_strategy_foreign_returns_false, test_delete_strategy_foreign_404 |
| S7 is_training_ready read-only | PASS | test_update_strategy_strips_training_ready |
| S8 (frontend) | OUT OF SCOPE | 6b.x pending |
| S9 (frontend) | OUT OF SCOPE | 6b.x pending |
| S10 Unauthenticated 401 | PASS | test_unauthenticated_all_routes_401 |

---

## Design Coherence

| Check | Status | Notes |
|-------|--------|-------|
| Layered pattern | PASS | Matches portfolio/analysis module structure |
| Single-primary atomic invariant | PASS | Bulk UPDATE + targeted set + single commit (service:153-166) |
| Decimal to float serialization | PASS | _rules_to_json() handles SQLite JSON column limitation |
| Partial PUT semantics | PASS (design decision) | model_dump(exclude_unset=True); documented |
| Ownership scoping | PASS | user_id predicate in all service functions |
| is_active/is_primary excluded from StrategyUpdate | PASS | Dedicated PATCH endpoints only |

---

## Issues

### CRITICAL
None.

### WARNING

W1 -- R1.2 ordering deviation
Spec: ordered by created_at descending.
Impl: is_primary DESC, created_at DESC (primary-first).
File: backend/app/services/strategy_service.py:32-35
Impact: benign UX improvement; no consumer broken. Recommend updating spec text.

W2 -- R4.2 rules key set divergence
Spec lists 8 keys including rsi_entry_min and min_free_cash_flow_ttm.
Impl: 12 keys per DD2 (rsi_exit_min semantic rename, adds risk-sizing, drops min_free_cash_flow_ttm).
File: backend/app/schemas/strategies.py:47-55
Impact: min_free_cash_flow_ttm cannot be set; rsi_entry_min would 422. Spec should be updated.

W3 -- R6.2 partial vs. full replacement semantics
Spec: all fields required. Impl: all optional, partial update applied.
File: backend/app/schemas/strategies.py:70-80
Impact: documented design decision aligning with prior deliverables. Spec text needs update.

W4 -- R6.5 PrimaryRequest schema missing
Spec defines PrimaryRequest {is_primary: bool}. Impl: PATCH /primary bodyless, always promotes.
File: backend/app/api/strategies.py:87-96
Impact: zero-primary state not achievable via API. Intentional; spec R6.5 and R3.3 need alignment.

### SUGGESTION

S1 -- httpx cookie deprecation warnings (70 warnings)
Files: backend/tests/test_strategies_api.py and other test files.
Recommendation: migrate to client-level cookies when upgrading httpx.

---

## Verdict

PASS WITH WARNINGS

0 CRITICALs | 4 WARNINGs | 1 SUGGESTION

All 109 tests pass. The 4 warnings are spec-text/documentation drift against design decisions
already documented in apply-progress. No code changes required before merge.

## Out of Scope (Pending -- 6b.x)
R7, R8, R9, R10.4 (next build), S8, S9 -- frontend requirements.
Tasks 6b.1--6b.11 not implemented yet.
