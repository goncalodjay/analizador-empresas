# Tasks: Strategy Management Module (Deliverable 6)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1 180 |
| 400-line budget risk | HIGH |
| Chained PRs recommended | Yes |
| Suggested split | PR 6a (backend, ~580 lines) → PR 6b (frontend, ~600 lines) |
| Decision needed before apply | Yes |

**Rationale:** The design estimates 15 files across ~1 180 lines — nearly 3× the 400-line
safe budget. The backend and frontend slices have a clean seam: the frontend only needs the
API contract (already documented), not the backend implementation, to start. Each slice is
independently revertible with no migration in either. The 6a → 6b ordering is recommended
(frontend can mock-build against the types before the backend is deployed, then wire live in
the same PR).

---

## PR 6a: Backend — Schemas → Service → API → Tests (~580 lines)

_Ordered so each task can build on the previous with no circular dependencies._
_All tasks in this PR are sequential._

### [x] Task 6a.1 — `schemas/strategies.py` — Pydantic contracts
**Files:** `backend/app/schemas/strategies.py` (NEW)

Define all schema types needed by the service and router:

- `StrategyStyle` enum: `value | growth | momentum | dividend | hybrid`
- `StrategyRules` with `model_config = ConfigDict(extra="forbid")` — 12 optional fields
  (`max_pe`, `min_roe`, `min_dividend_yield`, `max_debt_to_equity`, `min_revenue_growth`,
  `rsi_entry_max`, `rsi_exit_min`, `ema_crossover`, `macd_bullish`, `max_position_pct`,
  `stop_loss_pct`, `take_profit_pct`) with type constraints per design DD2
- `StrategyBase`, `StrategyCreate`, `StrategyUpdate` (partial, excludes is_active/is_primary)
- `StrategyOut` with `from_attributes=True` and UUID serializer
- `ActivateRequest` (`is_active: bool`)
- Module-level docstring documenting D7 contract ownership and comparison semantics

**Spec refs:** R4.1, R4.2, R4.3, R4.4, R4.5, R6.1–R6.5

**Acceptance:**
- `from app.schemas.strategies import StrategyCreate, StrategyOut, StrategyRules` resolves
- `StrategyRules(max_pe=-1)` raises `ValidationError` (gt=0 constraint)
- `StrategyRules(unknown_key=1)` raises `ValidationError` (extra="forbid")
- `StrategyRules.model_validate({"rsi_entry_max": 150})` raises ValidationError (le=100)

---

### [x] Task 6a.2 — `services/strategy_service.py` — CRUD + invariants
**Files:** `backend/app/services/strategy_service.py` (NEW)

Implement all service functions (async, accept `AsyncSession`):

- `get_strategies(db, user_id)` → `list[InvestmentStrategy]`, ordered primary-first then
  `created_at DESC`
- `get_strategy(db, strategy_id, user_id)` → `InvestmentStrategy | None` (ownership-scoped)
- `create_strategy(db, data: StrategyCreate, user_id)` → `InvestmentStrategy`; if
  `data.is_primary=True`, clear all other user primaries in the same transaction first
- `update_strategy(db, strategy_id, data: StrategyUpdate, user_id)` → `InvestmentStrategy | None`;
  partial update (only supplied fields); re-validates rules via `StrategyRules.model_validate`
- `delete_strategy(db, strategy_id, user_id)` → `bool` (False = not found)
- `set_active(db, strategy_id, user_id, is_active: bool)` → `InvestmentStrategy | None`
- `set_primary(db, strategy_id, user_id)` → `InvestmentStrategy | None`; atomic
  bulk-UPDATE unset then targeted set, single `await db.commit()`

Define `StrategyNotFoundError(Exception)` in this module (re-used by the router).

**Spec refs:** R1.1–R1.6, R2.1–R2.3, R3.1–R3.4, R5.1–R5.2

