# Spec: Dashboard Summary with Portfolio Metrics

**Capability**: dashboard-summary  
**Status**: Pending Implementation  
**Scope**: Dashboard page with 4 core metrics (Total Invested, Current Value, Unrealized P&L, Realized P&L), flat holdings list, connection status  
**Out of Scope**: Sector/asset-class breakdown, historical P&L charting, advanced analytics, multi-portfolio comparison, performance vs. benchmark  

---

## Delta Requirements

### DeltaR1: Dashboard Page Structure
**Requirement**: The dashboard MUST be the primary post-login entry point. It MUST display: (1) IOL connection status header, (2) 4 key metrics in cards or summary section, (3) a flat list of portfolio holdings with individual metrics, (4) a "Refresh Portfolio" button.

**Rationale**: Dashboard serves as the investment summary hub. Metrics give the user a quick snapshot of their portfolio health.

**Acceptance Criteria**:
- Dashboard route is `/dashboard` (existing, but currently a stub)
- Page loads after authentication and IOL setup (user is on /dashboard, not redirected)
- Header displays: "Connected to IOL: [Account Name]" with connection status badge (green if active)
- Four metric cards are displayed prominently:
  1. **Total Invested** (cost basis)
  2. **Current Portfolio Value** (sum of current market value)
  3. **Unrealized P&L** (current value - cost basis)
  4. **Realized P&L** (if user has sold holdings; otherwise display "—" or hide)
- Metric cards include:
  - Large, readable number
  - Label
  - Trend indicator (up/down arrow and % change, if applicable)
- Portfolio holdings table displays all user holdings:
  - Ticker
  - Quantity
  - Avg Buy Price
  - Current Price (with source badge)
  - Current Value (quantity × current price)
  - Unrealized P&L per holding
- "Refresh Portfolio" button is visible; triggers POST /iol/sync-now
- Page is responsive (desktop and tablet); mobile display is deferred (responsive web only)

### DeltaR2: Total Invested Metric Calculation
**Requirement**: Total Invested is the sum of all holdings' cost basis (quantity × average buy price) in the user's base currency (ARS). It represents the total amount the user has invested.

**Rationale**: Total Invested shows the user's cumulative capital allocation.

**Acceptance Criteria**:
- Query sums `portfolio_holdings.quantity × portfolio_holdings.avg_buy_price` for all holdings with currency = 'ARS'
- For USD holdings, convert to ARS using the current exchange rate (or display separately as "Total Invested (ARS)" and "Total Invested (USD)")
- If holdings have mixed currencies, the spec defers multi-currency consolidation; present metrics in ARS with a note that USD holdings are shown separately
- Metric updates after each portfolio sync
- Display format: "ARS 500,000.00" with comma separators

### DeltaR3: Current Portfolio Value Metric Calculation
**Requirement**: Current Portfolio Value is the sum of all holdings' current market value (quantity × current price) in the user's base currency. It represents the real-time value of the portfolio at current market prices.

**Rationale**: Shows the user what their portfolio is worth right now.

**Acceptance Criteria**:
- For each holding, calculate: `quantity × current_price` (current price fetched from price factory with currency-aware routing)
- Sum all holdings in ARS (convert USD holdings at the current exchange rate, or display separately)
- Query database to fetch holdings; for each holding, call price factory to get current price
- Cache the result for 1 minute (Redis) to avoid recalculating on every dashboard load
- Metric updates after each portfolio sync or manual refresh
- Display format: "ARS 520,000.50" with comma separators and 2 decimal places

### DeltaR4: Unrealized P&L Metric Calculation
**Requirement**: Unrealized P&L is the difference between Current Portfolio Value and Total Invested. It represents the user's profit or loss on their current holdings (not yet sold).

**Rationale**: Unrealized P&L shows the user's current gain/loss without accounting for tax or commissions.

