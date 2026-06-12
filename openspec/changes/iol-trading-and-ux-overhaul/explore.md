# Exploration: IOL Trading and UX Overhaul

## Overview

Comprehensive SDD exploration for IOL API integration (real-money trading), beautiful UX redesign, auth gate, dashboard with metrics, currency-aware pricing, and base strategies.

## Current Stack and Findings

### Frontend
- **Framework**: Next.js 14.2.4 + React 18 + Tailwind CSS
- **Authentication**: Cookie-based JWT (30-min TTL, email/password)
- **UI State**: No component library; navigation/sidebar always visible (no auth gate)
- **Pages**: login, register, dashboard (stub), portfolio, strategy, watchlists, analysis ([ticker])

### Backend
- **Framework**: FastAPI 0.111 + SQLAlchemy async
- **Database**: PostgreSQL + pgvector
- **Cache**: Redis
- **Authentication**: Cookie JWT with bcrypt
- **Services**: ingestion, portfolio, news, price history, strategy
- **Portfolio**: Currently manual (ticker + shares + avg_buy_price)
- **Pricing**: yfinance provider with factory abstraction, Redis caching, DB persistence

### IOL API v2
- **Endpoint**: api.invertironline.com
- **Auth**: OAuth2 Resource Owner Password Credentials flow
  - POST /token → bearer token (15-min TTL) + refresh token
  - Tight TTL requires backend-only proactive refresh
- **Key Endpoints**:
  - GET /estadocuenta (account statement)
  - GET /portafolio (holdings: ticker, quantity, buy price, currency ARS/USD)
  - GET /cotizaciones (price quotes)
  - POST /operar/comprar (buy order)
  - POST /operar/vender (sell order)
- **No Sandbox**: Only live trading (real money, irreversible)

## Key Risks and Constraints

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Real-money trading safety | HIGH | Strict confirmation gates; trading off by default; require user opt-in |
| 15-min token TTL | HIGH | Backend-only proactive refresh; never expose tokens to frontend |
| Multi-currency pricing | HIGH | yfinance unreliable for ARS CEDEARs; use IOL quotes endpoint as ARS price source |
| Portfolio sync conflicts | MED | Read-only from IOL; recommend IOL as source of truth, not manual edits |
| No test sandbox | MED | Test with small-balance real IOL account |
| Auth gate refactor | LOW | Straightforward Next.js layout modification |

## Suggested Delivery Strategy

- **Model**: Auto-chain, 6 independent PRs with clear dependency order
- **Chain Strategy**: stacked-to-main (each PR merges to main in sequence)
- **Estimated Effort**: 380–550 hours (14–20 weeks)

### PR Sequence
1. UX foundation + auth gate layout
2. IOL OAuth2 client + backend token management
3. Portfolio sync from IOL API
4. Currency-aware pricing (ARS/USD split)
5. Trading UI + order placement
6. Dashboard + base strategies

## Architectural Decisions (Pending Proposal)

- IOL credential storage: encrypted env vars or secure backend vault?
- Token refresh: proactive bg job or on-demand request interception?
- Portfolio read-only enforcement: API-level or advisory UI hints?
- Currency-aware price selection: factory pattern extension or dedicated service?
- Trading safety gates: modal confirmation, transaction receipt, rollback strategy?

## Next Phase

Proposal phase will define intent, scope, architectural decisions, assumptions, and propose concrete product questions for user feedback.
