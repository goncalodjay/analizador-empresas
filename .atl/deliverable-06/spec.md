# Spec: Strategy Management Module (Deliverable 6)

## Intent

Expose full lifecycle management for `InvestmentStrategy` records: CRUD, active/inactive toggle,
single-primary enforcement, and a typed rules editor. All strategy access is user-scoped.
No schema migration — `investment_strategies` table and `InvestmentStrategy` model already exist.

---

## Requirements

### R1 — Strategy CRUD (Backend)

**R1.1** `POST /strategies` creates a new strategy owned by the authenticated user; returns the
created resource with HTTP 201.

**R1.2** `GET /strategies` returns all strategies belonging to the authenticated user, ordered by
`is_primary` descending then `created_at` descending (primary strategy listed first).
*(Amended post-verify: implementation orders primary-first; original text said `created_at` only.)*

**R1.3** `GET /strategies/{id}` returns a single strategy; returns HTTP 404 if the strategy does
not exist or belongs to a different user.

**R1.4** `PUT /strategies/{id}` replaces `name`, `description`, `style`, and `rules`; preserves
`is_active`, `is_primary`, and `is_training_ready`; returns HTTP 404 on ownership mismatch.

**R1.5** `DELETE /strategies/{id}` removes the record and cascades to `generated_signals`,
`model_versions`, and `backtest_results`; returns HTTP 204; returns HTTP 404 on ownership
mismatch.

**R1.6** All endpoints require a valid JWT (`Depends(get_current_user)`); unauthenticated
requests are rejected with HTTP 401.

---

### R2 — Active / Inactive Toggle

**R2.1** `PATCH /strategies/{id}/activate` accepts `{"is_active": true | false}` and updates the
field for the authenticated user's strategy.

**R2.2** Deactivating a strategy that is currently primary does NOT auto-clear `is_primary`; the
primary designation and active state are independent flags.

**R2.3** The response body includes the full updated strategy resource.

---

### R3 — Single-Primary Enforcement

**R3.1** `PATCH /strategies/{id}/primary` sets `is_primary = true` on the target strategy.

**R3.2** Within the same database transaction, all other strategies owned by the same user have
`is_primary` set to `false` before the target is updated — ensuring at most one primary exists
per user at any point.

**R3.3** The primary endpoint is promote-only: `PATCH /strategies/{id}/primary` takes no body and
always sets the target as primary. A zero-primary state exists only before any strategy has been
promoted (or after the primary strategy is deleted); it cannot be reached via the API directly.
*(Amended post-verify: original text allowed clearing via `{"is_primary": false}`; the implemented
endpoint is bodyless by design.)*

**R3.4** `is_primary` cannot be set via `PUT /strategies/{id}`; it is controlled exclusively
through the `/primary` sub-resource endpoint.

---

### R4 — Rules and Style Validation

**R4.1** `style` must be one of: `value`, `growth`, `momentum`, `dividend`, `hybrid`; any other
value is rejected with HTTP 422.

**R4.2** The `rules` object is validated against a closed set of 12 optional keys (design DD2,
contract owner: `backend/app/schemas/strategies.py`, consumed by the D7 signal engine):
- Fundamental: `max_pe`, `min_roe`, `min_dividend_yield`, `max_debt_to_equity`, `min_revenue_growth`
- Technical: `rsi_entry_max`, `rsi_exit_min`, `ema_crossover` (boolean), `macd_bullish` (boolean)
- Position/risk: `max_position_pct`, `stop_loss_pct`, `take_profit_pct`

All keys are optional; absent keys default to `null` / not enforced. `max_*` fields are upper
bounds, `min_*` fields are lower bounds, booleans require the condition to be true.
*(Amended post-verify: original draft listed 8 keys including `rsi_entry_min` and
`min_free_cash_flow_ttm`, which do not exist in the implemented contract.)*

**R4.3** Numeric rule values must be non-negative where applicable (e.g., `max_pe >= 0`,
`min_roe` unrestricted because ROE can be negative); type violations return HTTP 422.

**R4.4** Extra keys beyond the validated set are stripped (not persisted) unless the schema
explicitly permits a pass-through `extra_rules` bucket.

**R4.5** `is_training_ready` is read-only in all strategy creation and update payloads; it is
ignored if present in requests and toggled only by later deliverables (D8).

---

### R5 — Ownership Scoping

**R5.1** Every service-layer query filters by `user_id = current_user.id`; strategies from other
users are never returned, modified, or deleted regardless of the provided `{id}`.

**R5.2** The service raises a `StrategyNotFoundError` (mapped to HTTP 404) when a strategy does
not exist OR belongs to a different user — no distinction is made between "not found" and
"forbidden" to prevent enumeration.

---

### R6 — API Schema Contracts

**R6.1** `StrategyCreateRequest`: `name` (required, non-empty), `style` (required), `rules`
(required, validated per R4), `description` (optional).

**R6.2** `StrategyUpdate`: partial update — `name`, `style`, `description`, `rules` are all
optional; fields absent from the payload remain unchanged. `is_active` and `is_primary` are
excluded; they are controlled exclusively via the dedicated PATCH endpoints.
*(Amended post-verify: original text required full replacement; partial semantics were resolved
as a design decision matching prior deliverables.)*

**R6.3** `StrategyResponse`: all model columns except `user_id`; includes `is_active`,
`is_primary`, `is_training_ready` (read-only), `created_at`, `updated_at`.

**R6.4** `ActivateRequest`: `{ "is_active": bool }`.

**R6.5** `PATCH /strategies/{id}/primary` takes no request body (promote-only per R3.3); no
`PrimaryRequest` schema exists.
*(Amended post-verify: original text defined a `PrimaryRequest` body.)*