**Acceptance Criteria**:
- Calculate as: `Unrealized P&L = Current Portfolio Value - Total Invested`
- Display in ARS with sign and color:
  - Positive: green, "+" prefix, e.g., "+ARS 20,000.50"
  - Negative: red, "-" prefix, e.g., "-ARS 5,000.00"
  - Zero: gray, "ARS 0.00"
- Also display % return: `(Unrealized P&L / Total Invested) × 100`, e.g., "+4.0%"
- Metric updates automatically when holdings or prices change

### DeltaR5: Realized P&L Metric (Conditional)
**Requirement**: Realized P&L is displayed ONLY if the user has sold any holdings (i.e., has a realized gain or loss). It represents the user's cumulative profit or loss from past trades. If the user has no sales history, the metric is hidden or displays "—".

**Rationale**: Realized P&L is not applicable to users who have never sold; showing it conditionally reduces visual clutter. Proposal Q4 specified "include only if user has sold holdings".

**Acceptance Criteria**:
- Backend tracks realized P&L by checking IOL holdings history or transaction log (if available)
- If IOL API does not provide realized P&L directly, the backend calculates it from past sales: `sum(sale_price × quantity - cost_basis)` for each past sale
- Metric is displayed only if realized P&L != 0
- If realized P&L is not available or user has no sales, the metric card displays "—" or is hidden entirely
- If displayed:
  - Show in ARS with sign and color (green for gains, red for losses)
  - Display % of total cost basis
- Metric is a read-only summary; no action required from the user

### DeltaR6: Holdings Table
**Requirement**: The dashboard displays all portfolio holdings in a table format with columns: Ticker, Quantity, Avg Buy Price, Current Price, Current Value, Unrealized P&L. Table is sortable by most columns; filtering is deferred to Phase 2.

**Rationale**: Holdings table gives the user a detailed view of each position.

**Acceptance Criteria**:
- Table displays all holdings from `portfolio_holdings` table
- Columns (in order):
  1. **Ticker**: stock symbol (clickable to navigate to analysis page)
  2. **Quantity**: number of shares
  3. **Avg Buy Price**: average purchase price (e.g., "ARS 250.00")
  4. **Current Price**: current market price with source badge (IOL, yfinance, Stale)
  5. **Current Value**: quantity × current price (e.g., "ARS 12,500.00")
  6. **Unrealized P&L**: current value - cost basis per holding (color-coded: green for gains, red for losses)
- Table is sortable by clicking column headers (sort asc/desc)
- Rows are highlighted on hover for readability
- Rows with large gains (>5%) have a light green background; large losses (<-5%) have light red background
- Table is paginated if holdings > 10 (deferred to Phase 2; MVP shows all holdings on one page)
- Total row at the bottom sums: Quantity (N/A), Avg Buy Price (N/A), Current Value, Unrealized P&L

### DeltaR7: Connection Status Header
**Requirement**: The dashboard header displays the IOL connection status: "Connected to IOL: [Account Name]" with a green status badge if connected, or "IOL Connection Required" with a red badge if not connected.

**Rationale**: Users need to know their IOL connection is active.

**Acceptance Criteria**:
- Header fetches connection status from GET /iol/status
- If connected: display "Connected to IOL: Juan Pérez" with green badge
- If not connected or token expired: display "IOL Connection Required" with red badge and a "Reconnect" button
- Reconnect button navigates to /onboarding/iol-setup or /settings/iol-reconnect (deferred)
- Status is cached for 5 minutes; user can manually refresh connection via a "Refresh Status" button (deferred)

---

## Database Queries

### Query 1: Total Invested (ARS)
```sql
SELECT COALESCE(SUM(quantity * avg_buy_price), 0) AS total_invested
FROM portfolio_holdings
WHERE user_id = $1 AND currency = 'ARS';
```

### Query 2: Current Portfolio Value
```sql
SELECT COALESCE(SUM(quantity), 0) AS total_quantity
FROM portfolio_holdings
WHERE user_id = $1;
-- Then for each holding, fetch current price from cache/factory
-- Sum all holding values in ARS
```

