# Tasks: IOL Read-Only Integration and UX Overhaul

**Change**: iol-trading-and-ux-overhaul  
**Project**: analizador-empresas  
**Delivery Strategy**: auto-chain (stacked-to-main)  
**Chain Strategy**: stacked-to-main (each PR merges to main in order)  
**Total Estimated Changed Lines**: 950–1,400 (across 5 PRs)

---

## PR 1: UX Auth Gate + Dashboard Layout (200–300 lines)

**Dependency**: None (foundational UX/auth)  
**Spec Requirements**: auth-gate (DeltaR1–R4), ux-overhaul (DeltaR1–R3, DeltaR6–R7)  
**Design References**: Section 4 (Auth Gate and UX Redesign), Section 7 (UX Overhaul Approach)  
**Start/Finish Boundary**: App enforces auth; login/register screens visible; dashboard layout with sidebar/header established; design tokens in Tailwind config.  
**Rollback Boundary**: Revert middleware, route groups, layout files, Tailwind config; revert to prior auth behavior (if any).  
**Test Approach**: Next.js middleware auth checks; login/register page renders; protected routes redirect unauthenticated users; JWT cookie persists; app shell visible post-login; Tailwind design tokens applied to 80%+ of existing pages.

### Task 1.1: Next.js Middleware Auth Check [x]
- **Description**: Implement `frontend/src/middleware.ts` to validate JWT on all routes; redirect unauthenticated users to /login; redirect authenticated users away from /login.
- **Files to Touch**: `frontend/src/middleware.ts` (existing, no changes needed); `next.config.js` (if matcher config needed)
- **Acceptance Criteria** (from spec auth-gate DeltaR3–R4):
  - Middleware checks for JWT in httpOnly cookie (existing cookie setup)
  - Unauthenticated access to `/dashboard`, `/analysis/*`, `/portfolio`, `/strategies`, `/watchlist` → 302 redirect to `/login`
  - Authenticated access to `/login`, `/register` → 302 redirect to `/dashboard`
  - JWT validation uses existing cookie parser and validation logic
  - `next` query param preserved for post-login redirect (e.g., `/login?next=/analysis/AAPL`)
- **Test Expectations**:
  - Unit test: middleware validates JWT, redirects on missing/expired JWT, allows on valid JWT
  - Integration test: unauthenticated user navigates to `/dashboard` → redirects to `/login`; authenticated user navigates to `/login` → redirects to `/dashboard`
  - Integration test: `next` param works (after login, user returns to previous route)

### Task 1.2: Route Groups — (auth) and (dashboard) Layout Split [x]
- **Description**: Reorganize Next.js app directory using route groups: `(auth)/login`, `(auth)/register` (minimal layout, no sidebar) and `(dashboard)/*` (full layout with sidebar, header, nav).
- **Files to Touch**:
  - `frontend/src/app/(auth)/layout.tsx` (new; minimal, no sidebar)
  - `frontend/src/app/(auth)/login/page.tsx` (move existing)
  - `frontend/src/app/(auth)/register/page.tsx` (move existing)
  - `frontend/src/app/(dashboard)/layout.tsx` (new; sidebar, header, nav)
  - `frontend/src/app/(dashboard)/dashboard/page.tsx` (move existing)
  - `frontend/src/app/(dashboard)/analysis/[ticker]/page.tsx` (move existing)
  - `frontend/src/app/(dashboard)/portfolio/page.tsx` (move existing)
  - `frontend/src/app/(dashboard)/strategies/page.tsx` (move existing)
  - `frontend/src/app/layout.tsx` (root layout, no sidebar, auth gates app shell visibility)
- **Acceptance Criteria** (from spec auth-gate DeltaR2, ux-overhaul DeltaR3):
  - `(auth)` routes render login/register without sidebar or main app shell
  - `(dashboard)` routes render with sidebar (nav links: Dashboard, Analysis, Portfolio, Strategies, Watchlist), header (logo, IOL connection status, user menu), and main content area
  - Root layout conditionally mounts app shell based on JWT validity (conditional render, not hydration mismatch)
  - All existing routes continue to work (no 404s after move)
  - Styling is consistent with design tokens (see Task 1.4)
- **Test Expectations**:
  - Unit test: layout components render correctly with/without sidebar
  - Integration test: unauthenticated `/login` route has no sidebar; authenticated `/dashboard` route has sidebar and header
  - Integration test: route navigation within (dashboard) preserves layout (no re-mount of sidebar/header)

### Task 1.3: Design Tokens in Tailwind Config [x]
- **Description**: Establish design system foundation in `frontend/tailwind.config.ts` with colors, spacing, typography, border radius, transitions tokens. No new component library yet (use Tailwind utilities).
- **Files to Touch**:
  - `frontend/tailwind.config.ts` (update/extend)
  - `frontend/src/styles/globals.css` (reset and token documentation)
