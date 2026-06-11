# Design: Strategy Management Module (Deliverable 6)

## Technical Approach

Expose the full lifecycle of `InvestmentStrategy` profiles through the established
layered pattern proven in portfolio/watchlist: `api/strategies.py → services/strategy_service.py → models/strategy.py`,
with Pydantic `schemas/strategies.py` contracts and `Depends(get_current_user)` ownership
scoping. The model and `investment_strategies` table already exist (`0001_initial_schema`),
so there is **no migration**. Two business invariants are enforced in the service layer:
the single-primary rule (transactional unset-then-set) and active-by-default toggling.
The `rules` JSON column is treated as a **typed contract** consumed downstream by the D7
signal engine — its known keys are pinned and validated in Pydantic. The frontend mirrors
the portfolio App Router structure: list page, detail/edit page, presentational components,
and a typed `lib/api.ts` strategy client.

## Architecture

```
api/strategies.py                       ← NEW: REST router, ownership-scoped
      │   GET/POST   /strategies
      │   GET/PUT/DELETE /strategies/{id}
      │   PATCH /strategies/{id}/activate
      │   PATCH /strategies/{id}/primary
      ▼
services/strategy_service.py            ← NEW: CRUD + invariants
      │   ├── get_strategies(user)         list (primary first, then created_at desc)
      │   ├── get_strategy(id, user)       ownership-scoped fetch
      │   ├── create_strategy(...)         honors is_primary on create
      │   ├── update_strategy(...)         partial; re-validates rules
      │   ├── delete_strategy(...)
      │   ├── set_active(id, user, bool)
      │   └── set_primary(id, user)        ← transactional unset-then-set
      ▼
models/strategy.py (InvestmentStrategy)  ← EXISTING, untouched
      │
schemas/strategies.py                    ← NEW: contracts + StrategyRules validation
```

## Design Decision 1 — Single-Primary Invariant (service-layer, transactional)

There is **no DB-level partial unique constraint** in scope (the proposal lists it as an
optional follow-up, and adding one requires a migration which is explicitly out of scope).
The invariant "at most one primary strategy per user" is enforced entirely in the service
inside a **single transaction** using an atomic bulk UPDATE before the targeted set:

```python
async def set_primary(db: AsyncSession, strategy_id: str, user_id: str) -> InvestmentStrategy | None:
    strategy = await get_strategy(db, strategy_id, user_id)
    if strategy is None:
        return None
    # 1. Clear any existing primary for this user in ONE statement (no row-by-row loop).
    await db.execute(
        update(InvestmentStrategy)
        .where(
            InvestmentStrategy.user_id == uuid.UUID(user_id),
            InvestmentStrategy.is_primary.is_(True),
        )
        .values(is_primary=False)
    )
    # 2. Set the target primary.
    strategy.is_primary = True
    # 3. Commit once — both writes succeed or both roll back.
    await db.commit()
    await db.refresh(strategy)
    return strategy
```

Rationale:
- A single `await db.commit()` wraps the clear + set, so a crash mid-operation cannot leave
  two primaries (atomicity from the surrounding transaction).
- The bulk `update(...)` avoids loading and mutating every row individually; it touches only
  the currently-primary row(s).
- `create_strategy` applies the same rule: if `is_primary=True` is requested on create, the
  service clears prior primaries first, in the same transaction, then inserts.

Concurrency note: without a DB constraint, two *simultaneous* `set_primary` calls from the
same user could theoretically interleave. This is accepted for D6 (single-user UI, low
contention). The mitigation (partial unique index `WHERE is_primary`) is documented as a
D-future migration. We do NOT add it now because it would violate the no-migration scope.

`set_active(is_active=False)` does NOT auto-clear primary — an inactive primary remains the
declared primary (the signal engine decides whether to honor inactive strategies). This keeps
the two toggles orthogonal and is documented in the rules contract section.

## Design Decision 2 — `rules` JSON Contract (pinned + validated)

The `rules` column is a `dict` consumed by the D7 signal engine. To prevent drift, D6 pins a
**typed `StrategyRules` schema** with a fixed set of known, optional keys. All keys are
optional (a strategy may constrain on any subset), but unknown keys are **rejected** so the
contract cannot silently expand.

