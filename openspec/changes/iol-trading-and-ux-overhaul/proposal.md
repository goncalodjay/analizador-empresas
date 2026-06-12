# Proposal: IOL Read-Only Integration and UX Overhaul

## Executive Summary

Transform the analizador-empresas app from a read-only analysis tool into an integrated investment dashboard by connecting to IOL API (read-only: portfolio sync, account status, market quotes), redesigning the UX with an auth gate, adding a dashboard with key metrics (invested, current value, P&L), and seeding validated base investment strategy templates. Estimated 280–400 hours; 5 chained PRs with clear dependencies. Trading (buy/sell) is explicitly out of scope.

---

## Intent

**Problem**: Users can analyze stocks and track a manual portfolio in the app, but cannot see their real IOL holdings and live account status without leaving the platform. Portfolio is manual-entry only, creating redundancy and sync friction.

**Why Now**: IOL API v2 is stable and available; exploration has confirmed endpoint availability and technical feasibility within the current stack. User wants a unified investment dashboard that reflects their real IOL holdings and account metrics in a single place.

**Success Looks Like**:
- User logs in to analizador-empresas, sees a secure dashboard with real IOL portfolio summary: total invested, current value, unrealized P&L
- Portfolio holdings auto-sync from IOL in real time (read-only, single source of truth)
- Analysis pages show prices and P&L in the currency of each holding (ARS for CEDEARs via IOL quotes, USD for ADRs via yfinance)
- Strategies section includes pre-built validated base strategy templates with descriptions and recommended timeframes
- Manual portfolio entry is deprecated; IOL is the only source of truth
- Secure IOL authentication with encrypted credentials and proactive token refresh

---

## Scope

### In Scope (Phase 1 MVP)

**Auth & UX Foundation**
- Login screen as initial gate; no navigation visible until authenticated
- Dashboard as investment summary: total invested, current capital, unrealized P&L

**IOL Integration (Backend)**
- OAuth2 Resource Owner Password Credentials client (backend-only)
- Secure token storage and proactive refresh (15-min TTL management)
- Encrypted IOL credential storage in environment or secure backend vault
- IOL onboarding: prompt for IOL username/password on first login (user enters once, backend stores encrypted)

**Portfolio**
- Auto-sync holdings from IOL API (currency, ticker, quantity, avg buy price)
- Read-only enforcement: IOL is source of truth; no manual portfolio edits
- Deprecate manual portfolio entry UI entirely
- Account status fetch: cash balance, buying power, account summary from IOL

**Pricing & P&L**
- Currency-aware market prices: ARS holdings → IOL BCBA quotes; USD holdings → yfinance
- Unrealized P&L calculation: current price vs. buy price per holding
- Portfolio summary: total invested (cost basis), current value, unrealized P&L, % return
- Realized P&L: include only if user has sold holdings (visible in IOL holdings history)

**Strategies**
- Pre-seeded base strategy templates: 3–5 validated templates (e.g., Value Investing, Growth, Income, Dollar-Cost Averaging)
- Each template includes: description, how it works, recommended timeframe, entry/exit rules (plain text, no backtesting)
- Custom strategy creation deferred to Phase 2
- Strategy backtesting deferred to Phase 2

### Out of Scope (Future Phases)

- **Trading (buy/sell orders)** — explicitly deferred to Phase 2 or later; this is read-only integration only
- Custom strategy creation — template-based only in MVP; custom creation deferred to Phase 2
- Strategy backtesting or simulation — deferred to Phase 2
- Order history and execution status — deferred (assumes read-only, no trading in Phase 1)
- Historical P&L charting — defer; keep current/unrealized only in MVP
- Sector/asset-class breakdown on dashboard — defer; show flat holdings list only
- Multi-user/multi-account (single user, single IOL account per app instance)
- Advanced charting (keep existing TradingView or similar integrations)
- Dividends and corporate actions tracking
- Tax reporting or statement export
- Machine-learning-based strategy recommendations
- Real-time notifications or alerts for price/order events
- API public endpoints (backend REST API remains internal)
- Dark mode or theme customization
- Mobile app (desktop only, responsive web)

---

## Approach

### Architectural Decisions

