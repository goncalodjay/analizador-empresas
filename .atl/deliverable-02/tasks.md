# Tasks: Portfolio CRUD (Deliverable 2)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1,000 |
| 400-line budget risk | HIGH |
| Chained PRs recommended | Yes |
| Suggested split | PR 4a (Backend, ~620 lines) → PR 4b (Frontend, ~380 lines) |

---

## PR 4a: Backend Portfolio CRUD (~620 lines)

### Task 4a.1 — Portfolio schemas
**Files:** `schemas/portfolio.py`
- `PortfolioPositionCreate` (ticker, shares, avg_buy_price, sector?, notes?)
- `PortfolioPositionUpdate` (all optional)
- `PortfolioPositionOut` (id, ticker, shares, avg_buy_price, sector, notes, created_at, updated_at)
- Use `Decimal` for monetary fields, `field_serializer("id", UUID → str)`
- **Verification:** schema instantiation test

### Task 4a.2 — Watchlist schemas
**Files:** `schemas/watchlist.py`
- `WatchlistCreate`, `WatchlistUpdate`, `WatchlistOut` (with ticker_count)
- `WatchlistDetail` (extends WatchlistOut with tickers list)
- `WatchlistTickerOut`, `WatchlistTickerAdd`
- **Verification:** schema instantiation test

### Task 4a.3 — Portfolio service
**Files:** `services/portfolio_service.py`
- `get_positions(db, user_id)` → list[PortfolioPosition]
- `get_position(db, position_id, user_id)` → PortfolioPosition | None
- `create_position(db, user_id, payload)` → PortfolioPosition (409 on dupe ticker)
- `update_position(db, position_id, user_id, payload)` → PortfolioPosition | None
- `delete_position(db, position_id, user_id)` → bool
- All queries filter by user_id
- **Verification:** service-layer tests

### Task 4a.4 — Watchlist service
**Files:** `services/watchlist_service.py`
- `get_watchlists(db, user_id)` → list[Watchlist] (load ticker count)
- `get_watchlist(db, watchlist_id, user_id)` → Watchlist | None (eager-load tickers)
- `create_watchlist(db, user_id, payload)` → Watchlist
- `update_watchlist(db, watchlist_id, user_id, payload)` → Watchlist | None
- `delete_watchlist(db, watchlist_id, user_id)` → bool
- `add_ticker(db, watchlist_id, user_id, ticker)` → Watchlist (409 on dupe)
- `remove_ticker(db, watchlist_id, user_id, ticker)` → bool
- **Verification:** service-layer tests

### Task 4a.5 — Portfolio API router
**Files:** `api/portfolio.py` + wire in `main.py`
- `GET /portfolio/positions` → list positions
- `POST /portfolio/positions` → create position
- `GET /portfolio/positions/{id}` → get position
- `PUT /portfolio/positions/{id}` → update position
- `DELETE /portfolio/positions/{id}` → delete position (204)
- All use `Depends(get_current_user)`
- **Verification:** integration tests with test client

### Task 4a.6 — Watchlist API router
**Files:** `api/watchlists.py` + wire in `main.py`
- `GET /watchlists` → list watchlists
- `POST /watchlists` → create watchlist
- `GET /watchlists/{id}` → get watchlist detail
- `PUT /watchlists/{id}` → update watchlist
- `DELETE /watchlists/{id}` → delete watchlist
- `POST /watchlists/{id}/tickers` → add ticker
- `DELETE /watchlists/{id}/tickers/{ticker}` → remove ticker
- **Verification:** integration tests with test client

### Task 4a.7 — Seed script
**Files:** `seed.py`
- Creates demo user if not exists
- Adds 3 sample positions (AAPL, MSFT, GOOGL)
- Creates 2 watchlists with tickers
- **Verification:** manual run, verify no errors

### Task 4a.8 — Backend integration tests
**Files:** `tests/test_portfolio.py`, `tests/test_watchlists.py`
- Test all portfolio CRUD scenarios (create, list, get, update, delete, duplicate, cross-user)
- Test all watchlist CRUD scenarios (create, list, get, update, delete, add ticker, remove ticker, duplicate ticker)
- Test authentication enforcement (401 on all endpoints without cookie)
- **Verification:** pytest passes all tests

---

## PR 4b: Frontend Portfolio CRUD (~380 lines)

### Task 4b.1 — TypeScript types
**Files:** `lib/types.ts` (modify existing)
- Add `PortfolioPosition`, `Watchlist`, `WatchlistDetail`, `WatchlistTicker` interfaces
- Add `PortfolioPositionCreate`, `PortfolioPositionUpdate`, `WatchlistCreate`, `WatchlistUpdate`
- **Verification:** TypeScript compilation

### Task 4b.2 — Portfolio page (list)
**Files:** `app/portfolio/page.tsx`, `components/portfolio/PortfolioTable.tsx`
- Table with columns: Ticker, Shares, Avg Price, Sector, Actions
- "Add Position" button linking to `/portfolio/new`
- Edit/delete action buttons per row
- Empty state message when no positions
- **Verification:** renders in Next.js dev server

### Task 4b.3 — Portfolio form (create/edit)
**Files:** `app/portfolio/new/page.tsx`, `app/portfolio/[id]/edit/page.tsx`, `components/portfolio/PositionForm.tsx`
- Shared `PositionForm` component with fields: ticker, shares, avg_buy_price, sector, notes
- Client-side validation (all required fields, positive numbers)
- Edit mode pre-fills from existing position data via GET
- Redirect to `/portfolio` on success
- **Verification:** renders both create and edit modes

### Task 4b.4 — Watchlist page (list)
**Files:** `app/watchlists/page.tsx`, `components/watchlist/WatchlistCard.tsx`
- Card grid layout showing each watchlist: name, description, ticker count
- "Create Watchlist" button
- Click card navigates to `/watchlists/[id]`
- **Verification:** renders in Next.js dev server

### Task 4b.5 — Watchlist detail + ticker management
**Files:** `app/watchlists/[id]/page.tsx`, `components/watchlist/WatchlistForm.tsx`, `components/watchlist/TickerInput.tsx`
- Displays watchlist name, description, list of tickers with remove button
- Inline "Add ticker" input with validation
- Edit watchlist name/description (inline or modal)
- Delete watchlist button with confirmation
- **Verification:** renders ticker list and add/remove works

### Task 4b.6 — Sidebar navigation update
**Files:** `components/layout/Sidebar.tsx` (modify existing)
- Add Portfolio and Watchlists links with icons
- Active state highlighting based on current path
- **Verification:** navigation links appear and highlight correctly
