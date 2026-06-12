# Spec: Portfolio Sync from IOL API

**Capability**: portfolio-sync  
**Status**: Pending Implementation  
**Scope**: Read-only portfolio holdings from IOL /portafolio endpoint, account status from /estadocuenta, periodic sync, manual sync endpoint  
**Out of Scope**: Manual portfolio entry UI (deprecated), portfolio editing, order execution, multi-account support, portfolio history/rollback  

---

## Delta Requirements

### DeltaR1: Read-Only Portfolio Holdings from IOL
**Requirement**: The backend MUST fetch the user's portfolio holdings from the IOL /portafolio endpoint. Holdings data MUST include ticker symbol, quantity, average buy price, and currency (ARS or USD). The app MUST treat IOL as the single source of truth; no manual portfolio entry is allowed in the UI.

**Rationale**: Current state has a manual portfolio (users manually enter ticker + shares + buy price). This creates sync friction and errors. IOL is the authoritative source; reading directly from IOL ensures data accuracy and eliminates duplicate entry.

**Acceptance Criteria**:
- Backend implements `GET /iol/holdings` endpoint (internal, requires JWT)
- Endpoint calls IOL GET /portafolio with the user's valid access token
- Endpoint parses the IOL response and transforms it into a normalized schema:
  ```json
  {
    "holdings": [
      {
        "ticker": "GGAL",
        "quantity": 50,
        "avg_buy_price": 250.0,
        "currency": "ARS"
      },
      {
        "ticker": "AAPL",
        "quantity": 10,
        "avg_buy_price": 145.0,
        "currency": "USD"
      }
    ]
  }
  ```
- Holdings are stored in PostgreSQL `portfolio_holdings` table (or equivalent) with columns: `user_id`, `ticker`, `quantity`, `avg_buy_price`, `currency`, `synced_at`
- The frontend displays portfolio holdings read from the database (not directly from the endpoint response)
- Existing manual portfolio entry UI (if present) is removed or deprecated; users cannot manually add/edit holdings

### DeltaR2: Account Status Fetch from IOL
**Requirement**: The backend MUST fetch account status from the IOL /estadocuenta endpoint. Account status MUST include cash balance, buying power, and account summary. This data is used for dashboard metrics and portfolio P&L calculations.

**Rationale**: Cash balance and account summary are needed to calculate total portfolio value and P&L accurately.

**Acceptance Criteria**:
- Backend implements `GET /iol/account-status` endpoint (internal, requires JWT)
- Endpoint calls IOL GET /estadocuenta with the user's valid access token
- Endpoint parses the IOL response and transforms it into a normalized schema:
  ```json
  {
    "cash_balance": 50000.00,
    "buying_power": 100000.00,
    "total_balance": 150000.00,
    "currency": "ARS"
  }
  ```
- Account status is stored in PostgreSQL `user_account_status` table with columns: `user_id`, `cash_balance`, `buying_power`, `total_balance`, `currency`, `synced_at`
- Endpoint caches the response for 5 minutes (Redis) to avoid hammering IOL API
- If IOL API is unreachable, endpoint returns the last cached/known state (graceful degradation)

### DeltaR3: Periodic Portfolio Sync
**Requirement**: The backend MUST run a periodic sync job (every 5–10 minutes) to automatically fetch the latest holdings and account status from IOL and update the database. Sync frequency is configurable. Sync failures are logged but do NOT crash the job.

**Rationale**: Portfolio data must stay fresh without requiring manual refresh. Periodic sync ensures the dashboard always reflects recent changes.

**Acceptance Criteria**:
- Backend implements a background job (FastAPI BackgroundTasks or Celery) that runs every 5–10 minutes (configurable)
- For each authenticated user with an active IOL connection, the job calls GET /iol/holdings and GET /iol/account-status
- Holdings data is merged with the existing `portfolio_holdings` table: existing rows are updated, new rows are inserted, sold holdings are marked as `quantity = 0` or deleted
- Account status is updated in the `user_account_status` table
- Job records the sync timestamp in `holdings.synced_at` and `account_status.synced_at`
- If a sync fails for a specific user (e.g., token expired), the job logs the error and moves to the next user; it does NOT crash
- If IOL API is completely down, the job skips the sync; existing data remains unchanged and is used as the last-known state
- Sync job completes within 30 seconds for a typical user (single holdings fetch, single account status fetch)

### DeltaR4: Manual Sync Endpoint
**Requirement**: The frontend MUST provide a "Refresh Portfolio" button (or equivalent) that triggers an on-demand sync of holdings and account status. The sync completes within a few seconds, and the UI reflects updated data immediately.

**Rationale**: Users may want to manually refresh their portfolio to see the latest IOL data (e.g., after a trade on the IOL platform outside this app).

**Acceptance Criteria**:
- Frontend includes a "Refresh Portfolio" button in the dashboard or portfolio page
- Button triggers POST /iol/sync-now endpoint (requires JWT)
- Endpoint calls `GET /iol/holdings` and `GET /iol/account-status`, updates the database, and returns:
  ```json
  {
    "status": "success",
    "holdings_count": 5,
    "synced_at": "2026-06-12T17:45:00Z"
  }
  ```
