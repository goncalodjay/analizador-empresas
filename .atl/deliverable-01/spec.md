# Spec: Foundation (Deliverable 1)

## Intent
Establish the runtime infrastructure and application skeleton for the Stock Market Company Analyzer: Docker dev environment, full database schema, authentication system, and frontend shell.

## Requirements

### R1 — Docker Development Environment
**R1.1** PostgreSQL 15 with pgvector extension running on port 5432.
**R1.2** Redis 7 running on port 6379.
**R1.3** FastAPI backend running on port 8000 with hot-reload.
**R1.4** Next.js 14 frontend running on port 3000 with hot-reload.
**R1.5** One-command startup via `docker compose up`.

### R2 — Database Schema (Alembic)
**R2.1** Initial migration covering all 17 tables: users, portfolio_positions, watchlists, watchlist_tickers, investment_strategies, fundamental_snapshots, technical_signals, analyst_ratings, insider_transactions, earnings_history, dividend_history, health_scores, generated_signals, news_items, daily_digests, model_versions, backtest_results.
**R2.2** All tables have proper indexes, foreign keys with CASCADE deletes, and unique constraints.
**R2.3** pgvector extension enabled for news embeddings (Deliverable 8).

### R3 — Authentication (JWT + bcrypt)
**R3.1** User registration with email + password (min 8 chars).
**R3.2** User login returning HTTPOnly JWT cookie.
**R3.3** Logout clearing the cookie.
**R3.4** GET /auth/me returning the authenticated user profile.
**R3.5** Duplicate email rejection (409 Conflict).
**R3.6** Invalid credentials rejection (401 Unauthorized).

### R4 — Frontend Shell
**R4.1** Root layout with persistent sidebar and top bar.
**R4.2** Login and register pages in auth route group.
**R4.3** Dashboard placeholder page.
**R4.4** Auth context (AuthProvider) managing JWT user state.
**R4.5** Middleware protecting authenticated routes, redirecting to /login.
**R4.6** API client with typed fetch wrapper (credentials: include).
**R4.7** DataFreshnessTag component available for all panels.

## Scenarios

### S1: Register
```
GIVEN a new user
WHEN they POST /auth/register with valid email and password
THEN 201 returned with user profile
```

### S2: Duplicate email
```
GIVEN user already registered
WHEN they POST /auth/register with same email
THEN 409 Conflict returned
```

### S3: Login
```
GIVEN a registered user
WHEN they POST /auth/login with correct credentials
THEN 200 returned with Set-Cookie header containing HttpOnly JWT
```

### S4: Login invalid
```
GIVEN a registered user
WHEN they POST /auth/login with wrong password
THEN 401 Unauthorized returned
```

### S5: Me
```
GIVEN a valid access_token cookie
WHEN they GET /auth/me
THEN 200 returned with user profile
```

### S6: Unauthenticated access
```
GIVEN no cookie
WHEN they access /dashboard, /portfolio, or any protected route
THEN redirected to /login
```

### S7: Logout
```
GIVEN a valid access_token cookie
WHEN they POST /auth/logout
THEN 204 returned, cookie cleared
```
