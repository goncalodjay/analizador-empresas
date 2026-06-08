# Design: Portfolio CRUD (Deliverable 2)

## Technical Approach

Deliverable 2 adds backend CRUD endpoints for portfolio positions and watchlists, plus frontend pages to manage them. Uses the existing User, PortfolioPosition, Watchlist, and WatchlistTicker models already migrated. Follows the same layered pattern as the auth module: `api/` → `services/` → `models/`, with Pydantic `schemas/` for request/response contracts.

## Architecture

All portfolio/watchlist endpoints live under authenticated routes using `get_current_user` dependency. Cross-user isolation is enforced by filtering queries on `user_id` — a user can never see another user's data.

```
FastAPI Router Layer (api/)
├── api/portfolio.py     → /portfolio/positions/*
└── api/watchlists.py    → /watchlists/*
        │
        ▼
Service Layer (services/)
├── services/portfolio_service.py
└── services/watchlist_service.py
        │
        ▼
Model Layer (models/)
├── models/portfolio.py  → PortfolioPosition, Watchlist, WatchlistTicker (exists)
└── models/user.py       → User (exists)
```

## API Contracts

### Portfolio Positions

| Method | Path | Auth | Request Body | Response | Status |
|--------|------|------|-------------|----------|--------|
| GET | `/portfolio/positions` | Yes | — | `PortfolioPositionOut[]` | 200 |
| GET | `/portfolio/positions/{id}` | Yes | — | `PortfolioPositionOut` | 200/404 |
| POST | `/portfolio/positions` | Yes | `PortfolioPositionCreate` | `PortfolioPositionOut` | 201/409 |
| PUT | `/portfolio/positions/{id}` | Yes | `PortfolioPositionUpdate` | `PortfolioPositionOut` | 200/404 |
| DELETE | `/portfolio/positions/{id}` | Yes | — | — | 204/404 |

### Watchlists

| Method | Path | Auth | Request Body | Response | Status |
|--------|------|------|-------------|----------|--------|
| GET | `/watchlists` | Yes | — | `WatchlistOut[]` | 200 |
| GET | `/watchlists/{id}` | Yes | — | `WatchlistDetail` | 200/404 |
| POST | `/watchlists` | Yes | `WatchlistCreate` | `WatchlistOut` | 201 |
| PUT | `/watchlists/{id}` | Yes | `WatchlistUpdate` | `WatchlistOut` | 200/404 |
| DELETE | `/watchlists/{id}` | Yes | — | — | 204/404 |
| POST | `/watchlists/{id}/tickers` | Yes | `WatchlistTickerAdd` | `WatchlistDetail` | 200/409 |
| DELETE | `/watchlists/{id}/tickers/{ticker}` | Yes | — | — | 204/404 |

## Pydantic Schemas

```python
# schemas/portfolio.py

class PortfolioPositionCreate(BaseModel):
    ticker: str = Field(min_length=1, max_length=10)
    shares: Decimal  # Numeric(14,4)
    avg_buy_price: Decimal  # Numeric(12,4)
    sector: str | None = None
    notes: str | None = None

class PortfolioPositionUpdate(BaseModel):
    ticker: str | None = None
    shares: Decimal | None = None
    avg_buy_price: Decimal | None = None
    sector: str | None = None
    notes: str | None = None

class PortfolioPositionOut(BaseModel):
    id: str  # UUID serialized
    ticker: str
    shares: str  # Decimal serialized as string for precision
    avg_buy_price: str
    sector: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
```

```python
# schemas/watchlist.py

class WatchlistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None

class WatchlistUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

class WatchlistOut(BaseModel):
    id: str
    name: str
    description: str | None
    ticker_count: int  # computed, number of tickers
    created_at: datetime
    model_config = {"from_attributes": True}

class WatchlistTickerOut(BaseModel):
    ticker: str
    added_at: datetime
    model_config = {"from_attributes": True}

class WatchlistDetail(WatchlistOut):
    tickers: list[WatchlistTickerOut]

class WatchlistTickerAdd(BaseModel):
    ticker: str = Field(min_length=1, max_length=10)
```

## Frontend Routes

```
src/app/
├── (auth)/              # existing
├── dashboard/           # existing
├── portfolio/
│   ├── page.tsx         # List: table + Add button
│   ├── new/page.tsx     # Create form
│   └── [id]/edit/page.tsx  # Edit form
└── watchlists/
    ├── page.tsx         # List: card grid + Create button
    └── [id]/page.tsx    # Detail: ticker list + add/remove
```

## Frontend Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `PortfolioTable` | `components/portfolio/PortfolioTable.tsx` | Table of positions with edit/delete actions |
| `PositionForm` | `components/portfolio/PositionForm.tsx` | Create/edit form shared between new and edit pages |
| `WatchlistCard` | `components/watchlist/WatchlistCard.tsx` | Card with name, description, ticker count |
| `WatchlistForm` | `components/watchlist/WatchlistForm.tsx` | Create/edit form for watchlist metadata |
| `TickerInput` | `components/watchlist/TickerInput.tsx` | Inline input + add button for tickers |

## Seed Script

`backend/seed.py` — standalone script (not a management command):
1. Creates a demo user (`demo@analyzer.local` / `demopass123`) if not exists
2. Adds 3 positions: AAPL (50 shares @ $175.50), MSFT (20 shares @ $420.30), GOOGL (10 shares @ $141.25)
3. Creates 2 watchlists: "Tech Giants" (AAPL, MSFT, GOOGL, AMZN, NVDA), "Dividend Candidates" (JNJ, PG, KO, PEP)
4. Prints summary of created data

Run via: `cd backend && python seed.py`

## Review Workload Forecast

| Layer | Files | Est. Lines |
|-------|-------|-----------|
| Backend schemas | 2 new | ~80 |
| Backend services | 2 new | ~120 |
| Backend API routers | 2 new | ~160 |
| Backend seed script | 1 new | ~60 |
| Backend tests | 2 new | ~200 |
| Frontend pages | 5 new | ~150 |
| Frontend components | 5 new | ~200 |
| Frontend types | 1 modified | ~30 |
| **Total** | **20 files** | **~1,000 lines** |

> Risk: HIGH — exceeds 400-line review budget. Recommend splitting into 2 chained PRs:
> - **PR 4a: Backend** (schemas + services + routers + seed + tests, ~620 lines)
> - **PR 4b: Frontend** (pages + components + types, ~380 lines)
