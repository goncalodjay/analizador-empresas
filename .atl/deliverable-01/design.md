# Design: Foundation (Deliverable 1)

## Technical Approach

Deliverable 1 establishes the entire runtime infrastructure and application skeleton. We bootstrap a Docker-based local development environment with PostgreSQL 15 (pgvector), Redis 7, FastAPI backend, and Next.js 14 frontend. The backend ships with a fully migrated database schema (all 17 tables), JWT+bcrypt authentication, and Pydantic v2 request/response contracts. The frontend delivers a typed Next.js App Router application with route-group authentication pages, a persistent sidebar layout, and a DataFreshnessTag component.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Docker Host                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  PostgreSQL │  │    Redis    │  │    Next.js 14       │ │
│  │  15 +       │  │    Cache /  │  │    (App Router)     │ │
│  │  pgvector   │  │    Sessions │  │    Port 3000        │ │
│  │  Port 5432  │  │    Port 6379│  │                     │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         │                  │                    │            │
│         └──────────────────┴────────────────────┘            │
│                            │                               │
│                     ┌──────┴──────┐                         │
│                     │  FastAPI    │                         │
│                     │  (Uvicorn)  │                         │
│                     │  Port 8000  │                         │
│                     └──────┬──────┘                         │
│                            │                               │
│         ┌──────────────────┼──────────────────┐           │
│         ▼                  ▼                  ▼           │
│    ┌─────────┐       ┌──────────┐       ┌──────────┐     │
│    │ Alembic │       │  JWT     │       │Providers │     │
│    │Migrations│      │Middleware│       │(abstract)│     │
│    └─────────┘       └──────────┘       └──────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Technology Choices

| Technology | Role | Rationale |
|------------|------|-----------|
| FastAPI + Python 3.11 | Backend framework | Native async, OpenAPI docs, Pydantic v2 |
| SQLAlchemy 2.0 (async) + Alembic | ORM / Migrations | Declarative 2.0, async sessions, incremental migration |
| PostgreSQL 15 + pgvector | Primary database | ACID, JSONB, pgvector for embeddings |
| Redis 7 | Cache / Sessions | TTL caching, rate limiting |
| python-jose + bcrypt | Auth | HS256 JWT, slow hashing, HttpOnly cookies |
| Next.js 14 App Router + TypeScript | Frontend | Server Components, parallel routing, Tailwind |
| Pydantic v2 | Validation | Settings, request/response schemas, strict types |
| Docker + docker-compose | Local dev | One-command spin-up, reproducible |

## Backend API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | No | Health check (DB + Redis) |
| POST | `/auth/register` | No | Create user (201) |
| POST | `/auth/login` | No | Login, set cookie (200) |
| POST | `/auth/logout` | Yes | Clear cookie (204) |
| GET | `/auth/me` | Yes | Current user (200) |

## Frontend Routes

| Route | Type | Component | Auth |
|-------|------|-----------|------|
| `/login` | Public | LoginForm | No |
| `/register` | Public | RegisterForm | No |
| `/dashboard` | Protected | Placeholder | Yes |

## Database Models (17 tables)

1. `users` — auth user with preferences
2. `portfolio_positions` — stock holdings
3. `watchlists` — named watchlist groups
4. `watchlist_tickers` — tickers in watchlists
5. `investment_strategies` — strategy profiles
6. `fundamental_snapshots` — cached fundamental data
7. `technical_signals` — computed indicators
8. `analyst_ratings` — analyst consensus
9. `insider_transactions` — insider activity
10. `earnings_history` — quarterly earnings
11. `dividend_history` — dividend payments
12. `health_scores` — composite company scores
13. `generated_signals` — AI-generated signals
14. `news_items` — fetched news articles
15. `daily_digests` — morning digest records
16. `model_versions` — fine-tuned model tracking
17. `backtest_results` — strategy backtest data

## Review Workload Forecast

| Layer | Files | Est. Lines |
|-------|-------|-----------|
| Docker + configs | 4 | ~180 |
| Backend core | 4 | ~160 |
| Backend models | 10 | ~550 |
| Backend API + schemas + services | 6 | ~280 |
| Backend Alembic | 3 | ~320 |
| Backend tests | 3 | ~200 |
| Frontend configs | 4 | ~60 |
| Frontend pages + components | 8 | ~350 |
| Frontend lib | 3 | ~130 |
| **Total** | **~45 files** | **~2,230 lines** |

> Risk: HIGH — requires chained PRs for reviewable slices.