**Acceptance:**
- Setting primary on strategy Y atomically clears strategy X's `is_primary` in one commit
- Deactivating a primary strategy leaves `is_primary` unchanged
- `get_strategy` with a foreign user_id returns `None`
- `delete_strategy` on a non-existent ID returns `False`

---

### [x] Task 6a.3 — `api/strategies.py` — REST router
**Files:** `backend/app/api/strategies.py` (NEW)

Wire all 7 endpoints from the design table:

| Method | Path | Handler |
|--------|------|---------|
| GET | `/strategies` | list, ordered per service |
| POST | `/strategies` | create, 201 |
| GET | `/strategies/{id}` | get, 404 on None |
| PUT | `/strategies/{id}` | update, 404 on None |
| DELETE | `/strategies/{id}` | delete, 204 |
| PATCH | `/strategies/{id}/activate` | set_active |
| PATCH | `/strategies/{id}/primary` | set_primary (no body) |

- `APIRouter(prefix="/strategies", tags=["strategies"])`
- Every endpoint: `Depends(get_current_user)`, `Depends(get_db)`
- 404 response: `{"detail": "Strategy not found"}` — never exposes ownership distinction
- 422 from Pydantic is automatic; do not catch it

**Spec refs:** R1.1–R1.6, R2.1–R2.3, R3.1–R3.4, R5.1–R5.2, R6.1–R6.5, S10

**Acceptance:**
- All 7 routes registered and visible in `/docs`
- Unauthenticated request to any route → 401 (Depends(get_current_user) enforces this)
- `DELETE /strategies/{id}` returns 204 with no body

---

### [x] Task 6a.4 — `main.py` wiring
**Files:** `backend/app/main.py` (MODIFY)

Add to the import line:

```python
from app.api import analysis, auth, health, ingestion, portfolio, strategies, watchlists
```

Add after the existing `include_router` calls:

```python
app.include_router(strategies.router)
```

**Spec refs:** R1.6 (all endpoints reachable)

**Acceptance:**
- `uvicorn app.main:app` starts without import error
- `/docs` lists the `strategies` tag with all 7 endpoints

---

### [x] Task 6a.5 — `tests/test_strategy_service.py` — service-layer tests
**Files:** `backend/tests/test_strategy_service.py` (NEW)

Test cases (use `pytest-asyncio`, `AsyncSession`, in-memory or test-DB fixture matching
existing test patterns):

- `test_create_strategy_defaults` — `is_active=True`, `is_primary=False`, `is_training_ready=False`
- `test_create_strategy_as_primary_clears_other` — verifies S4 atomicity: existing primary
  flips to False when new strategy is created with `is_primary=True`
- `test_get_strategies_own_only` — user A sees only their own strategies (S2)
- `test_get_strategy_foreign_returns_none` — S6 ownership: foreign ID → None
- `test_update_strategy_preserves_flags` — `update_strategy` does not alter `is_active` or
  `is_primary`
- `test_update_strategy_strips_training_ready` — `is_training_ready` unchanged (S7)
- `test_delete_strategy_success` — deletes and returns True
- `test_delete_strategy_foreign_returns_false` — S6
- `test_set_active_false_keeps_primary` — S5: deactivate primary → `is_primary` stays True
- `test_set_primary_clears_others` — S4: X primary, call set_primary(Y), X flips to False
- `test_set_primary_clear_leaves_none` — clearing primary leaves 0 primaries (R3.3)
- `test_rules_validation_rejects_unknown_key` — S3-style validation
- `test_get_strategy_ownership_scoping` — R5.1

**Spec refs:** R10.1, S2, S4, S5, S6, S7

**Acceptance:** `pytest backend/tests/test_strategy_service.py` passes, no skips

---

### [x] Task 6a.6 — `tests/test_strategies_api.py` — API-layer tests
**Files:** `backend/tests/test_strategies_api.py` (NEW)