- If sync succeeds, frontend displays a toast/notification: "Portfolio updated (5 holdings, 2 min ago)"
- If sync fails, frontend displays an error toast: "Portfolio sync failed. Please try again later."
- Button is disabled during sync; spinner/loading state is shown
- Endpoint completes within 5 seconds (timeout) or returns a 504 error

### DeltaR5: Deprecate Manual Portfolio Entry UI
**Requirement**: All UI components and endpoints that allow manual portfolio entry (e.g., "Add Holdings", "Edit Holdings", "Delete Holdings" forms) MUST be removed or explicitly hidden. The portfolio is now read-only from IOL.

**Rationale**: Manual entry creates sync confusion; IOL is the single source of truth.

**Acceptance Criteria**:
- Portfolio page no longer displays "Add Holdings" or "Edit Holdings" buttons
- Existing manual portfolio database tables/columns are retained (for migration/rollback safety) but not used in the app
- Frontend does not render any form for manual portfolio entry
- If user navigates to a manual edit URL (e.g., /portfolio/edit/GGAL), they are redirected to the read-only portfolio view

---

## Database Schema Changes

### New Tables

```sql
-- Portfolio holdings synced from IOL
CREATE TABLE IF NOT EXISTS portfolio_holdings (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  ticker VARCHAR(20) NOT NULL,
  quantity DECIMAL(10, 2) NOT NULL,
  avg_buy_price DECIMAL(12, 2) NOT NULL,
  currency VARCHAR(3) NOT NULL, -- 'ARS' or 'USD'
  synced_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id, ticker)
);

-- Account status synced from IOL
CREATE TABLE IF NOT EXISTS user_account_status (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id),
  cash_balance DECIMAL(15, 2) NOT NULL,
  buying_power DECIMAL(15, 2),
  total_balance DECIMAL(15, 2),
  currency VARCHAR(3) DEFAULT 'ARS',
  synced_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(user_id)
);
```

---

## Acceptance Scenarios

### Scenario 1: Periodic Sync Fetches Latest Holdings

**Given** a user has an active IOL connection  
**When** the background sync job runs (every 5–10 minutes)  
**Then** the job calls IOL GET /portafolio and GET /estadocuenta  
**And** the job updates `portfolio_holdings` with the latest data  
**And** the job updates `user_account_status` with cash balance and account summary  
**And** the dashboard reflects the updated holdings and account status within 10 minutes  

---

### Scenario 2: User Sells a Holding, Sync Updates Portfolio

**Given** a user has 50 shares of GGAL in the app  
**When** the user sells 20 shares via the IOL platform (outside this app)  
**And** the background sync job runs  
**Then** the job calls IOL GET /portafolio and receives 30 shares of GGAL  
**And** the `portfolio_holdings` table is updated: GGAL quantity = 30  
**And** the dashboard reflects the updated quantity (30 shares)  

---

### Scenario 3: Manual Refresh Button

**Given** the user is on the dashboard  
**When** they click the "Refresh Portfolio" button  
**Then** the frontend disables the button and shows a loading spinner  
**And** the frontend calls POST /iol/sync-now  
**And** the backend fetches latest holdings and account status  
**And** the backend updates the database and returns 200  
**And** the frontend re-fetches the portfolio data and re-renders the dashboard  
**And** a toast notification appears: "Portfolio updated (5 holdings, now)"  

---

### Scenario 4: Sync Fails (IOL API Unreachable)

**Given** the background sync job is running  
**And** IOL API is unreachable (500 error)  
**When** the job calls IOL GET /portafolio  
**Then** the job logs the error: "IOL API unreachable; using last-known portfolio"  
**And** the job does NOT crash; it continues to the next user  
**And** the dashboard continues to display the last synced holdings (graceful degradation)  
**And** the `synced_at` timestamp is NOT updated (it reflects the last successful sync)  

---

### Scenario 5: User Navigates to Manual Portfolio Editor (Deprecated)

**Given** a user navigates to /portfolio/edit/GGAL (old manual edit URL)  
**When** the page loads  
**Then** the app redirects to /portfolio (read-only view)  
**And** no edit form is rendered  

---

## Implementation Notes

- **IOL Endpoint**: GET /portafolio returns a list of holdings with ticker, quantity, buy price, currency
- **Sync Frequency**: Default 5–10 minutes, configurable via `PORTFOLIO_SYNC_INTERVAL` env var
- **Conflict Resolution**: IOL is authoritative; local holdings are overwritten on each sync
- **Sold Holdings**: Holdings with quantity = 0 are treated as "sold"; display as a historical record or remove from active portfolio
- **Performance**: Sync job completes within 30 seconds per user; batch multiple users in parallel if needed
- **Error Handling**: Sync failures are logged (structured logging); alerts sent if sync is stale for >30 minutes
- **Caching**: Account status cached for 5 minutes in Redis to reduce IOL API load

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Portfolio stale data | Periodic sync every 5–10 min; manual refresh button; display `synced_at` timestamp |
| IOL API outage | Cache last-known state; display warning if data is stale for >30 min |
| Sync conflicts (user edits while syncing) | Read-only from IOL; no local edits allowed; sync is always authoritative |
| Sync timeout or slowness | Set 5-sec timeout on sync endpoint; run periodic job in background async |
| Sold holdings disappear unexpectedly | Mark sold holdings as `quantity = 0` in UI; retain in database for historical reference |