| Decision | Rationale |
|----------|-----------|
| **IOL Credentials**: Encrypted env vars in backend; no frontend exposure | 15-min token TTL is backend-only responsibility; frontend never holds IOL secrets |
| **Token Refresh**: Proactive background job (± 2 min before expiry) | Async job is safer than request-level interception; reduces token expiry edge cases |
| **Portfolio Sync**: Read-only from IOL; no manual entry UI | Dual-source sync creates conflicts; IOL is authoritative; single source of truth |
| **Trading**: Explicitly deferred to Phase 2 | User prioritizes read-only integration and UX polish; real-money trading requires more safety work |
| **Price Provider Selection**: Factory pattern extended with currency routing | Route ARS requests to IOL BCBA quotes, USD to yfinance; clean separation of concerns |
| **Strategy Storage**: Simple JSON/text template in DB; no backtesting or custom creation in MVP | Templates are human-readable rules; custom creation and backtesting deferred to Phase 2 |
| **Dashboard Metrics**: Total invested, current value, unrealized P&L, realized P&L (if sold) | Focus on core portfolio health metrics; sector breakdown and historical charting deferred |

### Delivery Strategy: Auto-Chain, 5 PRs

**Chain Approach**: stacked-to-main (each PR merges to main in order; dependencies are sequential)

**Estimated Changed Lines Per PR**:
1. UX Auth Gate + Dashboard Layout: 200–300 (Next.js layout, components, Tailwind, onboarding flow)
2. IOL OAuth2 Client + Token Manager: 200–300 (FastAPI service, credential store, proactive token refresh job)
3. Portfolio Sync + Account Status: 200–250 (new portfolio endpoint, sync logic, account status endpoint, schema update)
4. Currency-Aware Pricing (ARS/USD): 150–200 (price factory refactor, IOL BCBA quotes vs. yfinance routing)
5. Dashboard + Base Strategy Templates: 200–350 (strategy endpoints, template seeding, dashboard queries, metrics calculation)

**Total Estimated Changed Lines**: 950–1,400 lines (6–9 commits, 10–15 weeks at typical velocity)

---

## Assumptions

1. **Single User**: App serves one user and one IOL account (no multi-tenancy beyond existing auth).
2. **IOL Account Ready**: User has an active IOL account with API access enabled and OAuth2 credentials available.
3. **Read-Only Portfolio**: User accepts that IOL is source of truth; manual portfolio edits are deprecated entirely in favor of auto-sync. No manual entry UI in MVP.
4. **No Trading in Phase 1**: User explicitly defers buy/sell functionality to Phase 2 or later. This integration is read-only: fetch holdings, account status, and quotes only.
5. **Acceptable Token TTL**: 15-min token refresh window is acceptable. Backend handles proactive refresh; frontend never holds IOL tokens.
6. **Price Feed Limitations**: yfinance is acceptable for USD; IOL BCBA quotes are acceptable for ARS CEDEARs (may differ from other sources).
7. **UI Redesign Scope**: "Beautiful UI" means modern Tailwind components, accessible forms, and intuitive workflows (no custom design system or external component library required).
8. **Strategy Templates**: Base strategies are descriptive templates only; no backtesting, no custom creation in MVP. Both deferred to Phase 2.
9. **Onboarding Friction**: User accepts entering IOL credentials on first login (no demo mode or deferred setup).

---

## Proposal Question Round — User Answers

**Status**: All questions answered by user (authoritative feedback received).

### Q1: Portfolio and Manual Editing
**User Answer**: **Option A** — Remove manual entry completely. Only import from IOL, no manual edits.
**Decision**: Manual portfolio entry UI is deprecated entirely. IOL is the only source of truth.

### Q2: Trading Safety and Defaults
**User Answer**: **Option B** applies, but **trading is now OUT OF SCOPE** for Phase 1. User explicitly defers buy/sell to Phase 2 or later.
**Decision**: Phase 1 is read-only. No trading UI, no order endpoints, no safety gates. This changes the scope significantly and reduces risk surface.

### Q3: Currency and Price Feeds
**User Answer**: **Option B** (fallback strategy). Try IOL BCBA quotes first for ARS; fall back to yfinance if unavailable.
**Decision**: Implement factory pattern with IOL-first routing for ARS CEDEARs; yfinance as fallback. For USD holdings, use yfinance directly.

