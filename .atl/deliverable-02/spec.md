# Spec: Portfolio CRUD (Deliverable 2)

## Intent
Enable the authenticated user to manage their stock portfolio positions and watchlist groups through a full-stack CRUD interface.

## Requirements

### R1 — Portfolio Position Management
**R1.1** The user can list all their portfolio positions, sorted by creation date.
**R1.2** The user can create a new position with: ticker, shares, avg buy price, sector (optional), notes (optional).
**R1.3** The user can update an existing position (ticker, shares, avg buy price, sector, notes).
**R1.4** The user can delete a position.
**R1.5** Duplicate ticker per user is rejected (409 Conflict).
**R1.6** All portfolio endpoints require authentication. Users can only access their own data.

### R2 — Watchlist Management
**R2.1** The user can list all their watchlists.
**R2.2** The user can create a watchlist with: name, description (optional).
**R2.3** The user can update a watchlist name and description.
**R2.4** The user can delete a watchlist (cascades to tickers).
**R2.5** The user can add a ticker to a watchlist.
**R2.6** The user can remove a ticker from a watchlist.
**R2.7** Duplicate ticker within the same watchlist is rejected (409 Conflict).
**R2.8** All watchlist endpoints require authentication. Users can only access their own data.

### R3 — Frontend Pages
**R3.1** `/portfolio` — table of positions with actions (add, edit, delete).
**R3.2** `/portfolio/new` — create position form.
**R3.3** `/portfolio/[id]/edit` — edit position form.
**R3.4** `/watchlists` — list of watchlist cards with create button.
**R3.5** `/watchlists/[id]` — watchlist detail showing tickers with add/remove actions.

### R4 — Seed Script
**R4.1** `backend/seed.py` populates a demo user with sample portfolio positions (AAPL, MSFT, GOOGL) and two watchlists ("Tech Giants", "Dividend Candidates").

### R5 — Data Compatibility
**R5.1** All list responses include `DataFreshnessTag` (value: `live` for user-entered data, always fresh).
**R5.2** Updated positions reflect `updated_at` timestamp.

## Scenarios

### S1: Create position
```
GIVEN an authenticated user
WHEN they POST /portfolio/positions with {ticker, shares, avg_buy_price}
THEN a new position is created, 201 returned, with id and timestamps
```

### S2: Duplicate ticker rejected
```
GIVEN user has a position with ticker AAPL
WHEN they POST /portfolio/positions with ticker AAPL again
THEN 409 Conflict is returned
```

### S3: List all positions
```
GIVEN user has 3 positions
WHEN they GET /portfolio/positions
THEN 200 with array of 3 positions, each with id, ticker, shares, avg_buy_price, sector, notes, timestamps
```

### S4: Update position
```
GIVEN user has a position with id=X
WHEN they PUT /portfolio/positions/X with updated shares
THEN 200 returned with updated position, updated_at changed
```

### S5: Delete position
```
GIVEN user has a position with id=X
WHEN they DELETE /portfolio/positions/X
THEN 204 returned, position no longer in list
```

### S6: Create watchlist with tickers
```
GIVEN an authenticated user
WHEN they POST /watchlists with {name, description}
THEN 201 returned, THEN POST /watchlists/{id}/tickers adds tickers
```

### S7: Delete watchlist cascades
```
GIVEN user has a watchlist with 3 tickers
WHEN they DELETE /watchlists/{id}
THEN watchlist and all its tickers are removed
```

### S8: Unauthenticated access rejected
```
GIVEN no valid access_token cookie
WHEN any /portfolio or /watchlists endpoint is called
THEN 401 Unauthorized
```

### S9: Cross-user access prevented
```
GIVEN user A has position X
WHEN user B tries to GET /portfolio/positions/X
THEN 404 Not Found (not 403 — do not reveal existence)
```