```python
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

class StrategyRules(BaseModel):
    model_config = ConfigDict(extra="forbid")   # reject unknown keys -> 422

    # --- Fundamental thresholds ---
    max_pe: Decimal | None = Field(default=None, gt=0)
    min_roe: Decimal | None = Field(default=None)              # percent, e.g. 15 = 15%
    min_dividend_yield: Decimal | None = Field(default=None, ge=0)
    max_debt_to_equity: Decimal | None = Field(default=None, ge=0)
    min_revenue_growth: Decimal | None = Field(default=None)

    # --- Technical thresholds (align with D5 indicators) ---
    rsi_entry_max: Decimal | None = Field(default=None, ge=0, le=100)
    rsi_exit_min: Decimal | None = Field(default=None, ge=0, le=100)
    ema_crossover: bool | None = Field(default=None)           # require golden cross
    macd_bullish: bool | None = Field(default=None)            # require bullish MACD

    # --- Position / risk sizing ---
    max_position_pct: Decimal | None = Field(default=None, gt=0, le=100)
    stop_loss_pct: Decimal | None = Field(default=None, gt=0, le=100)
    take_profit_pct: Decimal | None = Field(default=None, gt=0)
```

Validation approach:
- `extra="forbid"` makes any unknown key raise a 422 — the contract is closed.
- The create/update request schemas type `rules: StrategyRules` (NOT `dict`), so FastAPI
  validates the nested shape automatically and returns field-level 422 errors.
- On read, the stored `dict` is re-parsed through `StrategyRules` so the response surfaces a
  normalized, typed object (defaults to `null` for omitted keys, or we serialize only set keys
  via `model_dump(exclude_none=True)` — see Output schema).
- The `style` field is an enum, not free text:

```python
from enum import Enum
class StrategyStyle(str, Enum):
    VALUE = "value"
    GROWTH = "growth"
    MOMENTUM = "momentum"
    DIVIDEND = "dividend"
    HYBRID = "hybrid"
```

**Contract note for D7:** the signal engine reads these exact keys. Adding a new rule key is a
contract change that MUST update `StrategyRules` here first. Comparison semantics (`max_pe` is
an upper bound, `min_roe` a lower bound, boolean flags are "require this condition") are pinned
by the field naming convention and documented in the schema module docstring.

## Data Models (schemas/strategies.py)

```python
class StrategyBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    style: StrategyStyle
    description: str | None = Field(default=None, max_length=2000)
    rules: StrategyRules

class StrategyCreate(StrategyBase):
    is_active: bool = True
    is_primary: bool = False

class StrategyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    style: StrategyStyle | None = None
    description: str | None = Field(default=None, max_length=2000)
    rules: StrategyRules | None = None
    # is_active / is_primary intentionally NOT here — use dedicated PATCH endpoints

class StrategyOut(BaseModel):
    id: uuid.UUID
    name: str
    style: StrategyStyle
    description: str | None
    rules: StrategyRules
    is_active: bool
    is_primary: bool
    is_training_ready: bool          # read-only; toggled by later deliverables
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("id")
    def serialize_id(self, value: uuid.UUID) -> str:
        return str(value)
```

Toggle request bodies:

```python
class ActivateRequest(BaseModel):
    is_active: bool
```

`is_primary` has no body — `PATCH /strategies/{id}/primary` always sets the target to primary
(idempotent). There is no "unset primary" endpoint in D6 (a user always has 0-or-1 primary;
the only way to change it is to promote another).

## API Endpoints (api/strategies.py)

| Method | Path | Body | Response | Notes |
|--------|------|------|----------|-------|
| GET | `/strategies` | — | `list[StrategyOut]` | ownership-scoped, primary first |
| POST | `/strategies` | `StrategyCreate` | `StrategyOut` 201 | honors is_primary atomically |
| GET | `/strategies/{id}` | — | `StrategyOut` | 404 if not owned |
| PUT | `/strategies/{id}` | `StrategyUpdate` | `StrategyOut` | partial; 404 if not owned |
| DELETE | `/strategies/{id}` | — | 204 | 404 if not owned |
| PATCH | `/strategies/{id}/activate` | `ActivateRequest` | `StrategyOut` | toggle is_active |
| PATCH | `/strategies/{id}/primary` | — | `StrategyOut` | transactional unset-then-set |