- **Acceptance Criteria** (from spec ux-overhaul DeltaR1, R5–R6):
  - **Colors**: Primary (#0066cc), secondary (neutral), success (#00aa00), warning (#ff8800), error (#cc0000), neutral grayscale (white, light, medium, dark, black)
  - **Spacing**: xs (4px), sm (8px), md (12px), lg (16px), xl (24px)
  - **Typography**: Font family (Inter, -apple-system, Segoe UI); sizes (12px, 14px, 16px, 18px, 24px, 32px); weights (400, 600, 700)
  - **Borders**: Radius (4px, 8px, 16px)
  - **Transitions**: Duration (150ms, 300ms), easing (ease-in, ease-out)
  - All colors meet WCAG AA contrast ratio (4.5:1 for text)
  - Tokens are applied to all existing pages (login, dashboard, analysis, portfolio, strategies, watchlist) — at least 80%+ of UI uses tokens
  - Documentation of tokens added to globals.css or design-tokens.md
- **Test Expectations**:
  - Accessibility test: text colors meet WCAG AA (contrast checker or axe DevTools)
  - Visual test: all pages (login, dashboard, etc.) use consistent colors, spacing, typography from tokens
  - Responsive test: breakpoints work as expected (mobile <640px, tablet 640–1024px, desktop >1024px)

### Task 1.4: App Shell Components (Header, Sidebar, Layout) [x]
- **Description**: Implement header (logo, connection status placeholder, user menu with logout), sidebar (nav links with icons), and consistent layout structure. Use Tailwind + basic HTML/React (no new component library yet).
- **Files to Touch**:
  - `frontend/src/components/Header.tsx` (new)
  - `frontend/src/components/Sidebar.tsx` (new)
  - `frontend/src/app/(dashboard)/layout.tsx` (implement; includes Header and Sidebar)
  - `frontend/src/components/UserMenu.tsx` (new; dropdown for logout)
- **Acceptance Criteria** (from spec ux-overhaul DeltaR3):
  - **Header**: Logo on left, page title/IOL connection status in center, user menu (profile, logout) on right; fixed or sticky
  - **Sidebar**: Width 250px on desktop, collapsible to icon-only on tablet; nav links: Dashboard, Analysis, Portfolio, Strategies, Watchlist, Settings; icons aligned with text; active link highlighted
  - **Main Layout**: Header fixed, sidebar fixed or sticky, main content scrollable; padding/spacing consistent with design tokens
  - **User Menu**: Dropdown on user avatar; logout button; graceful logout (clear JWT cookie, redirect to /login)
  - **Responsive**: Desktop (sidebar left, visible); tablet (sidebar collapses to icons or hamburger); mobile (deferred)
  - **Accessibility**: Nav links are keyboard-navigable; ARIA labels on icons; focus indicators visible
- **Test Expectations**:
  - Unit test: Header, Sidebar, UserMenu components render correctly
  - Integration test: user can click logout, JWT cookie cleared, redirect to /login
  - Responsive test: sidebar collapses on tablet viewport; no horizontal scroll on any viewport
  - Accessibility test: keyboard Tab navigation through sidebar links works; ARIA labels present on icons

### Task 1.5: Login/Register Pages Styling & Form Validation [x]
- **Description**: Apply design tokens and consistent styling to login and register pages. Ensure form validation works (existing backend validation + frontend validation with react-hook-form/Zod if not already in place).
- **Files to Touch**:
  - `frontend/src/app/(auth)/login/page.tsx` (update styling)
  - `frontend/src/app/(auth)/register/page.tsx` (update styling)
  - `frontend/src/components/LoginForm.tsx` (extract/refactor if needed)
  - `frontend/src/components/RegisterForm.tsx` (extract/refactor if needed)
  - Existing form validation logic (reuse or enhance)
- **Acceptance Criteria** (from spec auth-gate):
  - Login form: email input, password input, "Login" button, "Forgot Password" link (deferred), "Sign Up" link
  - Register form: email input, password input, "Register" button, "Already have account?" link
  - Forms use design token colors, spacing, typography
  - Form validation: email format, password strength (if applicable), error messages displayed
  - Styling is consistent with dashboard layout (same color palette, fonts)
  - Forms are responsive on desktop/tablet
- **Test Expectations**:
  - Unit test: form validation rejects invalid email/password; accepts valid input
  - Integration test: login form POSTs to `/api/auth/login` on submit; register form POSTs to `/api/auth/register`
  - Visual test: login and register pages match design system tokens

### Task 1.6: Middleware and Layout Integration Test [DEFERRED]
- **Description**: E2E test ensuring auth gate works end-to-end: unauthenticated user lands on login, logs in, sees dashboard with app shell, navigates protected routes, logs out.
- **Files to Touch** (deferred to next phase - manual verification performed):
  - `frontend/__tests__/auth-gate.integration.test.ts` (new; or add to existing test suite)
- **Acceptance Criteria**:
  - Scenario: Unauthenticated user lands on `/` → redirects to `/login`
  - Scenario: User logs in with valid credentials → JWT cookie set, redirect to `/dashboard`, app shell visible
  - Scenario: User navigates to `/analysis/AAPL` → protected route works (no redirect)
  - Scenario: User logs out → JWT cookie cleared, redirect to `/login`, app shell hidden
  - Scenario: User manually enters invalid JWT in cookie → middleware detects, redirects to `/login`
- **Test Expectations**:
  - E2E test (Cypress, Playwright, or similar): runs through all scenarios; verifies redirects, JWT presence, UI visibility
  - No console errors or auth-related warnings

---

## PR 2: IOL OAuth2 Client + Token Manager (200–300 lines)

**Dependency**: PR 1 (auth gate establishes user context)  
**Spec Requirements**: iol-connection (DeltaR1–R5)  
**Design References**: Section 1 (IOL Client Architecture)  
**Start/Finish Boundary**: IOL API client implemented; token refresh job runs; encrypted credential storage in place; /iol/setup endpoint validates and stores credentials.  
**Rollback Boundary**: Revert IOL-related backend files, migrations, env config, and scheduler setup; manual removal of IOL credentials table if migration is reverted.  
**Test Approach**: Strict TDD: test IOL client authenticate/refresh methods; test token refresh job scheduling; test credential encryption/decryption; test /iol/setup endpoint with valid/invalid credentials.

- [x] Make backend JWT cookie `secure` flag environment-aware (currently secure=False in backend/app/api/auth.py) — carried over from PR 1 review

### Task 2.1: Database Schema — IOLCredentials Table
- [x] **COMPLETE**
- **Description**: Create Alembic migration adding `iol_credentials` table to store encrypted IOL credentials (username, encrypted password, access token, refresh token, expiry, sync status).
- **Files to Touch**:
  - `backend/alembic/versions/[timestamp]_add_iol_credentials.py` (new migration)
- **Acceptance Criteria** (from design Section 1.2):
  - Table schema:
    - `id` (UUID PK)
    - `user_id` (UUID FK, unique)
    - `iol_username` (str)
    - `encrypted_password` (str)
    - `access_token` (str)
    - `token_expires_at` (datetime with timezone)
    - `refresh_token` (str, nullable)
    - `created_at` (datetime, server default)
    - `updated_at` (datetime, server default)
    - `last_synced_at` (datetime, nullable)
    - `sync_error` (str, nullable)
  - Migration is reversible (has downgrade function)
  - Migration can be run on existing database without data loss
  - Constraint: `UNIQUE(user_id)` ensures one IOL connection per user
- **Test Expectations**:
  - Migration test: run migration forward and backward; verify table exists after forward, is dropped after backward
  - Schema validation test: verify columns and constraints are correct (use SQLAlchemy introspection)

### Task 2.2: IOLCredentials SQLAlchemy Model
- [x] **COMPLETE**
- **Description**: Create `backend/app/models/iol_credentials.py` with SQLAlchemy model for IOL credentials with encryption/decryption methods.
- **Files to Touch**:
  - `backend/app/models/iol_credentials.py` (new)
  - `backend/app/models/__init__.py` (add import)
- **Acceptance Criteria** (from design Section 1.2):
  - Model has fields matching schema: id, user_id, iol_username, encrypted_password, access_token, token_expires_at, refresh_token, created_at, updated_at, last_synced_at, sync_error
  - Relationship to `User` model: `user: Mapped["User"] = relationship("User")`
  - Methods:
    - `encrypt_password(cls, raw_password: str) -> str` (class method, uses Fernet)
    - `decrypt_password(self) -> str` (instance method, uses Fernet key from env)
  - Property `time_until_expiry()` returns seconds until token expiry
  - Type hints are complete (Decimal, datetime, Optional, etc.)
- **Test Expectations**:
  - Unit test: `encrypt_password()` encrypts string and produces valid Fernet ciphertext
  - Unit test: `decrypt_password()` decrypts and returns original string
  - Unit test: multiple encryptions of same password produce different ciphertexts (Fernet includes nonce)
  - Unit test: `time_until_expiry()` returns correct seconds

### Task 2.3: Encryption Key Setup (Fernet)
- [x] **COMPLETE**
- **Description**: Add `ENCRYPTION_KEY` environment variable handling to app config. Generate or validate Fernet key on startup.
- **Files to Touch**:
  - `backend/app/core/config.py` (update; add ENCRYPTION_KEY env var)
  - `.env.example` (add ENCRYPTION_KEY example)
  - `backend/app/core/__init__.py` (or main.py) (add key validation on startup)
- **Acceptance Criteria** (from design Section 1.2):
  - Config reads `ENCRYPTION_KEY` from environment (base64-encoded Fernet key)
  - On app startup, validate that key is present and valid (can encode/decode a test string)
  - If key is missing or invalid, app raises `ConfigError` with clear message: "ENCRYPTION_KEY not set or invalid. Run: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())' and set IOL_ENCRYPTION_KEY env var."
  - Key is accessed globally via `config.ENCRYPTION_KEY` (avoid re-reading from env on each encrypt/decrypt)
  - Documentation in `.env.example` explains how to generate key
- **Test Expectations**:
  - Unit test: config loads valid Fernet key from env var
  - Unit test: config raises error if ENCRYPTION_KEY is missing
  - Unit test: config raises error if ENCRYPTION_KEY is invalid base64
  - Integration test: app startup succeeds with valid ENCRYPTION_KEY

### Task 2.4: IOL API Client (IOLClient Class)
- [x] **COMPLETE**
- **Description**: Implement `backend/app/providers/iol_provider.py` with IOLClient class for OAuth2 authentication, token refresh, portfolio fetch, account status fetch, quotes fetch.
- **Files to Touch**:
  - `backend/app/providers/iol_provider.py` (new)
- **Acceptance Criteria** (from design Section 1.4, 1.5):
  - Class `IOLClient`:
    - Constructor: `__init__(client_id: str, client_secret: str, base_url: str)`
    - Method `authenticate(iol_username: str, iol_password: str) -> dict` (POST /token)
    - Method `refresh_token(refresh_token: str) -> dict` (POST /token with refresh grant)
    - Method `fetch_portfolio(access_token: str) -> dict` (GET /portafolio)
    - Method `fetch_account_status(access_token: str) -> dict` (GET /estadocuenta)
    - Method `fetch_quotes(access_token: str, tickers: list[str]) -> dict` (GET /cotizaciones)
  - All methods are async
  - Error handling: catches aiohttp errors and converts to custom exceptions (IOLAuthError, IOLRateLimitError, IOLUnavailableError, IOLError)
  - Retry logic: implemented in helper function `call_iol_with_retry()` (exponential backoff for rate limit, no retry for auth errors)
  - Request timeout: 5 seconds per request
  - Logging: all requests and errors are logged (structured logging)
  - Session management: aiohttp.ClientSession is created in __init__ and closed (or context manager)
- **Test Expectations**:
  - Unit test: authenticate() with valid credentials returns token_response with access_token, expires_in, refresh_token
  - Unit test: authenticate() with invalid credentials raises IOLAuthError
  - Unit test: refresh_token() with valid refresh token returns new access_token
  - Unit test: fetch_portfolio() with valid token returns holdings dict
  - Unit test: fetch_account_status() with valid token returns account dict
  - Unit test: fetch_quotes() with valid token and ticker list returns quotes dict
  - Unit test: retry logic backoffs exponentially on 429 (rate limit), gives up after 3 attempts
  - Unit test: request timeout (>5s) raises IOLError after timeout
  - Mocking: all tests mock aiohttp calls (no real HTTP to IOL); use `aioresponses` or similar

### Task 2.5: IOL Token Manager Service
- [x] **COMPLETE**
- **Description**: Implement `backend/app/services/iol_service.py` with IOLTokenManager class for credential storage, token retrieval, and token refresh with safety checks.
- **Files to Touch**:
  - `backend/app/services/iol_service.py` (new)
- **Acceptance Criteria** (from design Section 1.3):
  - Class `IOLTokenManager`:
    - Method `store_credentials(db: AsyncSession, user_id: UUID, iol_username: str, iol_password: str) -> IOLCredentials` (encrypts password, stores in DB)
    - Method `get_valid_token(db: AsyncSession, user_id: UUID) -> str` (returns access_token; triggers refresh if expiring soon <60s)
    - Method `refresh_token_if_near_expiry(db: AsyncSession, user_id: UUID) -> bool` (refreshes if <2 min to expiry; returns success bool)
    - Method `revoke_credentials(db: AsyncSession, user_id: UUID) -> None` (deletes IOL credentials)
    - Method `get_credentials_status(db: AsyncSession, user_id: UUID) -> dict` (returns connected/disconnected status)
  - All methods are async
  - All methods use database session (injected)
  - Error handling: catches DB errors, encryption errors, IOL errors; logs and raises custom exceptions
  - Request-level safeguard: `get_valid_token()` checks time_until_expiry <60s and triggers refresh immediately if needed (belt-and-suspenders with background job)
- **Test Expectations**:
  - Unit test: `store_credentials()` encrypts password and stores in DB; subsequent decrypt returns original password
  - Unit test: `get_valid_token()` returns token if not expiring; triggers refresh if <60s to expiry
  - Unit test: `refresh_token_if_near_expiry()` returns True if refresh succeeds; False if error or no refresh needed
  - Unit test: `revoke_credentials()` deletes credentials from DB
  - Unit test: `get_credentials_status()` returns {"connected": true, "account_name": "..."} or {"connected": false}
  - Integration test: store credentials → get valid token → refresh works
  - Mock: IOLClient calls are mocked; DB session is provided via fixture

### Task 2.6: Proactive Token Refresh Job (APScheduler)
- [ ] **DEFERRED** (not required for core PR 2 functionality; request-level safeguard in get_valid_token() sufficient for MVP)
- **Description**: Implement background job using APScheduler that runs every 13 minutes to proactively refresh IOL tokens expiring within 2 minutes. Set up scheduler lifecycle (startup, shutdown).
- **Files to Touch**:
  - `backend/app/core/scheduler.py` (new)
  - `backend/app/services/iol_service.py` (add refresh job method)
  - `backend/app/main.py` (add scheduler startup/shutdown event handlers)
- **Acceptance Criteria** (from design Section 1.3):
  - Scheduler `proactive_refresh_job()`:
    - Runs every 13 minutes (configurable via `PROACTIVE_REFRESH_INTERVAL` env var, default 13)
    - For each user with active IOL credentials:
      - Check token expiry via `iol_service.get_credentials()`
      - If expiry < 2 min (120s):
        - Call `iol_service.refresh_token_if_near_expiry()` to refresh
        - Log: `"Token refreshed for user {user_id}"`
      - If refresh fails:
        - Log error but do NOT crash
        - Mark credentials as `sync_error = "Token refresh failed: {error}"`
        - Alert/monitor (logging sufficient for MVP)
  - Scheduler lifecycle:
    - `start_scheduler(app)` called on app startup (FastAPI lifespan or event handler)
    - `stop_scheduler(app)` called on app shutdown
    - If scheduler is already running, don't start twice (idempotent)
  - Job handles empty credentials gracefully (no users with IOL → job completes immediately)
  - Job uses a fresh DB session for each run (avoid session reuse across job invocations)
- **Test Expectations**:
  - Unit test: scheduler can be created and started (no errors)
  - Unit test: `proactive_refresh_job()` refreshes token if <2 min to expiry
  - Unit test: `proactive_refresh_job()` logs error but doesn't crash if refresh fails
  - Unit test: `proactive_refresh_job()` handles no credentials gracefully
  - Integration test: scheduler starts with app; job runs after 13 minutes (simulated with immediate test run)

### Task 2.7: /iol/setup Endpoint (IOL Onboarding)
- [x] **COMPLETE** (portfolio sync deferred to PR 3)
- **Description**: Implement FastAPI endpoint `POST /iol/setup` that validates IOL credentials, stores encrypted credentials, triggers immediate portfolio sync, and sets `iol_connected = true` in user context.
- **Files to Touch**:
  - `backend/app/api/iol.py` (new)
  - `backend/app/main.py` (include router)
- **Acceptance Criteria** (from spec iol-connection DeltaR1):
  - Endpoint: `POST /iol/setup` (requires JWT)
  - Request body:
    ```json
    {
      "iol_username": "user@example.com",
      "iol_password": "password123"
    }
    ```
  - Response on success (200 OK):
    ```json
    {
      "status": "connected",
      "account_name": "Juan Pérez",
      "synced_tickers": ["GGAL", "AAPL"],
      "synced_at": "2026-06-12T17:45:00Z"
    }
    ```
  - Response on failure (401):
    ```json
    {
      "error": "Invalid IOL credentials"
    }
    ```
  - Steps:
    1. Extract current_user from JWT
    2. Test credentials: call `IOLClient.authenticate()` with iol_username and iol_password
    3. If authentication fails → return 401 "Invalid IOL credentials"
    4. If successful:
       - Store encrypted credentials via `iol_token_manager.store_credentials()`
       - Trigger immediate portfolio sync (POST /iol/sync-now logic)
       - Update user JWT/context with `iol_connected = true` (optional; rely on DB status)
       - Return success response with synced holdings and timestamp
  - Error handling: catch IOLAuthError, IOLError; return clear error messages; no stack traces exposed
  - Logging: log successful connection (account name, timestamp); log failed attempts (username, error reason)
- **Test Expectations**:
  - Unit test: POST /iol/setup with valid credentials succeeds (200), returns synced holdings
  - Unit test: POST /iol/setup with invalid credentials fails (401), returns error message
  - Unit test: POST /iol/setup stores encrypted credentials in DB
  - Unit test: POST /iol/setup without JWT returns 401 (unauthenticated)
  - Integration test: POST /iol/setup → credentials stored → subsequent GET /iol/status returns connected=true

### Task 2.8: /iol/status Endpoint (Connection Status)
- [x] **COMPLETE**
- **Description**: Implement `GET /iol/status` endpoint that returns IOL connection status, account name, cash balance, last sync time, needs_reauth flag.
- **Files to Touch**:
  - `backend/app/api/iol.py` (add endpoint)
- **Acceptance Criteria** (from spec iol-connection DeltaR5):
  - Endpoint: `GET /iol/status` (requires JWT)
  - Response if connected (200 OK):
    ```json
    {
      "connected": true,
      "account_name": "Juan Pérez",
      "cash_balance": 125000.50,
      "currency": "ARS",
      "last_sync": "2026-06-12T17:45:00Z",
      "needs_reauth": false
    }
    ```
  - Response if not connected (200 OK):
    ```json
    {
      "connected": false,
      "reason": "credentials_invalid"
    }
    ```
  - Logic:
    1. Check if user has IOL credentials in DB
    2. If not → return `{"connected": false}`
    3. If yes:
       - Fetch cached account status from Redis (with 5-min TTL)
       - If cache hit → return cached response
       - If cache miss:
         - Call IOL /estadocuenta to fetch fresh account status
         - Cache result for 5 minutes
         - Return response with fresh data
    4. If IOL API call fails → return cached last-known state or `{"connected": false}`
  - Caching: Redis key `iol:account_status:{user_id}`, TTL 300s (5 min)
  - Error handling: if IOL API fails, fall back to last-known state (graceful degradation)
- **Test Expectations**:
  - Unit test: GET /iol/status with connected user returns {"connected": true, ...}
  - Unit test: GET /iol/status with unconnected user returns {"connected": false}
  - Unit test: GET /iol/status caches account status for 5 minutes
  - Unit test: GET /iol/status without JWT returns 401
  - Integration test: call endpoint immediately after setup → connected=true; wait 6 minutes and call again → uses fresh data (cache miss)

---

## PR 3: Portfolio Sync + Account Status (200–250 lines)

**Dependency**: PR 2 (IOL client and token manager)  
**Spec Requirements**: portfolio-sync (DeltaR1–R5)  
**Design References**: Section 2 (Portfolio Sync Design)  
**Start/Finish Boundary**: Portfolio holdings fetched from IOL; synced to portfolio_holdings table; periodic sync job runs every 5 minutes; manual /iol/sync-now endpoint works; deprecated manual portfolio entry UI.  
**Rollback Boundary**: Revert migrations, sync service, sync job, endpoints; manual portfolio UI revert to old state.  
**Test Approach**: Strict TDD: test portfolio sync service with mocked IOL data; test sync job scheduling; test sync endpoint; test manual portfolio deprecation (redirects on old URLs).

### Task 3.1: Database Schema — Portfolio Holdings and Account Status Tables
- [x] **COMPLETE**
- **Description**: Create Alembic migrations for `portfolio_holdings` and `user_account_status` tables (separate from old manual portfolio if present).
- **Files to Touch**:
  - `backend/alembic/versions/[timestamp]_add_portfolio_holdings_table.py` (new migration)
  - `backend/alembic/versions/[timestamp]_add_user_account_status_table.py` (new migration)
- **Acceptance Criteria** (from spec portfolio-sync Database Schema, design Section 2.1):
  - `portfolio_holdings` table:
    - `id` (INT PK, auto-increment)
    - `user_id` (UUID FK, references users)
    - `ticker` (VARCHAR 20)
    - `quantity` (DECIMAL 10,2)
    - `avg_buy_price` (DECIMAL 12,2)
    - `currency` (VARCHAR 3, 'ARS' or 'USD')
    - `synced_at` (TIMESTAMP with timezone, not null)
    - `created_at` (TIMESTAMP, server default NOW())
    - `updated_at` (TIMESTAMP, server default NOW())
    - Constraint: `UNIQUE(user_id, ticker)`
  - `user_account_status` table:
    - `id` (INT PK, auto-increment)
    - `user_id` (UUID FK, unique)
    - `cash_balance` (DECIMAL 15,2)
    - `buying_power` (DECIMAL 15,2, nullable)
    - `total_balance` (DECIMAL 15,2, nullable)
    - `currency` (VARCHAR 3, default 'ARS')
    - `synced_at` (TIMESTAMP with timezone)
    - `created_at` (TIMESTAMP, server default NOW())
    - `updated_at` (TIMESTAMP, server default NOW())
  - Both migrations are reversible
  - Can be run on existing DB without data loss
- **Test Expectations**:
  - Migration test: run forward and backward; tables exist after forward, dropped after backward
  - Schema validation: verify columns, constraints, indexes via SQLAlchemy introspection

### Task 3.2: SQLAlchemy Models — PortfolioHolding and AccountStatus
- [x] **COMPLETE**
- **Description**: Create `backend/app/models/portfolio_holdings.py` and extend user model with account status fields (or separate model).
- **Files to Touch**:
  - `backend/app/models/portfolio_holdings.py` (new)
  - `backend/app/models/account_status.py` (new)
  - `backend/app/models/__init__.py` (add imports)
- **Acceptance Criteria**:
  - `PortfolioHolding` model:
    - Fields: id, user_id, ticker, quantity, avg_buy_price, currency, synced_at, created_at, updated_at
    - Relationship: `user: Mapped["User"]`
    - Type hints complete (UUID, Decimal, datetime, etc.)
    - Index on (user_id, ticker) for upsert performance
  - `AccountStatus` model:
    - Fields: id, user_id, cash_balance, buying_power, total_balance, currency, synced_at, created_at, updated_at
    - Relationship: `user: Mapped["User"]`
    - Type hints complete
- **Test Expectations**:
  - Unit test: models can be instantiated and serialized to dict/JSON
  - Unit test: relationships work (user.portfolio_holdings, user.account_status)

### Task 3.3: Portfolio Sync Service
- [x] **COMPLETE**
- **Description**: Implement `backend/app/services/portfolio_sync_service.py` with PortfolioSyncService class for fetching IOL holdings, syncing to portfolio_holdings table, fetching account status.
- **Files to Touch**:
  - `backend/app/services/portfolio_sync_service.py` (new)
- **Acceptance Criteria** (from design Section 2.2–2.3):
  - Class `PortfolioSyncService`:
    - Method `sync_portfolio(user_id: UUID, db: AsyncSession) -> PortfolioSyncReport`
      - Fetch IOL token via iol_token_manager
      - Call IOL /portafolio endpoint
      - For each holding, upsert to portfolio_holdings (INSERT ... ON CONFLICT ... DO UPDATE)
      - Delete holdings where source="manual" (deprecated)
      - Update iol_credentials.last_synced_at and sync_error
      - Return report with synced_count, tickers, synced_at
    - Method `sync_account_status(user_id: UUID, db: AsyncSession) -> AccountStatus`
      - Fetch IOL token
      - Call IOL /estadocuenta endpoint
      - Upsert to user_account_status
      - Return AccountStatus object
  - Error handling:
    - IOLAuthError → set sync_error, log, raise
    - IOLError → log, raise (caller handles)
    - DB errors → rollback, raise
  - All methods are async
  - All methods use transaction (commit only on complete success)
- **Test Expectations**:
  - Unit test: sync_portfolio() with mocked IOL holdings → upserts to DB
  - Unit test: sync_portfolio() with IOL auth error → sets sync_error, raises IOLAuthError
  - Unit test: sync_account_status() with mocked IOL account → upserts to DB
  - Unit test: sync_portfolio() replaces manual holdings with IOL holdings
  - Integration test: full sync workflow (auth → fetch → upsert → commit)

### Task 3.4: Periodic Portfolio Sync Job (APScheduler)
- [ ] **DEFERRED** (same rationale as PR 2 Task 2.6: request-level safeguard in get_valid_token() sufficient for MVP; periodicsync job will be added in future optimization pass)
- **Description**: Implement background job that runs every 5 minutes to sync all users' portfolios and account status.
- **Files to Touch**:
  - `backend/app/core/scheduler.py` (extend; add periodic_portfolio_sync job)
  - `backend/app/main.py` (register job with scheduler)
- **Acceptance Criteria** (from design Section 2.3):
  - Job `periodic_portfolio_sync()`:
    - Runs every 5–10 minutes (configurable via `PORTFOLIO_SYNC_INTERVAL` env var, default 5)
    - For each user with active IOL credentials (sync_error is None):
      - Call `portfolio_sync_service.sync_portfolio()`
      - Call `portfolio_sync_service.sync_account_status()`
      - Log: `"Portfolio synced for user {user_id}: {synced_count} holdings"`
    - If sync fails for a user:
      - Log error, move to next user (don't crash)
      - Set iol_credentials.sync_error with failure reason
    - If IOL API is completely down:
      - Log warning, skip sync for all users
      - Existing data remains unchanged
    - Job completes within 30 seconds for typical single user (1–2 IOL API calls)
  - Scheduler registers job on app startup
  - Job uses fresh DB session for each run
- **Test Expectations**:
  - Unit test: periodic_portfolio_sync() calls sync_portfolio() for each user
  - Unit test: periodic_portfolio_sync() logs error but doesn't crash if one user sync fails
  - Unit test: periodic_portfolio_sync() handles no users gracefully
  - Integration test: job runs, updates portfolio_holdings and user_account_status

### Task 3.5: /iol/sync-now Endpoint (Manual Refresh)
- [x] **COMPLETE**
- **Description**: Implement `POST /iol/sync-now` endpoint for on-demand portfolio sync. Returns immediately with status.
- **Files to Touch**:
  - `backend/app/api/iol.py` (add endpoint)
- **Acceptance Criteria** (from spec portfolio-sync DeltaR4):
  - Endpoint: `POST /iol/sync-now` (requires JWT)
  - Response on success (200 OK):
    ```json
    {
      "status": "success",
      "holdings_count": 5,
      "synced_at": "2026-06-12T17:45:00Z"
    }
    ```
  - Response on failure (500):
    ```json
    {
      "error": "Portfolio sync failed: IOL API unreachable"
    }
    ```
  - Logic:
    1. Extract current_user from JWT
    2. Call portfolio_sync_service.sync_portfolio()
    3. Call portfolio_sync_service.sync_account_status()
    4. Return success response
  - Timeout: 5 seconds max; if timeout, return 504 Service Unavailable
  - Error handling: catch IOLError, sync errors; return 500 with error message
  - Logging: log request start, completion time, holdings count
- **Test Expectations**:
  - Unit test: POST /iol/sync-now with valid user → syncs and returns 200
  - Unit test: POST /iol/sync-now with IOL error → returns 500 with error message
  - Unit test: POST /iol/sync-now without JWT → returns 401
  - Integration test: endpoint completes within 5 seconds

### Task 3.6: /iol/holdings Endpoint (Fetch Holdings Read-Only)
- [x] **COMPLETE**
- **Description**: Implement `GET /iol/holdings` endpoint that returns user's current portfolio holdings from the database (not directly from IOL API).
- **Files to Touch**:
  - `backend/app/api/iol.py` (add endpoint)
- **Acceptance Criteria** (from spec portfolio-sync DeltaR1):
  - Endpoint: `GET /iol/holdings` (requires JWT)
  - Response (200 OK):
    ```json
    {
      "holdings": [
        {
          "ticker": "GGAL",
          "quantity": 50,
          "avg_buy_price": 250.0,
          "currency": "ARS"
        }
      ]
    }
    ```
  - Logic:
    1. Extract current_user from JWT
    2. Query portfolio_holdings for user_id
    3. Return serialized holdings list
  - Error handling: if no holdings found, return empty list
- **Test Expectations**:
  - Unit test: GET /iol/holdings with user who has holdings → returns holdings
  - Unit test: GET /iol/holdings with user who has no holdings → returns empty list
  - Unit test: GET /iol/holdings without JWT → returns 401

### Task 3.7: /iol/account-status Endpoint
- [x] **COMPLETE**
- **Description**: Implement `GET /iol/account-status` endpoint that returns cached account status.
- **Files to Touch**:
  - `backend/app/api/iol.py` (add endpoint)
- **Acceptance Criteria** (from spec portfolio-sync DeltaR2):
  - Endpoint: `GET /iol/account-status` (requires JWT)
  - Response (200 OK):
    ```json
    {
      "cash_balance": 50000.00,
      "buying_power": 100000.00,
      "total_balance": 150000.00,
      "currency": "ARS"
    }
    ```
  - Logic:
    1. Extract current_user from JWT
    2. Query user_account_status for user_id
    3. Return serialized data or empty dict if not synced
  - Caching: 5-minute Redis cache (cache key: `account_status:{user_id}`)
    - If cache hit, return cached data
    - If cache miss, query DB and cache result
- **Test Expectations**:
  - Unit test: GET /iol/account-status with valid user → returns account status
  - Unit test: GET /iol/account-status uses Redis cache
  - Unit test: GET /iol/account-status without JWT → returns 401

### Task 3.8: Deprecate Manual Portfolio Entry UI
- [x] **COMPLETE**
- **Description**: Hide or remove manual portfolio entry UI. Redirect old manual edit URLs to read-only portfolio view.
- **Files to Touch**:
  - `frontend/src/app/(dashboard)/portfolio/page.tsx` (update to read-only display; remove "Add Holdings" and "Edit Holdings" buttons)
  - `frontend/src/app/(dashboard)/portfolio/edit/[ticker]/page.tsx` (if exists; add redirect to /portfolio)
  - `frontend/src/components/PortfolioForm.tsx` (if exists; remove or hide)
  - Old manual portfolio API routes (if exist; add deprecation notices or remove)
- **Acceptance Criteria** (from spec portfolio-sync DeltaR5):
  - Portfolio page displays read-only holdings list (from API /iol/holdings)
  - No "Add Holdings", "Edit Holdings", or "Delete Holdings" buttons visible
  - Manual edit URLs (e.g., /portfolio/edit/GGAL) redirect to /portfolio with notice: "Manual portfolio entry is no longer supported; portfolio is synced from IOL"
  - Old manual portfolio tables in DB are retained (for rollback safety) but not used
- **Test Expectations**:
  - Unit test: portfolio page fetches holdings from /iol/holdings
  - Integration test: no "Add Holdings" button visible
  - Integration test: navigating to /portfolio/edit/TICKER → redirects to /portfolio

---

## PR 4: Currency-Aware Pricing (ARS/USD) (150–200 lines)

**Dependency**: PR 3 (portfolio holdings have currency field)  
**Spec Requirements**: currency-aware-pricing (DeltaR1–R6)  
**Design References**: Section 3 (Currency-Aware Pricing)  
**Start/Finish Boundary**: Price factory routes ARS→IOL, USD→yfinance; IOL quotes provider implemented; price source badges displayed; caching strategy in place.  
**Rollback Boundary**: Revert factory changes, IOL quotes provider; revert to single yfinance source for all tickers.  
**Test Approach**: Strict TDD: test price factory routing by currency; test IOL quotes provider; test caching with different TTLs; test fallback logic; test price source indicator.

### Task 4.1: Extended Price Factory with Currency Routing
- **Description**: Extend existing price factory to accept currency parameter and route ARS→IOL, USD→yfinance.
- **Files to Touch**:
  - `backend/app/providers/factory.py` (update; extend `get_price_provider()` to accept currency param)
- **Acceptance Criteria** (from design Section 3.1):
  - Method signature: `get_price_provider(currency: str = "USD") -> AbstractMarketDataProvider`
  - Logic:
    - If currency == "ARS" → return IOLQuotesProvider()
    - Else → return YFinanceProvider()
  - New method: `get_iol_quotes_provider() -> IOLQuotesProvider`
  - Backward compatible: existing callers without currency param get yfinance (default USD)
  - Type hints complete
- **Test Expectations**:
  - Unit test: factory returns IOLQuotesProvider for ARS
  - Unit test: factory returns YFinanceProvider for USD
  - Unit test: factory returns YFinanceProvider for unknown currency (default)

### Task 4.2: IOL Quotes Provider Class
- **Description**: Implement `backend/app/providers/iol_quotes_provider.py` with IOLQuotesProvider implementing AbstractMarketDataProvider.
- **Files to Touch**:
  - `backend/app/providers/iol_quotes_provider.py` (new)
  - `backend/app/providers/factory.py` (import IOLQuotesProvider)
- **Acceptance Criteria** (from design Section 3.1):
  - Class `IOLQuotesProvider(AbstractMarketDataProvider)`:
    - Property `name = "iol-bcba"`
    - Method `async fetch_price(ticker: str) -> PriceData`
      - Call iol_client.fetch_quotes(system_token, [ticker])
      - Extract last_price from response
      - Return PriceData(ticker, price, currency="ARS", source="iol-bcba", timestamp)
    - Method `async fetch_price_history(ticker: str, period: str) -> list[PriceBar]`
      - Not supported by IOL; defer to yfinance
      - Call yfinance_provider.fetch_price_history()
  - Error handling:
    - IOLAuthError → log, fall back to yfinance
    - IOLError → log, fall back to yfinance
    - Fallback: yfinance.fetch_price(ticker) with currency converted to source
  - Uses system service account token (stored in config/env or fetched via special endpoint)
  - Returns PriceData with source field populated
- **Test Expectations**:
  - Unit test: fetch_price() with mocked IOL quote → returns PriceData with source="iol-bcba"
  - Unit test: fetch_price() with IOL error → falls back to yfinance, returns PriceData with source="yfinance"
  - Unit test: fetch_price_history() delegates to yfinance
  - Mock: IOL quotes calls are mocked; yfinance calls are mocked

### Task 4.3: Price Source Metadata in Responses
- **Description**: Ensure all price responses include source field (iol-bcba, yfinance, stale). Update existing PriceData model if needed.
- **Files to Touch**:
  - `backend/app/schemas/price.py` (or existing price schema file; update PriceData model)
- **Acceptance Criteria** (from design Section 3.3):
  - `PriceData` schema/model includes:
    - ticker (str)
    - price (Decimal)
    - currency (str)
    - source (str) — "iol-bcba" | "yfinance" | "stale"
    - source_name (str) — "IOL BCBA" | "Yahoo Finance"
    - fetched_at (datetime)
    - confidence (str) — "high" | "medium" | "low"
  - Response example:
    ```json
    {
      "ticker": "GGAL",
      "price": 250.50,
      "currency": "ARS",
      "source": "iol-bcba",
      "source_name": "IOL BCBA",
      "fetched_at": "2026-06-12T17:45:00Z",
      "confidence": "high"
    }
    ```
- **Test Expectations**:
  - Unit test: PriceData serializes with source and source_name fields
  - Unit test: stale price has source="stale", confidence="low"

### Task 4.4: Price Caching Strategy (Separate by Source)
- **Description**: Implement caching with separate TTLs: IOL 1-min, yfinance 5-min, stale price 24-hr fallback.
- **Files to Touch**:
  - `backend/app/services/price_service.py` (new or update existing if present)
  - `backend/app/core/cache.py` (add cache helpers)
- **Acceptance Criteria** (from design Section 3.4, spec DeltaR5):
  - Cache keys: `price:{ticker}:{currency}`, `price:{ticker}:{currency}:last_known` (for stale fallback)
  - TTLs:
    - IOL BCBA: 1 minute during trading hours (09:00–17:00 ARS time), 5 minutes after hours
    - yfinance: 5 minutes (always)
    - Last-known price: 24 hours (for fallback use)
  - Method `get_price_cached(ticker: str, currency: str) -> PriceData`:
    - Check Redis cache for `price:{ticker}:{currency}`
    - If hit, return cached PriceData
    - If miss:
      - Call provider.fetch_price()
      - Store in cache with appropriate TTL
      - Also store in last-known cache with 24-hr TTL
      - Return PriceData
  - Fallback logic:
    - If both primary and fallback fail:
      - Check last-known cache
      - If found, mark as source="stale"
      - Return stale price
      - If not found, return None or default price
- **Test Expectations**:
  - Unit test: cache stores IOL price with 1-min TTL
  - Unit test: cache stores yfinance price with 5-min TTL
  - Unit test: cache hit returns cached price without calling provider
  - Unit test: cache miss calls provider, stores, returns fresh price
  - Unit test: stale price fallback returns with source="stale", confidence="low"

### Task 4.5: Per-Holding Currency Routing in Ingestion Service
- **Description**: Update existing ingestion service to use currency-aware routing when fetching prices.
- **Files to Touch**:
  - `backend/app/services/ingestion_service.py` (update; add currency routing)
- **Acceptance Criteria** (from design Section 3.2):
  - Method signature: `async ingest_ticker(ticker: str, user_id: str, currency: str = None) -> IngestionResult`
  - Logic:
    - If currency not provided, fetch from portfolio_holdings for this user/ticker
    - If not in portfolio, default to "USD"
    - Call `ProviderFactory.get_price_provider(currency)`
    - Call provider.fetch_price()
    - Cache and persist price
    - Return result with source field
  - Type hints complete
- **Test Expectations**:
  - Unit test: ingest_ticker with ARS currency → uses IOL provider
  - Unit test: ingest_ticker with USD currency → uses yfinance provider
  - Unit test: ingest_ticker with no currency → fetches from portfolio, uses correct provider

### Task 4.6: Price Source Indicator Frontend Component
- **Description**: Create frontend component to display price source badge (IOL, yfinance, Stale) next to prices.
- **Files to Touch**:
  - `frontend/src/components/PriceSourceBadge.tsx` (new)
- **Acceptance Criteria** (from spec DeltaR3):
  - Component: `<PriceSourceBadge source="iol-bcba" fetched_at="..." />`
  - Display:
    - IOL → green badge "IOL"
    - yfinance → blue badge "yfinance"
    - stale → orange badge "Stale"
  - Tooltip on hover: timestamp (e.g., "Updated 5 minutes ago")
  - Color scheme uses design tokens (green/blue/orange from palette)
- **Test Expectations**:
  - Unit test: component renders correct badge color for each source
  - Unit test: tooltip displays formatted timestamp

### Task 4.7: Analysis Page Price Display with Currency Routing
- **Description**: Update analysis page ([ticker]) to display current price with source badge, using currency-aware routing.
- **Files to Touch**:
  - `frontend/src/app/(dashboard)/analysis/[ticker]/page.tsx` (update)
  - `frontend/src/components/Analysis/TickerPrice.tsx` (new or update)
- **Acceptance Criteria** (from spec DeltaR6):
  - Page displays: "Current Price: $X.XX (IOL)" or "Current Price: $X.XX (yfinance)"
  - Price is fetched from API endpoint that returns source
  - If user has ticker in portfolio, use portfolio currency; else default to USD
  - Source badge displayed next to price
- **Test Expectations**:
  - Integration test: analysis page loads price with source badge
  - Integration test: ARS holding shows IOL source; USD shows yfinance

### Task 4.8: Dashboard Holdings Table with Price Source Badges
- **Description**: Update dashboard holdings table to include current price with source badge and proper formatting.
- **Files to Touch**:
  - `frontend/src/components/Dashboard/HoldingsTable.tsx` (update or create)
  - `frontend/src/app/(dashboard)/dashboard/page.tsx` (ensure uses updated table)
- **Acceptance Criteria** (from spec DeltaR6):
  - Table columns: Ticker, Quantity, Avg Buy Price, Current Price (with source badge), Current Value, Unrealized P&L
  - Source badge displayed next to each price
  - Colors: price gains green, losses red; source badge colored by source
- **Test Expectations**:
  - Unit test: HoldingsTable renders with correct columns
  - Integration test: holdings load with source badges for each price

---

## PR 5: Dashboard + Base Strategy Templates (200–350 lines)

**Dependency**: PR 4 (currency-aware pricing complete)  
**Spec Requirements**: dashboard-summary (DeltaR1–R7), strategy-templates (DeltaR1–R6)  
**Design References**: Section 5 (Dashboard Metrics Computation), Section 6 (Strategy Templates)  
**Start/Finish Boundary**: Dashboard page displays 4 core metrics (Total Invested, Current Value, Unrealized P&L, Realized P&L); holdings table sortable; connection status header; Refresh button. Strategy templates seeded (3–5 templates); read-only display with cards/accordion.  
**Rollback Boundary**: Revert dashboard service, endpoints, migrations (strategy templates), frontend dashboard page, strategies page.  
**Test Approach**: Strict TDD: test dashboard metrics calculation with mocked prices and holdings; test strategy template seeding; test endpoints; test strategy template display.

### Task 5.1: Database Schema — Strategy Templates Table
- **Description**: Create Alembic migration for `strategy_templates` table.
- **Files to Touch**:
  - `backend/alembic/versions/[timestamp]_add_strategy_templates.py` (new migration)
- **Acceptance Criteria** (from spec strategy-templates Database Schema):
  - Table schema:
    - `id` (INT PK, auto-increment)
    - `name` (VARCHAR 100, unique)
    - `description` (TEXT)
    - `how_it_works` (TEXT)
    - `recommended_timeframe` (VARCHAR 100)
    - `best_suited_for` (VARCHAR 200)
    - `risk_level` (VARCHAR 20, CHECK IN ('low', 'medium', 'high'))
    - `created_at` (TIMESTAMP, server default NOW())
    - `updated_at` (TIMESTAMP, server default NOW())
  - Migration is reversible
- **Test Expectations**:
  - Migration test: run forward and backward; table exists after forward

### Task 5.2: SQLAlchemy Model — StrategyTemplate
- **Description**: Create `backend/app/models/strategy_template.py` with StrategyTemplate model.
- **Files to Touch**:
  - `backend/app/models/strategy_template.py` (new)
  - `backend/app/models/__init__.py` (add import)
- **Acceptance Criteria**:
  - Model fields: id, name, description, how_it_works, recommended_timeframe, best_suited_for, risk_level, created_at, updated_at
  - Type hints complete
  - No user relationship (templates are system-wide, not user-owned in MVP)
- **Test Expectations**:
  - Unit test: model instantiates and serializes correctly

### Task 5.3: Strategy Templates Seeding
- **Description**: Create seed data or migration to insert 3–5 base strategy templates on app startup or via command.
- **Files to Touch**:
  - `backend/app/core/migrations/seed_strategies.py` (new)
  - OR `backend/alembic/versions/[timestamp]_seed_strategy_templates.py` (migration-based)
  - `backend/app/main.py` (call seed on startup)
- **Acceptance Criteria** (from spec strategy-templates DeltaR1, DeltaR3, Template Specifications):
  - Seeds 4 templates:
    1. Value Investing (Medium Risk)
    2. Growth Investing (High Risk)
    3. Dividend/Income Investing (Low Risk)
    4. Dollar-Cost Averaging (Low–Medium)
  - Each template has populated name, description, how_it_works, recommended_timeframe, best_suited_for, risk_level
  - Seed is idempotent (checks if template exists by name; skips if already seeded)
  - Seed is logged: "Seeded 4 base strategy templates"
  - Seed is called on app startup or can be run manually: `python -m backend.app.core.migrations.seed_strategies`
- **Test Expectations**:
  - Unit test: seed script inserts templates into DB
  - Unit test: seed is idempotent (run twice, only 4 templates exist)
  - Integration test: app startup runs seed; templates are queryable from DB

### Task 5.4: Dashboard Metrics Service
- **Description**: Implement `backend/app/services/dashboard_service.py` with DashboardService class for computing portfolio metrics.
- **Files to Touch**:
  - `backend/app/services/dashboard_service.py` (new)
- **Acceptance Criteria** (from design Section 5.1, spec DeltaR2–R5):
  - Class `DashboardService`:
    - Method `async compute_metrics(user_id: UUID, db: AsyncSession) -> DashboardMetrics`
      - Query portfolio_holdings for user_id
      - For each holding, fetch current price via price_service.get_price_cached()
      - Calculate:
        - Total Invested: sum(shares × avg_buy_price) for all holdings
        - Current Value: sum(shares × current_price) for all holdings
        - Unrealized P&L: current_value - total_invested
        - Return %: (unrealized_pnl / total_invested) × 100
      - Realized P&L: fetch from IOL or calculated from past sales (if available; otherwise 0 or null)
      - Return DashboardMetrics object with all 4 values
  - Error handling:
    - If no holdings, return all zeros
    - If price fetch fails, use avg_buy_price as fallback for current_price (and log)
  - All methods are async
  - Type hints complete
- **Test Expectations**:
  - Unit test: compute_metrics with 2 holdings (ARS and USD) → calculates correct totals
  - Unit test: compute_metrics with no holdings → returns all zeros
  - Unit test: price fetch failure uses fallback price
  - Unit test: unrealized P&L and % return calculated correctly

### Task 5.5: Dashboard Metrics Caching
- **Description**: Add caching layer for dashboard metrics (1-minute TTL per user).
- **Files to Touch**:
  - `backend/app/services/dashboard_service.py` (add cache logic)
  - OR `backend/app/core/cache.py` (if cache helpers needed)
- **Acceptance Criteria** (from design Section 5.2):
  - Cache key: `dashboard:metrics:{user_id}`
  - TTL: 60 seconds
  - Get logic:
    - Check Redis cache for key
    - If hit, return cached metrics
    - If miss, call compute_metrics(), store in cache, return
  - Cache invalidation: manual refresh button triggers re-compute (cache delete + refetch)
- **Test Expectations**:
  - Unit test: metrics cached for 60 seconds
  - Unit test: cache miss triggers compute_metrics() call
  - Unit test: manual refresh clears cache

### Task 5.6: /dashboard/metrics Endpoint
- **Description**: Implement `GET /dashboard/metrics` endpoint that returns cached/computed dashboard metrics.
- **Files to Touch**:
  - `backend/app/api/dashboard.py` (new)
  - `backend/app/main.py` (include router)
- **Acceptance Criteria** (from spec DeltaR1, design Section 5.3):
  - Endpoint: `GET /dashboard/metrics` (requires JWT)
  - Response (200 OK):
    ```json
    {
      "total_invested": 500000.00,
      "current_value": 520000.50,
      "unrealized_pnl": 20000.50,
      "return_percent": 4.0,
      "realized_pnl": 0.00,
      "last_updated": "2026-06-12T17:45:00Z"
    }
    ```
  - Logic:
    1. Extract current_user from JWT
    2. Call dashboard_service.get_metrics_cached(user_id)
    3. Return metrics or 500 on error
  - Caching: 60-second Redis TTL (managed by service)
  - Error handling: if compute fails, return 500 with error message
- **Test Expectations**:
  - Unit test: GET /dashboard/metrics with valid user → returns metrics
  - Unit test: GET /dashboard/metrics without JWT → returns 401
  - Integration test: metrics endpoint uses cache

### Task 5.7: Dashboard Page Component (Frontend)
- **Description**: Implement `/dashboard` page with metric cards, holdings table, connection status header, refresh button.
- **Files to Touch**:
  - `frontend/src/app/(dashboard)/dashboard/page.tsx` (update or create)
  - `frontend/src/components/Dashboard/MetricCard.tsx` (new)
  - `frontend/src/components/Dashboard/HoldingsTable.tsx` (update; ensure includes current price with source)
  - `frontend/src/components/Dashboard/ConnectionStatus.tsx` (new)
- **Acceptance Criteria** (from spec DeltaR1–R7):
  - **Connection Status Header**: Displays "Connected to IOL: [Account Name]" (green badge) or "IOL Connection Required" (red badge)
    - Fetches from GET /iol/status on page load
    - Cached for 5 minutes (or manual refresh button to update)
  - **4 Metric Cards**: Total Invested, Current Value, Unrealized P&L, Realized P&L (conditional)
    - Large, readable numbers
    - Labels
    - Trend indicators (up/down arrow, % change)
    - Fetched from GET /dashboard/metrics
  - **Holdings Table**:
    - Columns: Ticker (clickable to analysis page), Quantity, Avg Buy Price, Current Price (with source badge), Current Value, Unrealized P&L
    - Sortable by clicking column headers
    - Rows highlighted on hover
    - Large gains (>5%) light green background; large losses (<-5%) light red
    - Total row at bottom sums values
  - **Refresh Button**: "Refresh Portfolio"
    - Triggers POST /iol/sync-now
    - Shows loading spinner during sync
    - Displays toast on success: "Portfolio updated"
  - **Responsive**: Desktop and tablet (mobile deferred)
- **Test Expectations**:
  - Unit test: MetricCard component renders with correct label and value
  - Unit test: HoldingsTable renders with all columns
  - Unit test: Ticker links navigate to analysis page
  - Integration test: page loads metrics and holdings
  - Integration test: refresh button triggers sync and updates data

### Task 5.8: Strategies Page with Template Display
- **Description**: Implement `/strategies` page displaying base strategy templates as cards/accordion.
- **Files to Touch**:
  - `frontend/src/app/(dashboard)/strategies/page.tsx` (update or create)
  - `frontend/src/components/Strategies/StrategyCard.tsx` (new)
  - `frontend/src/components/Strategies/StrategyAccordion.tsx` (new)
- **Acceptance Criteria** (from spec strategy-templates DeltaR2–R3):
  - Page title: "Investment Strategies"
  - Displays 4 base template cards in a grid or list
  - Each card shows:
    - Title (strategy name)
    - Description (1–2 sentence summary)
    - Risk level badge (Low green, Medium yellow, High red)
    - "View Details" button or click-to-expand
  - Expanded view shows:
    - Full description
    - "How It Works" (numbered steps)
    - Recommended timeframe
    - Best suited for
    - Risk level
  - No "Create Custom Strategy" button (deferred to Phase 2)
  - Cards are collapsible/expandable (accordion)
  - Responsive grid (desktop and tablet)
- **Test Expectations**:
  - Unit test: StrategyCard renders correctly with data
  - Unit test: accordion expand/collapse works
  - Integration test: strategies page loads and displays 4 templates

### Task 5.9: /strategies Endpoint
- **Description**: Implement `GET /strategies` endpoint returning all base strategy templates.
- **Files to Touch**:
  - `backend/app/api/strategies.py` (new)
  - `backend/app/main.py` (include router)
- **Acceptance Criteria** (from spec strategy-templates DeltaR4):
  - Endpoint: `GET /strategies` (public, no JWT required for MVP)
  - Response (200 OK):
    ```json
    {
      "strategies": [
        {
          "id": 1,
          "name": "Value Investing",
          "description": "A strategy focused on finding undervalued stocks...",
          "how_it_works": "1. Screen for low P/E ratios...\n2. Analyze fundamentals...",
          "recommended_timeframe": "6–12 months to 2+ years",
          "best_suited_for": "Patient investors seeking undervalued stocks",
          "risk_level": "medium"
        },
        ...
      ]
    }
    ```
  - Caching: Redis 24-hour TTL (templates are static)
  - Error handling: 500 on DB error
- **Test Expectations**:
  - Unit test: GET /strategies returns 4 templates
  - Unit test: response matches schema
  - Unit test: cache hit returns cached response

### Task 5.10: DashboardMetrics Schema (Validation)
- **Description**: Create Pydantic model for DashboardMetrics response validation.
- **Files to Touch**:
  - `backend/app/schemas/dashboard.py` (new)
- **Acceptance Criteria**:
  - Schema `DashboardMetrics`:
    - total_invested (Decimal)
    - current_value (Decimal)
    - unrealized_pnl (Decimal)
    - return_percent (Decimal)
    - realized_pnl (Decimal, optional)
    - last_updated (datetime)
  - Used in endpoint response_model
  - All fields documented
- **Test Expectations**:
  - Unit test: schema validates correct data
  - Unit test: schema rejects missing required fields

---

## Summary of Task Dependencies

```
PR 1: UX Auth Gate + Dashboard Layout
  ├─ Task 1.1: Middleware
  ├─ Task 1.2: Route Groups
  ├─ Task 1.3: Design Tokens
  ├─ Task 1.4: App Shell Components
  ├─ Task 1.5: Login/Register Pages
  └─ Task 1.6: Integration Tests

PR 2: IOL OAuth2 Client + Token Manager (depends on PR 1 auth context)
  ├─ Task 2.1: IOLCredentials Table (migration)
  ├─ Task 2.2: IOLCredentials Model
  ├─ Task 2.3: Encryption Key Setup
  ├─ Task 2.4: IOL API Client (IOLClient)
  ├─ Task 2.5: Token Manager Service
  ├─ Task 2.6: Proactive Token Refresh Job
  ├─ Task 2.7: /iol/setup Endpoint
  └─ Task 2.8: /iol/status Endpoint

PR 3: Portfolio Sync + Account Status (depends on PR 2 IOL client)
  ├─ Task 3.1: Portfolio Holdings & Account Status Tables (migrations)
  ├─ Task 3.2: SQLAlchemy Models
  ├─ Task 3.3: Portfolio Sync Service
  ├─ Task 3.4: Periodic Sync Job
  ├─ Task 3.5: /iol/sync-now Endpoint
  ├─ Task 3.6: /iol/holdings Endpoint
  ├─ Task 3.7: /iol/account-status Endpoint
  └─ Task 3.8: Deprecate Manual Portfolio UI

PR 4: Currency-Aware Pricing (depends on PR 3 portfolio holdings with currency)
  ├─ Task 4.1: Extended Price Factory
  ├─ Task 4.2: IOL Quotes Provider
  ├─ Task 4.3: Price Source Metadata
  ├─ Task 4.4: Price Caching Strategy
  ├─ Task 4.5: Per-Holding Currency Routing
  ├─ Task 4.6: Price Source Indicator Component
  ├─ Task 4.7: Analysis Page Price Display
  └─ Task 4.8: Dashboard Holdings Table with Badges

PR 5: Dashboard + Strategy Templates (depends on PR 4 currency-aware pricing)
  ├─ Task 5.1: Strategy Templates Table (migration)
  ├─ Task 5.2: StrategyTemplate Model
  ├─ Task 5.3: Strategy Templates Seeding
  ├─ Task 5.4: Dashboard Metrics Service
  ├─ Task 5.5: Dashboard Metrics Caching
  ├─ Task 5.6: /dashboard/metrics Endpoint
  ├─ Task 5.7: Dashboard Page Component
  ├─ Task 5.8: Strategies Page Component
  ├─ Task 5.9: /strategies Endpoint
  └─ Task 5.10: DashboardMetrics Schema
```

---

## Review Workload Forecast

### Per-PR Line Estimate

| PR | Title | Est. Changed Lines | Risk | Notes |
|----|----|---|---|---|
| 1 | Auth Gate + Dashboard Layout | 200–300 | Low | Foundational UX; well-understood; no backend changes |
| 2 | IOL OAuth2 Client + Token Manager | 200–300 | Medium | Crypto/token handling; strict TDD required; background job scheduling |
| 3 | Portfolio Sync + Account Status | 200–250 | Medium | DB migrations; sync logic; error handling for IOL API flakiness |
| 4 | Currency-Aware Pricing | 150–200 | Medium | Price provider routing; caching; fallback strategy; front-end badges |
| 5 | Dashboard + Strategy Templates | 200–350 | Medium | Metrics calculation; template seeding; front-end dashboard + strategies pages |

**Total Estimated Changed Lines**: 950–1,400 lines

### Chained PRs Assessment

- **PR 1** (Auth Gate) is autonomous; can be reviewed and merged independently; no dependencies.
- **PR 2** (IOL Client) depends on PR 1 (user auth context); can merge after PR 1.
- **PR 3** (Portfolio Sync) depends on PR 2 (IOL client ready); can merge after PR 2.
- **PR 4** (Currency Pricing) depends on PR 3 (portfolio with currency field); can merge after PR 3.
- **PR 5** (Dashboard) depends on PR 4 (pricing complete); can merge after PR 4.

### Review Budget Forecast

- **PR 1** (UX): 60–90 min review
  - Middleware auth check (straightforward)
  - Route groups reorganization (file structure change, review for no 404s)
  - Design tokens (Tailwind config; validate colors, spacing, typography)
  - App shell (Header, Sidebar; responsive, accessibility)
  - Estimate: **Low (60 min)**

- **PR 2** (IOL OAuth2 Token): 90–120 min review
  - Encryption setup (security review; validate Fernet usage)
  - IOL API client (async, error handling, retry logic)
  - Token manager (database, encryption/decryption)
  - Token refresh job (scheduler, interval logic)
  - Endpoints (/iol/setup, /iol/status)
  - Estimate: **Medium (90–120 min)** — security-sensitive, requires careful review

- **PR 3** (Portfolio Sync): 75–105 min review
  - Database migrations (schema, constraints, indexes)
  - Sync service (upsert logic, conflict resolution)
  - Periodic sync job (scheduling, error handling, idempotency)
  - Endpoints (/iol/sync-now, /iol/holdings, /iol/account-status)
  - Deprecated UI (verify old routes hidden)
  - Estimate: **Medium (75–105 min)**

- **PR 4** (Currency Pricing): 75–100 min review
  - Factory routing (logic for ARS/USD)
  - IOL quotes provider (fallback logic, caching)
  - Price caching strategy (TTLs, last-known fallback)
  - Frontend components (badges, display logic)
  - Estimate: **Medium (75–100 min)**

- **PR 5** (Dashboard + Templates): 90–130 min review
  - Metrics calculation (math, caching, performance)
  - Template seeding (idempotency, content accuracy)
  - Dashboard page (component structure, responsiveness, accessibility)
  - Strategies page (template display, accordion)
  - API endpoints (/dashboard/metrics, /strategies)
  - Estimate: **Medium-High (90–130 min)**

**Total Review Time**: 390–555 minutes (~6.5–9 hours)  
**Per-PR Review Time**: 75–110 minutes per PR (avg. ~90 min)

### 400-Line Budget Risk Assessment

- **PR 1** (200–300 lines): **Low Risk** — well under 400 lines; straightforward UX changes
- **PR 2** (200–300 lines): **Low Risk** — under 400 lines; security review depth compensates for size
- **PR 3** (200–250 lines): **Low Risk** — under 400 lines
- **PR 4** (150–200 lines): **Low Risk** — under 400 lines
- **PR 5** (200–350 lines): **Low Risk** — upper range but likely under 400 with frontend/backend split; if frontend portions are heavy, consider splitting to separate PR if >400 realized

**Overall**: Chained PRs recommended: **Yes**  
All 5 PRs are individually under or near the 400-line threshold. **No PR is expected to exceed 400 lines**, so the stacked-to-main chain strategy is appropriate.

### Risks and Bottlenecks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| **Strict TDD enforced for backend tasks** | High | Plan 20–30% extra time for test writing; ensure mocking/fixtures are in place early (PR 2, 3, 4) |
| **Crypto/encryption key management (PR 2)** | High | Security review early; validate Fernet usage; document key rotation plan for Phase 2 |
| **IOL API availability during integration tests** | Medium | Mock all IOL calls in tests; no real HTTP to IOL API required; design tests to cover fallback paths |
| **Database migration reversibility** | Medium | Test all migrations both forward and backward before merge; document any data loss scenarios |
| **Price source badge rendering in frontend (PR 4, 5)** | Low | Design token colors ensure consistency; responsive on tablet/mobile (basic in MVP) |
| **Dashboard metrics performance** | Medium | Cache metrics for 1 minute; profile with many holdings (10+); document N+1 prevention strategies |
| **Strategy template content accuracy** | Low | Domain expert review deferred to Phase 2 if templates are inaccurate; MVP seeds with provided templates only |

### Decision Needed Before Apply

**None identified.** All 5 PRs are autonomous and can proceed to `sdd-apply` without further user decisions. Delivery strategy (`auto-chain`, `stacked-to-main`) is locked.

---

## Artifact Links

- **Spec Files**: `openspec/changes/iol-trading-and-ux-overhaul/specs/`
  - 01-auth-gate.md
  - 02-iol-connection.md
  - 03-portfolio-sync.md
  - 04-currency-aware-pricing.md
  - 05-dashboard-summary.md
  - 06-strategy-templates.md
  - 07-ux-overhaul.md
- **Design**: `openspec/changes/iol-trading-and-ux-overhaul/design.md`
- **Proposal**: `openspec/changes/iol-trading-and-ux-overhaul/proposal.md`

---

## Notes

- All backend tasks include **strict TDD requirements** (asyncio_mode=auto, SQLite in-memory fixtures, test + code in same commit).
- Frontend tasks verify via `next lint` and build; no test runner enforced for frontend MVP (responsive design verification via manual testing or Playwright E2E).
- Each PR includes a **rollback boundary** and **verification steps** for CI/CD pipeline.
- **No tasks are blocked**; all tasks are dependent on prior PR completion but are not blocked by external unknowns.
- **Chained PR merge strategy**: Each PR merges to main immediately after verification; no tracker branch needed (stacked-to-main decision).
- **Changed lines are well within 400-line budget**; no PR exceeds this threshold, so splitting is not necessary.
