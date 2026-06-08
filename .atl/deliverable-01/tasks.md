# Tasks: Foundation (Deliverable 1)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~2,230 |
| 400-line budget risk | HIGH |
| Chained PRs required | Yes |
| Delivery strategy | PR 1 (Infra+DB) → PR 2 (Backend Auth) → PR 3 (Frontend) |

---

## PR 1: Infrastructure & Database

### Task 1.1 — Docker environment
**Files:** `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`, `.env.example`
- PostgreSQL 15 + pgvector, Redis 7, FastAPI backend, Next.js frontend
- Health checks, volume persistence, hot-reload
- **Status:** ✅ Complete (PR 1, 2 commits)

### Task 1.2 — Backend configuration
**Files:** `backend/requirements.txt`, `backend/app/core/config.py`
- Pydantic-settings with DATABASE_URL, REDIS_URL, SECRET_KEY
- JWT settings (ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES)
- **Status:** ✅ Complete

### Task 1.3 — Database core
**Files:** `backend/app/core/database.py`, `backend/app/core/redis.py`
- Async SQLAlchemy engine + sessionmaker
- Redis client singleton
- **Status:** ✅ Complete

### Task 1.4 — All 17 SQLAlchemy models
**Files:** `backend/app/models/*.py` (10 files)
- User, PortfolioPosition, Watchlist, WatchlistTicker, InvestmentStrategy
- FundamentalSnapshot, TechnicalSignal, AnalystRating, InsiderTransaction
- EarningsHistory, DividendHistory, HealthScore
- GeneratedSignal, NewsItem, DailyDigest, ModelVersion, BacktestResult
- Mapped/mapped_column 2.0 style, relationships, indexes
- **Status:** ✅ Complete (1 commit)

### Task 1.5 — FastAPI app factory
**Files:** `backend/app/main.py`, `backend/app/api/health.py`
- Lifespan events, health check (DB + Redis ping)
- **Status:** ✅ Complete (1 commit)

### Task 1.6 — Alembic initial migration
**Files:** `backend/alembic/env.py`, `backend/alembic/versions/0001_initial_schema.py`
- All 17 tables + indexes + pgvector ivfflat
- **Status:** ✅ Complete (1 commit)

---

## PR 2: Backend Authentication

### Task 2.1 — Auth schemas
**Files:** `backend/app/schemas/auth.py`
- UserCreate, UserLogin, UserOut with Pydantic v2
- UUID serializer, EmailStr validation
- **Status:** ✅ Complete (1 commit)

### Task 2.2 — Security core
**Files:** `backend/app/core/security.py`
- JWT encode/decode with python-jose
- bcrypt password hashing (direct, not passlib)
- **Status:** ✅ Complete (PR 1 had initial version, PR 2 refined)

### Task 2.3 — API dependencies
**Files:** `backend/app/api/deps.py`
- get_current_user: extract JWT from HttpOnly cookie, lookup user
- **Status:** ✅ Complete (1 commit)

### Task 2.4 — User service
**Files:** `backend/app/services/user_service.py`
- create_user (hash password), get_user_by_email, get_user_by_id
- **Status:** ✅ Complete (1 commit)

### Task 2.5 — Auth endpoints
**Files:** `backend/app/api/auth.py`
- POST /auth/register, POST /auth/login, POST /auth/logout, GET /auth/me
- HttpOnly cookie management
- **Status:** ✅ Complete (1 commit)

### Task 2.6 — Auth tests
**Files:** `backend/tests/conftest.py`, `backend/tests/test_auth.py`
- SQLite async fixtures, 13 integration tests
- Register, login, logout, me, validation, auth enforcement
- **Status:** ✅ Complete (1 commit)

---

## PR 3: Frontend Shell

### Task 3.1 — Root layout + globals
**Files:** `frontend/src/app/layout.tsx`, `frontend/src/app/globals.css`
- AuthProvider wrapping, Sidebar + TopBar layout
- Tailwind directives
- **Status:** ✅ Complete (1 commit)

### Task 3.2 — Auth pages
**Files:** `frontend/src/app/(auth)/login/page.tsx`, `frontend/src/app/(auth)/register/page.tsx`
- Route-group auth pages
- **Status:** ✅ Complete (1 commit)

### Task 3.3 — Dashboard placeholder
**Files:** `frontend/src/app/dashboard/page.tsx`
- **Status:** ✅ Complete (1 commit)

### Task 3.4 — Layout components
**Files:** `frontend/src/components/layout/Sidebar.tsx`, `TopBar.tsx`, `DataFreshnessTag.tsx`
- Collapsible sidebar, top bar with user info, data freshness badge
- **Status:** ✅ Complete (1 commit)

### Task 3.5 — Auth form components
**Files:** `frontend/src/components/auth/LoginForm.tsx`, `RegisterForm.tsx`
- Client-side validation, API integration
- **Status:** ✅ Complete (1 commit)

### Task 3.6 — API client + types
**Files:** `frontend/src/lib/api.ts`, `frontend/src/lib/types.ts`
- Fetch wrapper with credentials:include, ApiError class
- User DTO interfaces
- **Status:** ✅ Complete (1 commit)

### Task 3.7 — Auth context + middleware
**Files:** `frontend/src/lib/auth-context.tsx`, `frontend/src/middleware.ts`
- AuthProvider with useAuth hook, login/register/logout methods
- Cookie-based route protection, redirect unauthenticated users
- **Status:** ✅ Complete (1 commit)

### Task 3.8 — Build configs
**Files:** `frontend/postcss.config.js`, `frontend/tsconfig.json`, `frontend/next.config.js`
- Tailwind + PostCSS + TypeScript + Next.js config
- **Status:** ✅ Complete (1 commit fix)