Router: `APIRouter(prefix="/strategies", tags=["strategies"])`, registered in `main.py`
alongside the existing routers (one-line `app.include_router(strategies.router)` + import).

Errors:
- 404 `"Strategy not found"` when fetch returns `None` (covers both missing and not-owned —
  never leak existence of another user's strategy).
- 422 from Pydantic for invalid `rules`/`style`/unknown keys (automatic).

## Frontend Architecture

### Routing decision (important)

The existing `Sidebar.tsx` navigates to **`/strategy`** (singular), while the proposal text
says `/strategies`. To avoid a dead nav link, the frontend pages live under **`/strategy`**
(singular) to match the already-shipped sidebar. The backend REST prefix stays `/strategies`
(plural, RESTful resource). This is an intentional split: UI route `/strategy`, API resource
`/strategies`. (Alternative — change the sidebar to `/strategies` — is also viable but touches
shipped navigation; the singular UI route is the lower-risk choice.)

### Pages (App Router)

```
frontend/src/app/strategy/
├── page.tsx              ← NEW: list page (grid of StrategyCard) + "New strategy" link
├── new/page.tsx          ← NEW: create form (StrategyForm in create mode)
└── [id]/page.tsx         ← NEW: detail/edit (StrategyForm in edit mode + toggles)
```

This mirrors the portfolio layout (`portfolio/page.tsx`, `portfolio/new/page.tsx`,
`portfolio/[id]/edit/page.tsx`).

### Components (presentational, container-presentational split)

```
frontend/src/components/strategy/
├── StrategyCard.tsx          ← NEW: name, style badge, active/primary badges, rule summary count
├── StrategyForm.tsx          ← NEW: name/style/description + embeds StrategyRulesEditor
├── StrategyRulesEditor.tsx   ← NEW: TYPED form — one labelled input per known rule key
├── PrimaryToggle.tsx         ← NEW: "Set as primary" button (disabled when already primary)
└── ActiveToggle.tsx          ← NEW: active/inactive switch
```

**Rules editor — Design Decision 3 (typed form, defer arbitrary-key editor):**
`StrategyRulesEditor` renders a **fixed set of labelled inputs**, one per key in
`StrategyRules` (numeric inputs for thresholds, checkboxes for the boolean flags), grouped
into "Fundamental", "Technical", "Risk" sections. There is **no dynamic key/value add-row UI**
— this is deferred per the proposal risk mitigation. Empty inputs map to `undefined`/omitted
keys so the payload only carries the rules the user actually set. This keeps the editor a
straightforward controlled form fully aligned 1:1 with the pinned backend contract; when D7
or later expands `StrategyRules`, the editor adds a field rather than supporting free-form keys.

Component breakdown summary:
- `StrategyCard` — presentational, receives a `Strategy`, links to `/strategy/[id]`. Shows
  style badge + Active/Inactive + Primary badges (mirrors `WatchlistCard`).
- `StrategyForm` — controlled form; orchestrates name/style/description + `StrategyRulesEditor`;
  submit calls create or update via the api client.
- `StrategyRulesEditor` — typed grid of inputs, no free-form keys.
- `PrimaryToggle` / `ActiveToggle` — small action components hitting the PATCH endpoints; live
  on the detail page (and primary can also surface on each card on the list page).

### API client + types

`frontend/src/lib/api.ts` keeps the generic `apiFetch<T>`; strategy calls are thin wrappers
(or inline `apiFetch` calls in pages, matching current portfolio style). New types in
`frontend/src/lib/types.ts`:

```typescript
export type StrategyStyle = 'value' | 'growth' | 'momentum' | 'dividend' | 'hybrid';

export interface StrategyRules {
  max_pe?: string;
  min_roe?: string;
  min_dividend_yield?: string;
  max_debt_to_equity?: string;
  min_revenue_growth?: string;
  rsi_entry_max?: string;
  rsi_exit_min?: string;
  ema_crossover?: boolean;
  macd_bullish?: boolean;
  max_position_pct?: string;
  stop_loss_pct?: string;
  take_profit_pct?: string;
}

export interface Strategy {
  id: string;
  name: string;
  style: StrategyStyle;
  description: string | null;
  rules: StrategyRules;
  is_active: boolean;
  is_primary: boolean;
  is_training_ready: boolean;
  created_at: string;
  updated_at: string;
}

export interface StrategyCreate {
  name: string;
  style: StrategyStyle;
  description?: string;
  rules: StrategyRules;
  is_active?: boolean;
  is_primary?: boolean;
}

export interface StrategyUpdate {
  name?: string;
  style?: StrategyStyle;
  description?: string;
  rules?: StrategyRules;
}
```

(Decimal-backed fields are serialized as strings on the backend and typed as `string` here,
matching the existing `PortfolioPosition` convention.)

## Integration Points

- **Auth (D1):** `Depends(get_current_user)` + `get_db` from `app.api.deps` — unchanged.
- **D7 signal engine (future):** consumes `StrategyRules` keys. This module is the contract
  owner; document it in the schema module docstring.
- **D9 backtester / D8 training (future):** read `is_primary`, `is_active`, `is_training_ready`.
  D6 exposes them read (training_ready read-only) and writes the first two via toggles.
- **Sidebar:** existing `/strategy` link now resolves to a real page.

## Directory Structure

```
backend/app/
├── services/strategy_service.py    # NEW
├── api/strategies.py               # NEW
├── schemas/strategies.py           # NEW
├── main.py                         # MODIFIED: import + include_router (1 line each)

backend/tests/
├── test_strategy_service.py        # NEW: invariants (single-primary, ownership, active)
├── test_strategies_api.py          # NEW: endpoint + 422/404 coverage

frontend/src/
├── app/strategy/page.tsx           # NEW
├── app/strategy/new/page.tsx       # NEW
├── app/strategy/[id]/page.tsx      # NEW
├── components/strategy/StrategyCard.tsx          # NEW
├── components/strategy/StrategyForm.tsx          # NEW
├── components/strategy/StrategyRulesEditor.tsx   # NEW
├── components/strategy/PrimaryToggle.tsx         # NEW
├── components/strategy/ActiveToggle.tsx          # NEW
├── lib/types.ts                    # MODIFIED: Strategy* types
```

## ADR Summary

| # | Decision | Rationale | Rejected Alternative |
|---|----------|-----------|----------------------|
| 1 | Single-primary enforced in service via bulk-UPDATE + single commit | No-migration scope; atomic within one transaction | DB partial unique index (needs migration, out of scope) — deferred to D-future |
| 2 | `rules` typed as closed `StrategyRules` schema with `extra="forbid"` | Pins the D7 contract; field-level 422; prevents silent drift | `rules: dict` free-form (drift risk, no validation) |
| 3 | Typed rules editor (fixed inputs per known key) | Lowest complexity; 1:1 with backend contract | Dynamic key/value editor (creep risk) — deferred |
| 4 | Toggles via dedicated PATCH endpoints, excluded from PUT body | Keeps invariant logic isolated; PUT stays pure field edit | Allowing is_primary/is_active in PUT (bypasses invariant transaction) |
| 5 | UI route `/strategy` (singular), API `/strategies` (plural) | Matches already-shipped Sidebar link; avoids dead nav | `/strategies` UI (would require editing shipped navigation) |
| 6 | Inactive does not clear primary | Toggles orthogonal; signal engine decides | Auto-unset primary on deactivate (hidden coupling) |

## Review Workload Forecast

| Layer | Files | Est. Lines |
|-------|-------|-----------|
| Schemas | 1 new | ~120 |
| Strategy service | 1 new | ~120 |
| Strategies API | 1 new | ~120 |
| main.py wiring | 1 modified | ~2 |
| Backend tests | 2 new | ~220 |
| Frontend pages | 3 new | ~220 |
| Frontend components | 5 new | ~320 |
| types.ts | 1 modified | ~60 |
| **Total** | **~15 files** | **~1180 lines** |

> Risk: HIGH on size. Recommend chained PRs:
> - **PR 6a (backend):** schemas + service + API + main.py + backend tests (~580 lines)
> - **PR 6b (frontend):** pages + components + types (~600 lines)
>
> Each slice is independently revertible (proposal rollback plan supports backend/frontend
> two-slice revert). No DB migration in either slice.
