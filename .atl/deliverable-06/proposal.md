# Proposal: Deliverable-06 — Strategy Management Module

## Intent

Deliverables 1-5 ship auth, portfolio/watchlist CRUD, data ingestion, and fundamental + technical analysis. The downstream signal engine (D7), backtester (D9), and fine-tuned model all read from `investment_strategies`, yet no API, service, schema, or UI exists to create or manage strategy profiles. This deliverable exposes full strategy lifecycle management so users can author the quantitative rules that drive every later module.

## Scope

### In Scope
- `strategy_service.py`: CRUD + business rules (single-primary enforcement, active/inactive toggle, ownership scoping).
- `api/strategies.py`: REST endpoints — `GET/POST /strategies`, `GET/PUT/DELETE /strategies/{id}`, `PATCH /strategies/{id}/activate`, `PATCH /strategies/{id}/primary`.
- `schemas/strategies.py`: Pydantic contracts incl. a validated `rules` payload (max_pe, min_roe, min_dividend_yield, rsi_entry_max, ema_crossover, etc.) and `style` enum (value/growth/momentum/dividend/hybrid).
- Frontend: `/strategies` manager list page, `/strategies/[id]` detail page, `StrategyCard`, `StrategyRulesEditor`, active/inactive switch, primary selector. API client + types.
- Backend pytest coverage and passing Next.js build.

### Out of Scope
- Backtest execution and performance metrics display (D9 — `StrategyComparePanel` and backtest fields deferred).
- Signal generation / signal log tagging (D7).
- Model retraining / `is_training_ready` workflow and JSONL export (D8/training).
- Any schema migration — table/model already exist.

## Capabilities

### New Capabilities
- `strategy-management`: CRUD, active/inactive toggle, single-primary selector, and rules editor for investment strategy profiles, user-scoped.

### Modified Capabilities
- None.

## Approach

Reuse the established layered pattern from portfolio/watchlist: `api/ → services/ → models/` with Pydantic `schemas/` contracts and `Depends(get_current_user)` ownership scoping. The `InvestmentStrategy` model and `investment_strategies` table already exist (`0001_initial_schema`), so no migration. Single-primary invariant enforced transactionally in the service (clear prior primary before setting new). Validate `rules` JSON shape and `style` enum in schemas. Frontend mirrors portfolio page structure (App Router pages + presentational components + `lib/api.ts` client). `is_training_ready` exposed read-only; toggled by later deliverables.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `backend/app/services/strategy_service.py` | New | CRUD + primary/active invariants |
| `backend/app/api/strategies.py` | New | REST router + activate/primary endpoints |
| `backend/app/schemas/strategies.py` | New | Request/response + rules validation |
| `backend/app/main.py` (router wiring) | Modified | Register strategies router |
| `frontend/src/app/strategies/` | New | List + detail pages |
| `frontend/src/components/strategies/` | New | StrategyCard, StrategyRulesEditor |
| `frontend/src/lib/api.ts`, `types.ts` | Modified | Strategy client + types |
| `backend/tests/` | New | Service + API tests |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Concurrent primary toggles create two primaries | Med | Enforce within single transaction; unique partial constraint optional follow-up |
| Free-form `rules` JSON drifts from D7 consumer expectations | Med | Validate known keys in schema; document contract for signal engine |
| Frontend rules editor complexity (dynamic key/value) creep | Low | Ship typed form for known rule keys; defer arbitrary-key editor |

## Rollback Plan

All-new files plus a one-line router registration. Revert by removing `strategies.py`/`strategy_service.py`/`schemas/strategies.py`, the frontend `strategies/` dirs, and the `main.py` router line. No migration ran, so no DB rollback. Single PR or two-slice (backend / frontend) revert.

## Dependencies

- Existing `InvestmentStrategy` model + `users` FK (present).
- Auth `get_current_user` dependency (D1, present).

## Success Criteria

- [ ] Authenticated user can create, list, edit, delete strategies scoped to their account.
- [ ] Active/inactive toggle and single-primary selector enforced server-side.
- [ ] Rules and style validated; invalid payloads rejected with 422.
- [ ] Backend pytest suite green; Next.js build passes.