### Query 3: Unrealized P&L
```sql
SELECT 
  SUM(quantity * avg_buy_price) AS cost_basis,
  -- Current value is calculated by summing (quantity * current_price) for each holding
  -- Unrealized P&L = Current Value - Cost Basis
```

### Query 4: Realized P&L (if available from IOL)
```sql
-- If IOL provides realized P&L endpoint, query that
-- Otherwise, calculate from past sales: SUM(sale_price * quantity - cost_basis)
-- Query deferred; MVP may not include realized P&L until IOL API clarification
```

---

## Acceptance Scenarios

### Scenario 1: User Logs In, Sees Dashboard

**Given** a user has logged in and completed IOL setup  
**When** they navigate to /dashboard  
**Then** the page loads with connection status: "Connected to IOL: Juan Pérez" (green)  
**And** four metric cards display:
- Total Invested: ARS 500,000.00
- Current Portfolio Value: ARS 520,000.50
- Unrealized P&L: +ARS 20,000.50 (+4.0%)
- Realized P&L: —
**And** portfolio holdings table shows 5 holdings (GGAL, YPFD, TXAR, AAPL, MSFT)  

---

### Scenario 2: Unrealized P&L Updates After Price Change

**Given** GGAL current price is $250.00; user has 50 shares  
**When** the price changes to $255.00 (fetched from price factory)  
**Then** the dashboard recalculates:
- Current Value: ARS 12,750.00 (50 × 255.00)
- Unrealized P&L per holding: +ARS 250.00
- Total Unrealized P&L: +ARS 20,750.00 (updated)  
**And** the metric card updates instantly (or within 1 minute of cache TTL)  

---

### Scenario 3: User Clicks Refresh Portfolio

**Given** the user is on the dashboard  
**When** they click "Refresh Portfolio"  
**Then** the button shows a loading spinner  
**And** the frontend calls POST /iol/sync-now  
**And** the backend fetches latest holdings and account status  
**And** the dashboard re-fetches metrics and updates displays  
**And** a toast notification appears: "Portfolio updated"  

---

### Scenario 4: Holdings Table Sorted by Current Value

**Given** the holdings table is displayed  
**When** the user clicks the "Current Value" column header  
**Then** the table rows are sorted by current value (descending, highest value first)  
**And** the column header shows a down arrow indicating sort direction  

---

### Scenario 5: User Has Sold Holdings, Realized P&L Displays

**Given** a user has sold 20 GGAL shares with a profit of ARS 5,000  
**When** they view the dashboard  
**Then** the Realized P&L metric card displays: "+ARS 5,000.00 (+1.0%)"  
**And** the card has a green background (gain)  

---

### Scenario 6: User Has Never Sold, Realized P&L Hidden

**Given** a user has never sold any holdings  
**When** they view the dashboard  
**Then** the Realized P&L metric card displays: "—"  
**Or** the card is hidden entirely (deferred to design)  

---

## Implementation Notes

- **Metric Calculation**: All metrics are calculated server-side (in the backend) and returned via a single GET /dashboard/metrics endpoint to reduce frontend complexity
- **Price Fetching**: Current Portfolio Value requires calling the price factory for each holding; cache this result for 1 minute to avoid repeated calls
- **Currency Conversion**: ARS/USD consolidation is deferred; MVP shows separate totals or notes USD holdings separately
- **Real-time Updates**: Dashboard does not auto-refresh; user must click "Refresh Portfolio" or rely on periodic sync (every 5–10 min in background)
- **Performance**: Dashboard page load must complete within 2 seconds (including metric calculation and price fetching)

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Slow metric calculation (many holdings) | Cache metric results for 1 min; batch price factory calls |
| Stale prices used in P&L | Display source badge on each price; log stale price usage |
| Missing Realized P&L from IOL API | MVP may not include realized P&L; use conditional display (show only if available) |
| High cache miss rate | Pre-warm cache on app startup; manually refresh on demand |
| Dashboard does not update after trades | Display "Refresh Portfolio" button; rely on periodic sync every 5–10 min |