---

### R7 — Frontend: Strategy List Page (`/strategies`)

**R7.1** The page lists all strategies returned by `GET /strategies` as `StrategyCard` components.

**R7.2** Each `StrategyCard` displays: name, style badge, active/inactive status, primary
indicator, and a summary of the rules object (key count or top 2-3 key/value pairs).

**R7.3** An active/inactive toggle switch on each card calls `PATCH /strategies/{id}/activate`
and reflects the updated state without full page reload.

**R7.4** A "Set as Primary" button on each card calls `PATCH /strategies/{id}/primary`; the
previously-primary card updates to non-primary in the same render cycle.

**R7.5** A "New Strategy" button navigates to the creation form (inline or `/strategies/new`).

**R7.6** A delete action on each card calls `DELETE /strategies/{id}` and removes the card from
the list on success, with a confirmation prompt before execution.

---

### R8 — Frontend: Strategy Detail / Edit Page (`/strategies/[id]`)

**R8.1** The page loads the strategy via `GET /strategies/{id}` and pre-fills all fields.

**R8.2** `StrategyRulesEditor` renders a typed form for the known rule keys (R4.2); each key has
an appropriate input type (number, checkbox for boolean) and a label.

**R8.3** Submitting the form calls `PUT /strategies/{id}`; success redirects to `/strategies`.

**R8.4** `is_training_ready` is displayed as a read-only indicator (badge or label) and is not
editable from this page.

**R8.5** The page shows HTTP 404 state when the strategy does not exist or belongs to a different
user.

---

### R9 — API Client and Types (Frontend)

**R9.1** `frontend/src/lib/api.ts` exports: `getStrategies()`, `getStrategy(id)`,
`createStrategy(data)`, `updateStrategy(id, data)`, `deleteStrategy(id)`,
`activateStrategy(id, active)`, `setPrimaryStrategy(id)` (no payload — promote-only per R3.3).

**R9.2** `frontend/src/types.ts` (or a dedicated `strategy.ts`) exports: `Strategy`,
`StrategyCreatePayload`, `StrategyUpdatePayload`, `StrategyStyle` (union type),
`StrategyRules` (typed object with optional keys per R4.2).

**R9.3** All API functions handle non-2xx responses by throwing a typed error with the HTTP
status and message from the response body.

---

### R10 — Test Coverage

**R10.1** `backend/tests/test_strategy_service.py` covers: create, list, get by id (own and
foreign), update, delete, activate toggle, single-primary enforcement (setting primary clears
others), ownership scoping for every operation.

**R10.2** `backend/tests/test_strategy_api.py` covers: all seven endpoints with authenticated and
unauthenticated requests; 422 on invalid style and rule values; 404 on foreign-user strategy.

**R10.3** `pytest` suite passes with no failures and no skips on covered tests.

**R10.4** `next build` passes with no TypeScript errors.

---

## Scenarios

### S1: Create a strategy
```
GIVEN an authenticated user with no strategies
WHEN POST /strategies with name="Growth 2025", style="growth", rules={"max_pe": 30, "min_roe": 15}
THEN HTTP 201 is returned with the created strategy resource including a UUID, is_active=true,
     is_primary=false, is_training_ready=false
```

### S2: List returns only own strategies
```
GIVEN user A has 2 strategies and user B has 3 strategies
WHEN user A calls GET /strategies
THEN only 2 strategies are returned, none belonging to user B
```

### S3: Invalid style rejected
```
GIVEN an authenticated user
WHEN POST /strategies with style="speculative"
THEN HTTP 422 is returned with a validation error identifying the style field
```

### S4: Single-primary enforcement
```
GIVEN user has strategy X (is_primary=true) and strategy Y (is_primary=false)
WHEN PATCH /strategies/Y/primary (no body)
THEN strategy Y has is_primary=true AND strategy X has is_primary=false in a single transaction
```

### S5: Deactivate does not clear primary
```
GIVEN a strategy with is_active=true and is_primary=true
WHEN PATCH /strategies/{id}/activate with {"is_active": false}
THEN is_active=false AND is_primary remains true
```

### S6: Delete foreign strategy returns 404
```
GIVEN strategy Z belongs to user B
WHEN user A calls DELETE /strategies/Z
THEN HTTP 404 is returned; strategy Z still exists in the database
```

### S7: is_training_ready is read-only
```
GIVEN a strategy with is_training_ready=false
WHEN PUT /strategies/{id} with is_training_ready=true in the payload
THEN the field remains false; no error is raised (field is silently ignored)
```

### S8: Rules editor persists typed values
```
GIVEN user is on /strategies/[id] with StrategyRulesEditor
WHEN user sets max_pe=25, ema_crossover=true and submits
THEN PUT /strategies/{id} is called with rules={"max_pe": 25, "ema_crossover": true}
     and the list page reflects the updated rule summary
```

### S9: Toggle switch updates without reload
```
GIVEN user is on /strategies viewing a card with is_active=true
WHEN user flips the active toggle
THEN PATCH /strategies/{id}/activate is called; the card reflects is_active=false
     without a full page navigation
```

### S10: Unauthenticated request rejected
```
GIVEN no Authorization header or invalid token
WHEN any /strategies endpoint is called
THEN HTTP 401 is returned
```

---

## Out of Scope

- Backtest execution, performance metrics, and `StrategyComparePanel` (D9).
- Signal generation and signal log tagging per strategy (D7).
- `is_training_ready` toggling and JSONL export workflow (D8).
- Any database schema migration (table and model already exist).
- Arbitrary-key rules editor beyond the validated key set defined in R4.2.