### Q4: Dashboard Metrics and P&L Calculation
**User Answer**: Priority metrics are:
- Total Invested (cost basis)
- Current Portfolio Value (sum of current prices)
- Unrealized P&L (current - invested)
- Realized P&L (if user has sold any holdings)

**Decision**: Dashboard shows these 4 core metrics. % return can be derived. Sector/asset-class breakdown deferred to Phase 2.

### Q5: Base Strategies and Customization
**User Answer**: **Option C** intent, but reconciled with scope deferral: MVP ships validated base strategy templates only (3–5 templates with description, how it works, recommended timeframe). Custom strategy creation and backtesting deferred to Phase 2.
**Decision**: Strategy section in MVP is template-based, read-only, no backtesting.

### Q6: Auth and Onboarding Flow
**User Answer**: **Option B** — Dashboard first, IOL setup optional. But user clarified they accept entering IOL credentials on first login (no demo mode).
**Decision**: After login, prompt for IOL credentials immediately; successful connection unlocks dashboard. IOL setup is required, not deferred.

### Q7: Scope Boundary — What Can Wait?
**User Answer**: Defer these to Phase 2:
- (a) Sector/asset-class breakdown on dashboard — show flat list only in MVP
- (b) Custom strategy creation — templates only in MVP
- (c) Realized P&L tracking — include only if user has sold holdings per IOL data; defer if not applicable

**Decision**: All three deferred items are now explicitly out of scope for Phase 1. Realize P&L calculation included only if IOL data shows sells.

---

## Risks and Unknowns

| Risk | Severity | Impact | Mitigation |
|------|----------|--------|-----------|
| IOL API unavailability or token expiry | HIGH | App cannot fetch prices or account data | Proactive token refresh, fallback to cached prices, clear error messages |
| Portfolio sync conflicts or stale data | MED | User sees outdated holdings or account balance | Read-only from IOL, periodic sync (every 5–10 min), clear UI refresh timestamp |
| Credential storage security | HIGH | IOL account compromise | Encrypt at rest, rotate secrets regularly, audit access logs, never log credentials |
| Price feed reliability for ARS CEDEARs | MED | Incorrect portfolio valuation or P&L | Use IOL BCBA quotes as primary; fall back to yfinance; add price source indicator in UI |
| Tight 15-min token TTL | MED | Token refresh fails, user locked out mid-session | Proactive refresh with monitoring (run job every 13 min); clear error UI and recovery steps |
| Onboarding friction (credential entry) | LOW | User abandons setup if entry is confusing | Clear onboarding flow, IOL credential validation before save, helpful error messages |

---

## Next Recommended Phase

**sdd-spec** and **sdd-design** can run in parallel after proposal approval.

- **sdd-spec**: Detail the API contracts, DB schema, and user workflows (what the app does)
- **sdd-design**: Architect the service layer, token refresh job, portfolio sync mechanism, and trading safety gates (how the app does it)

---

## Notes for Reviewers

- This proposal **explicitly removes trading from Phase 1 MVP**. The integration is read-only: fetch holdings, account status, and quotes only. Buying and selling is deferred to Phase 2 or later.
- This scope change **reduces estimated effort from 380–550 hours to 280–400 hours** and the PR chain from 6 PRs to 5 PRs.
- This proposal assumes **single-user ownership** of the app (the user and their IOL account). Multi-user/multi-tenant support is explicitly out of scope.
- **Currency complexity** is unavoidable: ARS CEDEARs and USD ADRs require different price feeds. We've chosen a fallback strategy (IOL-first for ARS, yfinance as fallback).
- **5-PR delivery** is sequential (stacked-to-main). Each PR is autonomous and can be reviewed/merged independently. Early PRs (UX, IOL client, portfolio) are lower risk; later PRs (pricing, dashboard) are integration-heavy.
- **All 7 product questions have been answered by the user**. Proposal assumptions are now finalized and ready for spec and design phases.

---

## Final Proposal Status

**Status**: Finalized with user feedback incorporated. All critical decisions and assumptions are locked.

**Next Action**: Proceed to **sdd-spec** and **sdd-design** phases (can run in parallel).