Test cases using the existing `TestClient`/`AsyncClient` fixture pattern:

- `test_create_strategy_201` — authenticated, valid body → 201 + StrategyOut shape
- `test_create_strategy_invalid_style_422` — S3: style="speculative" → 422
- `test_create_strategy_invalid_rules_422` — negative `max_pe` → 422
- `test_create_strategy_extra_rules_key_422` — extra key → 422 (R4.4)
- `test_list_strategies_authenticated` — 200, list shape
- `test_list_strategies_unauthenticated_401` — S10
- `test_get_strategy_own_200` — 200 + full resource
- `test_get_strategy_foreign_404` — S6
- `test_update_strategy_200` — valid body → 200
- `test_update_strategy_training_ready_ignored` — S7: field silently dropped
- `test_delete_strategy_204` — 204, no body
- `test_delete_strategy_foreign_404` — S6
- `test_activate_strategy_false` — S5: is_active flips, is_primary unchanged in response
- `test_set_primary_clears_previous` — S4: previous primary flips in same response cycle
- `test_unauthenticated_all_routes_401` — all 7 routes return 401 without token (R1.6)

**Spec refs:** R10.2, S3, S4, S5, S6, S7, S10

**Acceptance:** `pytest backend/tests/test_strategies_api.py` passes, no skips; combined
suite (`pytest backend/`) passes with all existing tests still green (≥81 passing)

---

## PR 6b: Frontend — Types → API Client → Components → Pages → Build (~600 lines)

_Can be branched from 6a after merge, or prepared in parallel and wired once 6a is deployed._
_Tasks within this PR are sequential._

### [x] Task 6b.1 — `lib/types.ts` — Strategy type additions
**Files:** `frontend/src/lib/types.ts` (MODIFY)

Append the following exports (do not disturb existing types):

- `StrategyStyle` union: `'value' | 'growth' | 'momentum' | 'dividend' | 'hybrid'`
- `StrategyRules` interface — 12 optional fields matching D6 backend schema; numeric fields
  typed as `string` (Decimal serialized), booleans as `boolean` (matching PortfolioPosition
  convention for Decimals)
- `Strategy` interface — all columns except `user_id`; includes `is_training_ready: boolean`
- `StrategyCreate` interface — `name`, `style`, `rules` required; `description`, `is_active`,
  `is_primary` optional
- `StrategyUpdate` interface — all fields optional; excludes `is_active`, `is_primary`

**Spec refs:** R9.2

**Acceptance:** `next build` passes; TypeScript resolves all Strategy* imports from
`@/lib/types`

---

### [x] Task 6b.2 — `lib/api.ts` — Strategy API client functions
**Files:** `frontend/src/lib/api.ts` (MODIFY)

Add the 7 strategy functions (follow existing `apiFetch<T>` pattern):

- `getStrategies(): Promise<Strategy[]>`
- `getStrategy(id: string): Promise<Strategy>`
- `createStrategy(data: StrategyCreate): Promise<Strategy>`
- `updateStrategy(id: string, data: StrategyUpdate): Promise<Strategy>`
- `deleteStrategy(id: string): Promise<void>`
- `activateStrategy(id: string, isActive: boolean): Promise<Strategy>` — body:
  `{ is_active: isActive }`
- `setPrimaryStrategy(id: string): Promise<Strategy>` — `PATCH .../primary` (no body)

All functions throw a typed error with HTTP status and message body on non-2xx (matching
existing error-handling pattern in the file).

**Spec refs:** R9.1, R9.3

**Acceptance:** `next build` passes; TypeScript shows no implicit `any` on return types

---

### [x] Task 6b.3 — `components/strategy/ActiveToggle.tsx`
**Files:** `frontend/src/components/strategy/ActiveToggle.tsx` (NEW)

Presentational + wired toggle switch:

- Props: `strategyId: string`, `isActive: boolean`, `onToggle: (updated: Strategy) => void`
- Renders a `<button role="switch">` (or `<input type="checkbox">`) labeled
  "Active" / "Inactive"
- On click: calls `activateStrategy(strategyId, !isActive)`, then calls `onToggle` with the
  returned `Strategy`; shows a loading state during the call
- Error: surface inline (toast or inline text — match existing UI patterns)

**Spec refs:** R7.3, S9

**Acceptance:** `next build` passes; toggle calls PATCH endpoint and reflects new state
without navigation

---

### [x] Task 6b.4 — `components/strategy/PrimaryToggle.tsx`
**Files:** `frontend/src/components/strategy/PrimaryToggle.tsx` (NEW)

Presentational + wired "Set as Primary" button:

- Props: `strategyId: string`, `isPrimary: boolean`, `onSet: (updated: Strategy) => void`
- Renders a button labeled "Set as Primary"; disabled (and shows a "Primary" badge) when
  `isPrimary === true`
- On click: calls `setPrimaryStrategy(strategyId)`, then calls `onSet` with the returned
  `Strategy`; shows loading state
- Parent is responsible for updating all other cards' `isPrimary` to `false` after `onSet`
  fires (the server returns the updated target, not the full list)

**Spec refs:** R7.4, S4

**Acceptance:** `next build` passes; button is disabled when already primary; clicking calls
PATCH and propagates result to parent

---

### [x] Task 6b.5 — `components/strategy/StrategyRulesEditor.tsx`
**Files:** `frontend/src/components/strategy/StrategyRulesEditor.tsx` (NEW)

Typed, controlled form section for `StrategyRules`:

- Props: `value: StrategyRules`, `onChange: (rules: StrategyRules) => void`
- Renders 3 labeled groups:
  - **Fundamental:** `max_pe`, `min_roe`, `min_dividend_yield`, `max_debt_to_equity`,
    `min_revenue_growth` — `<input type="number">`
  - **Technical:** `rsi_entry_max`, `rsi_exit_min` — numeric inputs; `ema_crossover`,
    `macd_bullish` — `<input type="checkbox">`
  - **Risk:** `max_position_pct`, `stop_loss_pct`, `take_profit_pct` — numeric inputs
- Empty numeric inputs map to `undefined` (key omitted from payload, not `null`)
- No dynamic key/value add-row UI — fixed fields only

**Spec refs:** R8.2, R4.2, S8

**Acceptance:** `next build` passes; changing a field calls `onChange` with the merged
`StrategyRules`; empty inputs produce omitted keys (not `null`) in the resulting object

---

### [x] Task 6b.6 — `components/strategy/StrategyCard.tsx`
**Files:** `frontend/src/components/strategy/StrategyCard.tsx` (NEW)

Presentational card (mirrors `WatchlistCard` structure):

- Props: `strategy: Strategy`, `onActivateToggle: (updated: Strategy) => void`,
  `onPrimarySet: (updated: Strategy) => void`, `onDelete: (id: string) => void`
- Displays: name (link to `/strategy/[id]`), `StrategyStyle` badge, Active/Inactive badge,
  Primary badge (when `is_primary=true`)
- Rule summary: shows count of non-null rules, e.g. "3 rules set" or top 2 key/value pairs
- Embeds `ActiveToggle` and `PrimaryToggle` (passing through callbacks)
- Delete button: shows a `window.confirm` before calling `deleteStrategy(id)` then
  calling `onDelete(id)`

**Spec refs:** R7.1–R7.6, S9

**Acceptance:** `next build` passes; card renders all badges; delete prompts confirmation

---

### [x] Task 6b.7 — `components/strategy/StrategyForm.tsx`
**Files:** `frontend/src/components/strategy/StrategyForm.tsx` (NEW)

Controlled form for create and edit modes:

- Props: `mode: 'create' | 'edit'`, `initial?: Strategy`, `onSuccess: () => void`
- Fields: `name` (`<input type="text">`), `style` (`<select>` with 5 options), `description`
  (`<textarea>`), and `<StrategyRulesEditor>` for the `rules` section
- In edit mode: pre-fills from `initial`; displays `is_training_ready` as a read-only badge
  (not editable); does NOT render `is_active` or `is_primary` controls (those are on the card
  / detail page separately)
- Submit: calls `createStrategy(data)` or `updateStrategy(id, data)` depending on mode;
  on success calls `onSuccess()` (caller navigates)
- Validation: `name` must be non-empty before submit; `style` must be selected

**Spec refs:** R8.1–R8.4, S7, S8

**Acceptance:** `next build` passes; edit form pre-fills all fields; `is_training_ready`
shows as badge, not input

---

### [x] Task 6b.8 — `app/strategy/page.tsx` — List page
**Files:** `frontend/src/app/strategy/page.tsx` (NEW)

- Client component (`'use client'`)
- On mount: calls `getStrategies()`, renders list of `StrategyCard` in a responsive grid
- State: `strategies: Strategy[]` — update in place after toggle/primary/delete callbacks
  (no full reload needed)
- Primary propagation: when `onPrimarySet` fires, set the new primary on the returned
  strategy and clear `is_primary` on all other cards in local state
- "New Strategy" button/link → navigates to `/strategy/new`
- Empty state: message when no strategies exist with a link to create

**Spec refs:** R7.1–R7.6

**Acceptance:** `next build` passes; Sidebar `/strategy` link resolves to this page; toggling
a card updates it without navigation

---

### [x] Task 6b.9 — `app/strategy/new/page.tsx` — Create page
**Files:** `frontend/src/app/strategy/new/page.tsx` (NEW)

- Renders `<StrategyForm mode="create" onSuccess={router.push('/strategy')} />`
- Shows page heading "New Strategy"
- `onSuccess` navigates back to `/strategy`

**Spec refs:** R7.5

**Acceptance:** `next build` passes; submitting a valid form creates the strategy and
redirects to the list

---

### [x] Task 6b.10 — `app/strategy/[id]/page.tsx` — Detail / Edit page
**Files:** `frontend/src/app/strategy/[id]/page.tsx` (NEW)

- On mount: calls `getStrategy(id)` from params
- 404 state: if the call throws a 404, renders a "Strategy not found" message (R8.5)
- Renders `<StrategyForm mode="edit" initial={strategy} onSuccess={router.push('/strategy')} />`
- Below the form: render `<ActiveToggle>` and `<PrimaryToggle>` for the current strategy,
  updating local state on callback
- `is_training_ready` badge shown within `StrategyForm` (see 6b.7)

**Spec refs:** R8.1–R8.5, S8

**Acceptance:** `next build` passes; navigating to `/strategy/[real-id]` loads the form
pre-filled; navigating to a bad ID renders the 404 state

---

### [x] Task 6b.11 — Final build verification
**Files:** none (verification only)

Run `next build` from `frontend/` and confirm:

- Zero TypeScript errors
- No `any`-typed strategy-related variables
- All new pages included in the build output

**Spec refs:** R10.4

**Acceptance:** `next build` exits 0 with no type errors

---

## Task Dependency Graph

```
PR 6a (sequential):
6a.1 → 6a.2 → 6a.3 → 6a.4 → 6a.5 → 6a.6

PR 6b (sequential, branches from 6a merge OR can start from 6a.1 types alone):
6b.1 → 6b.2 → 6b.3 → 6b.4 → 6b.5 → 6b.6 → 6b.7 → 6b.8 → 6b.9 → 6b.10 → 6b.11
```

PRs are independent slices. 6b can be drafted in parallel (the TypeScript types and API
client need only the agreed contract, not a running backend). The wiring of live API calls
in 6b.8–6b.10 is verified at `next build` time and does not require the backend to be
deployed.
