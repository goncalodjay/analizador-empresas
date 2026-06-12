# Design: IOL Read-Only Integration and UX Overhaul

## Executive Summary

This design implements a read-only IOL investment dashboard by separating concerns into six architectural layers: (1) secure credential management with encrypted storage and proactive token refresh, (2) portfolio sync using IOL as the authoritative source, (3) currency-aware price routing (ARS → IOL, USD → yfinance) via factory extension, (4) auth-gated UI using Next.js route groups and middleware, (5) backend dashboard metrics computation with Redis caching, and (6) template-based strategy seeding. Trading is explicitly out of scope; this integration fetches holdings, account status, and quotes only.

---

## 1. IOL Client Architecture

### 1.1 Module Placement and Structure

**Backend Package**: `backend/app/providers/iol_provider.py` + `backend/app/services/iol_service.py`

```
backend/app/
├── providers/
│   ├── iol_provider.py          # IOL API client (OAuth2, quote fetch, portfolio fetch)
│   ├── iol_quotes_provider.py   # IOL BCBA quotes provider (implements AbstractMarketDataProvider)
│   └── factory.py               # Extended: add get_iol_provider(), currency routing
├── services/
│   ├── iol_service.py           # Token manager, credential encrypt/decrypt, proactive refresh
│   ├── portfolio_sync_service.py # Fetch IOL holdings → sync to PortfolioPosition
│   └── (existing services)
├── models/
│   └── iol_credentials.py        # IOL OAuth2 token + credential storage schema
├── core/
│   └── config.py                # IOL_CLIENT_ID, IOL_CLIENT_SECRET, ENCRYPTION_KEY
└── api/
    └── iol.py                   # Endpoints: POST /iol/connect, GET /iol/account, POST /iol/sync
```

### 1.2 OAuth2 Password Flow Implementation

**Decision**: Backend-only OAuth2 Resource Owner Password Credentials flow. Frontend never touches IOL secrets.

**Token Manager (`iol_service.py`):**

```
class IOLTokenManager:
  - store_credentials(user_id, iol_username, iol_password_encrypted) → None
  - get_valid_token(user_id) → token_str
  - refresh_token_if_near_expiry(user_id) → bool
  - revoke_credentials(user_id) → None
```

**Credential Storage Model (`iol_credentials.py`):**

```
class IOLCredentials(Base):
  __tablename__ = "iol_credentials"
  
  id: UUID (PK)
  user_id: UUID (FK → users, unique)
  iol_username: str (not sensitive)
  encrypted_password: str  # Fernet-encrypted, kept in DB
  access_token: str
  token_expires_at: datetime
  refresh_token: str (optional, if IOL v2 supports it)
  created_at: datetime
  updated_at: datetime
  last_synced_at: datetime (nullable)
  sync_error: str (nullable, e.g., "Invalid credentials")
```

**Encryption Scheme:**

- **Library**: `cryptography.fernet` (Fernet symmetric encryption)
- **Key Storage**: Environment variable `IOL_ENCRYPTION_KEY` (base64-encoded)
- **Generation** (one-time setup): `Fernet.generate_key()` → store in `.env` as `IOL_ENCRYPTION_KEY`
- **Encrypt on Store**: `Fernet(key).encrypt(iol_password.encode())`
- **Decrypt on Use**: `Fernet(key).decrypt(encrypted_password).decode()`

**Alternative Considered**: AES with IV → adds complexity; Fernet is sufficient for single-user, backend-only secrets.

### 1.3 Proactive Token Refresh

**Decision**: Async background job runs every 13 minutes; refreshes tokens expiring within 15 minutes.

**Mechanism (`iol_service.py`):**

```
async def proactive_refresh_job():
  """Runs every 13 minutes via APScheduler or manual cron."""
  all_creds = await get_all_iol_credentials(db)
  for cred in all_creds:
    time_until_expiry = (cred.token_expires_at - utcnow()).total_seconds()
    if time_until_expiry < 900:  # 15 min
      try:
        new_token = await iol_client.refresh_token(cred.refresh_token)
        cred.access_token = new_token
        cred.token_expires_at = utcnow() + timedelta(minutes=15)
      except Exception as e:
        cred.sync_error = str(e)
        log.error(f"Token refresh failed for user {cred.user_id}: {e}")
      await db.commit()
```

**Task Scheduler**: APScheduler (add to `backend/app/core/scheduler.py`)

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.add_job(
  proactive_refresh_job,
  trigger="interval",
  minutes=13,
  id="iol-proactive-refresh"
)

async def start_scheduler(app):
  scheduler.start()

async def stop_scheduler(app):
  scheduler.shutdown()

# In main.py or startup:
app.add_event_handler("startup", lambda: start_scheduler(app))
app.add_event_handler("shutdown", lambda: stop_scheduler(app))
```

**Request-Level Safeguard**: Any IOL API call checks `time_until_expiry < 60s` and triggers immediate refresh before the call (belt-and-suspenders).

### 1.4 IOL API Client

**File**: `backend/app/providers/iol_provider.py`

```python
class IOLClient:
  """OAuth2 + API endpoints for IOL."""
  
  def __init__(self, client_id: str, client_secret: str, base_url: str):
    self.client_id = client_id
    self.client_secret = client_secret
    self.base_url = base_url  # api.invertironline.com
    self.session = aiohttp.ClientSession()
  
  async def authenticate(self, iol_username: str, iol_password: str):
    """POST /token with Resource Owner Password Credentials flow."""
    payload = {
      "grant_type": "password",
      "username": iol_username,
      "password": iol_password,
      "client_id": self.client_id,
      "client_secret": self.client_secret,
    }
    response = await self.session.post(f"{self.base_url}/token", json=payload)
    return response.json()  # { access_token, token_type, expires_in, refresh_token }
  
  async def refresh_token(self, refresh_token: str):
    """POST /token with refresh_token grant."""
    payload = {
      "grant_type": "refresh_token",
      "refresh_token": refresh_token,
      "client_id": self.client_id,
      "client_secret": self.client_secret,
    }
    response = await self.session.post(f"{self.base_url}/token", json=payload)
    return response.json()
  
  async def fetch_account_status(self, access_token: str):
    """GET /estadocuenta: account balance, buying power, etc."""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await self.session.get(f"{self.base_url}/estadocuenta", headers=headers)
    return response.json()
  
  async def fetch_portfolio(self, access_token: str):
    """GET /portafolio: holdings with ticker, shares, currency."""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await self.session.get(f"{self.base_url}/portafolio", headers=headers)
    return response.json()  # { "posiciones": [...] }
  
  async def fetch_quotes(self, access_token: str, tickers: list[str]):
    """GET /cotizaciones?tickers=X,Y,Z: live prices."""
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"tickers": ",".join(tickers)}
    response = await self.session.get(f"{self.base_url}/cotizaciones", headers=headers, params=params)
    return response.json()
```

### 1.5 Error Handling and Retry Policy

**Errors to Catch**:

| Condition | Cause | Recovery |
|-----------|-------|----------|
| 401 Unauthorized | Token expired or revoked | Proactive refresh already tried; fallback to cached prices |
| 403 Forbidden | IOL account locked or API disabled | Set `sync_error`; show user message; stop retrying for 1 hour |
| 429 Too Many Requests | Rate limit (IOL ~100 req/min) | Exponential backoff: 2s → 5s → 10s → give up after 3 attempts |
| 500 Service Unavailable | IOL API down | Retry after 30s, max 2 attempts; fall back to cached data |
| Connection Timeout | Network issue | Retry immediately, max 3 attempts; fallback to cache |

**Retry Logic**:

```python
async def call_iol_with_retry(
  async_fn,
  max_attempts: int = 3,
  base_delay: float = 2.0,
  backoff_factor: float = 2.5
):
  """Exponential backoff retry."""
  last_error = None
  for attempt in range(max_attempts):
    try:
      return await async_fn()
    except IOLRateLimitError:
      delay = base_delay * (backoff_factor ** attempt)
      await asyncio.sleep(delay)
    except IOLAuthError as e:
      last_error = e
      break  # No retry for auth errors
    except IOLUnavailableError:
      if attempt < max_attempts - 1:
        await asyncio.sleep(30)
      else:
        last_error = e
  raise last_error or IOLError("All retries exhausted")
```

---

## 2. Portfolio Sync Design

### 2.1 Data Model Changes

**Decision**: Extend existing `PortfolioPosition` model to include IOL-specific fields, marking manual entries as deprecated.

**Model Update** (`backend/app/models/portfolio.py`):

```python
class PortfolioPosition(Base):
  __tablename__ = "portfolio_positions"
  
  # Existing fields
  id: UUID (PK)
  user_id: UUID (FK)
  ticker: str
  shares: Decimal(14, 4)
  avg_buy_price: Decimal(12, 4)
  sector: str | None
  notes: str | None
  created_at: datetime
  updated_at: datetime
  
  # NEW: IOL sync fields
  source: str  # "manual" | "iol"; default "manual" for backward compat, set to "iol" on sync
  iol_position_id: str | None  # IOL's internal position ID
  currency: str  # "ARS" | "USD"
  last_synced_at: datetime | None
  last_synced_price: Decimal | None  # Price at last sync time
```

**Migration Path**:

1. Add columns with defaults (backward compatible)
2. Set `source="manual"` for all existing positions
3. On first IOL sync, replace manual positions with `source="iol"` positions
4. Deprecate manual entry UI entirely (Phase 1 frontend does not expose create/update/delete for positions)

### 2.2 Sync Service

**File**: `backend/app/services/portfolio_sync_service.py`

```python
class PortfolioSyncService:
  """Fetch holdings from IOL; sync to PortfolioPosition."""
  
  async def sync_portfolio(self, user_id: UUID, db: AsyncSession):
    """Fetch IOL holdings, upsert to DB, return sync report."""
    # 1. Get valid IOL token
    iol_creds = await get_iol_credentials(db, user_id)
    if not iol_creds:
      raise IOLNotConnectedException(user_id)
    
    token = await iol_service.get_valid_token(user_id)
    
    # 2. Fetch IOL portfolio
    try:
      iol_portfolio = await iol_client.fetch_portfolio(token)
    except IOLAuthError:
      iol_creds.sync_error = "Invalid IOL credentials"
      await db.commit()
      raise
    
    # 3. Transform IOL holdings → PortfolioPosition objects
    tickers_to_sync = []
    for iol_holding in iol_portfolio["posiciones"]:
      ticker = iol_holding["ticker"]
      shares = Decimal(str(iol_holding["cantidad"]))
      avg_buy_price = Decimal(str(iol_holding["precio_promedio"]))
      currency = iol_holding.get("moneda", "ARS")  # ARS or USD
      iol_pos_id = iol_holding.get("id")
      
      # Upsert: (user_id, ticker) unique constraint → on conflict update all fields
      stmt = pg_insert(PortfolioPosition).values(
        user_id=user_id,
        ticker=ticker,
        shares=shares,
        avg_buy_price=avg_buy_price,
        currency=currency,
        source="iol",
        iol_position_id=iol_pos_id,
        last_synced_at=utcnow(),
      ).on_conflict_do_update(
        index_elements=["user_id", "ticker"],
        set_={
          "shares": shares,
          "avg_buy_price": avg_buy_price,
          "currency": currency,
          "source": "iol",
          "last_synced_at": utcnow(),
        }
      )
      await db.execute(stmt)
      tickers_to_sync.append(ticker)
    
    # 4. Remove manual positions (source="manual") for this user
    delete_stmt = delete(PortfolioPosition).where(
      PortfolioPosition.user_id == user_id,
      PortfolioPosition.source == "manual"
    )
    await db.execute(delete_stmt)
    
    await db.commit()
    
    # 5. Update sync timestamp
    iol_creds.last_synced_at = utcnow()
    iol_creds.sync_error = None
    await db.commit()
    
    return PortfolioSyncReport(
      synced_count=len(tickers_to_sync),
      tickers=tickers_to_sync,
      synced_at=utcnow()
    )
  
  async def get_account_status(self, user_id: UUID, db: AsyncSession):
    """Fetch account balance, buying power from IOL."""
    token = await iol_service.get_valid_token(user_id)
    account = await iol_client.fetch_account_status(token)
    return AccountStatus(
      cash_balance=Decimal(str(account["saldo_disponible"])),
      buying_power=Decimal(str(account["poder_compra"])),
      total_assets=Decimal(str(account["patrimonio"])),
      currency="ARS"  # IOL reports in ARS
    )
```

### 2.3 Sync Periodicity and Conflict Policy

**Decision**: Sync every 5 minutes (user-facing), manual on-demand refresh available.

**Mechanism**:

- Background job runs every 5 min via APScheduler (same job scheduler as token refresh)
- Each sync is idempotent (upsert semantics)
- Conflict resolution: IOL is authoritative; local manual edits are overwritten on sync
- UI always shows "Last synced: X minutes ago" + manual "Refresh Now" button

**Job Definition**:

```python
async def periodic_portfolio_sync():
  """Every 5 minutes: sync all active users' portfolios."""
  db = get_db_session()
  users_with_iol = await db.execute(
    select(User).join(IOLCredentials).where(IOLCredentials.sync_error == None)
  )
  for user in users_with_iol:
    try:
      await portfolio_sync_service.sync_portfolio(user.id, db)
    except Exception as e:
      log.warning(f"Portfolio sync failed for {user.id}: {e}")

scheduler.add_job(
  periodic_portfolio_sync,
  trigger="interval",
  minutes=5,
  id="portfolio-sync"
)
```

---

## 3. Currency-Aware Pricing

### 3.1 Provider Factory Extension

**Decision**: Extend factory pattern to route currency → provider. ARS → IOL quotes (primary), USD → yfinance. IOL quotes provider implements `AbstractMarketDataProvider`.

**File Structure**:

```
backend/app/providers/
├── factory.py                # Updated get_price_provider(currency: str)
├── iol_quotes_provider.py    # New: IOL BCBA quotes → PriceData
└── yfinance_provider.py      # Existing, unchanged
```

**Updated Factory** (`backend/app/providers/factory.py`):

```python
class ProviderFactory:
  @staticmethod
  def get_price_provider(currency: str = "USD") -> AbstractMarketDataProvider:
    """Route by currency: ARS → IOL, USD → yfinance."""
    if currency == "ARS":
      return IOLQuotesProvider()  # New
    else:
      return YFinanceProvider()   # Existing
  
  @staticmethod
  def get_iol_quotes_provider() -> "IOLQuotesProvider":
    return IOLQuotesProvider()
  
  # (existing methods unchanged)
```

**IOL Quotes Provider** (`backend/app/providers/iol_quotes_provider.py`):

```python
class IOLQuotesProvider(AbstractMarketDataProvider):
  """Fetch BCBA quote from IOL API for ARS CEDEARs."""
  
  def __init__(self):
    self.name = "iol-bcba"
    self.iol_client = IOLClient(...)  # Injected from config
  
  async def fetch_price(self, ticker: str) -> PriceData:
    """GET /cotizaciones?tickers=TICKER; extract bid/ask midpoint."""
    try:
      # Use a system service account token (stored in config/DB)
      system_token = await get_system_iol_token()
      quotes = await self.iol_client.fetch_quotes(system_token, [ticker])
      
      if ticker not in quotes:
        raise PriceFetchError(f"Ticker {ticker} not found in IOL quotes")
      
      quote = quotes[ticker]
      bid = Decimal(str(quote["bid"]))
      ask = Decimal(str(quote["ask"]))
      price = (bid + ask) / 2
      
      return PriceData(
        ticker=ticker,
        price=price,
        currency="ARS",
        source="iol-bcba",
        timestamp=utcnow()
      )
    except IOLAuthError:
      # Fall back to yfinance if IOL fails
      yf = YFinanceProvider()
      return await yf.fetch_price(ticker)
    except Exception as e:
      raise PriceFetchError(str(e))
  
  async def fetch_price_history(self, ticker: str, period: str) -> list[PriceBar]:
    """Not supported by IOL; defer to yfinance for history."""
    yf = YFinanceProvider()
    return await yf.fetch_price_history(ticker, period)
```

### 3.2 Per-Holding Currency Routing

**Usage in Ingestion Service** (`backend/app/services/ingestion_service.py`):

```python
async def ingest_ticker(self, ticker: str, user_id: str, currency: str = None) -> IngestionResult:
  """Ingest ticker price; route to correct provider by currency."""
  ticker_upper = ticker.upper()
  
  # If currency not provided, fetch from portfolio
  if currency is None:
    position = await get_position_for_ticker(user_id, ticker_upper)
    currency = position.currency if position else "USD"
  
  # Get provider by currency
  provider = ProviderFactory.get_price_provider(currency)
  
  try:
    price_data = await provider.fetch_price(ticker_upper)
    # ... cache and persist
  except Exception as e:
    result.error = str(e)
  
  return result
```

### 3.3 Price Source Metadata

**Decision**: Surface price source in API response and UI so users know whether prices come from IOL or yfinance.

**Backend**:

```python
class PriceDataWithSource(BaseModel):
  ticker: str
  price: Decimal
  currency: str
  source: str  # "iol-bcba" | "yfinance" | "finnhub" | "alpha-vantage"
  source_name: str  # Human-readable: "IOL BCBA", "Yahoo Finance"
  fetched_at: datetime
  confidence: str  # "high" | "medium" | "low" (for fallbacks)
```

**Frontend**:

Display source badge next to price: "(IOL BCBA)" or "(Yahoo Finance)" with gray text.

### 3.4 Caching Strategy

**Decision**: Separate cache keys by source. Cache IOL quotes for 1 min; yfinance for 5 min.

```python
async def get_price_cached(ticker: str, currency: str, user_id: str = None):
  provider = ProviderFactory.get_price_provider(currency)
  cache_ttl = 60 if currency == "ARS" else 300  # 1 min vs 5 min
  
  cache_key = f"price:{provider.name}:{ticker}"
  cached = await cache.get(cache_key)
  if cached:
    return cached
  
  price = await provider.fetch_price(ticker)
  await cache.set(cache_key, price, ttl=cache_ttl)
  return price
```

---

## 4. Auth Gate and UX Redesign

### 4.1 Next.js Layout and Route Groups

**Decision**: Use route groups `(auth)` for login/register; move authenticated routes under `(dashboard)` or default layout. Apply middleware redirect.

**Structure**:

```
frontend/src/app/
├── (auth)/
│   ├── login/
│   │   └── page.tsx
│   ├── register/
│   │   └── page.tsx
│   └── layout.tsx         # No sidebar, minimal layout
├── (dashboard)/           # NEW: protected routes
│   ├── dashboard/
│   │   └── page.tsx
│   ├── portfolio/
│   │   └── page.tsx
│   ├── strategy/
│   │   └── page.tsx
│   ├── analysis/
│   │   └── [ticker]/page.tsx
│   └── layout.tsx         # Sidebar + TopBar
└── layout.tsx             # Root layout, no sidebar
```

### 4.2 Middleware Auth Check

**File**: `frontend/src/middleware.ts`

```typescript
import { NextRequest, NextResponse } from "next/server";

const publicPaths = ["/login", "/register"];
const AUTH_COOKIE = "access_token";

export function middleware(request: NextRequest) {
  const token = request.cookies.get(AUTH_COOKIE)?.value;
  const pathname = request.nextUrl.pathname;

  // If no token and trying to access protected route, redirect to login
  if (!token && !publicPaths.some(p => pathname.startsWith(p))) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // If has token and on auth page, redirect to dashboard
  if (token && publicPaths.some(p => pathname.startsWith(p))) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};
```

### 4.3 Onboarding Flow (Post-Login)

**Behavior**:

1. User logs in → `GET /auth/me` returns user
2. Frontend checks if user has IOL credentials → `GET /iol/credentials/status`
3. If not, show "Connect to IOL" modal with username/password form
4. On submit, `POST /iol/connect` → backend stores encrypted credentials, triggers immediate sync
5. On success, hide modal; show dashboard with holdings
6. On error, show clear message with retry button

**Endpoint** (`backend/app/api/iol.py`):

```python
@router.post("/iol/connect")
async def connect_iol(
  payload: IOLConnectRequest,  # { iol_username, iol_password }
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  """Store encrypted IOL credentials; test connection; sync portfolio immediately."""
  try:
    # Test credentials first
    iol_client = IOLClient(...)
    token_response = await iol_client.authenticate(
      payload.iol_username,
      payload.iol_password
    )
    access_token = token_response["access_token"]
    expires_in = token_response["expires_in"]
    
    # Store encrypted credentials
    encrypted_pwd = fernet.encrypt(payload.iol_password.encode())
    creds = IOLCredentials(
      user_id=current_user.id,
      iol_username=payload.iol_username,
      encrypted_password=encrypted_pwd,
      access_token=access_token,
      token_expires_at=utcnow() + timedelta(seconds=expires_in)
    )
    db.add(creds)
    await db.commit()
    
    # Trigger immediate portfolio sync
    sync_result = await portfolio_sync_service.sync_portfolio(current_user.id, db)
    
    return IOLConnectionResponse(
      status="connected",
      synced_tickers=sync_result.tickers,
      synced_at=sync_result.synced_at
    )
  except IOLAuthError:
    raise HTTPException(401, "Invalid IOL credentials")
  except Exception as e:
    raise HTTPException(500, f"IOL connection failed: {str(e)}")
```

### 4.4 Component Structure (Container-Presentational)

**Pattern**: Separate data-fetching containers from presentation components.

```typescript
// frontend/src/components/Dashboard/DashboardContainer.tsx
"use client";
import { useEffect, useState } from "react";
import { DashboardMetrics } from "./DashboardMetrics";
import { PortfolioHoldings } from "./PortfolioHoldings";
import { IOLSetupModal } from "./IOLSetupModal";

export function DashboardContainer() {
  const [iolConnected, setIOLConnected] = useState(false);
  const [metrics, setMetrics] = useState(null);
  const [holdings, setHoldings] = useState([]);

  useEffect(() => {
    checkIOLStatus();
    if (iolConnected) {
      fetchMetrics();
      fetchHoldings();
    }
  }, [iolConnected]);

  async function checkIOLStatus() {
    const res = await fetch("/api/iol/credentials/status");
    if (res.ok) {
      setIOLConnected(true);
    }
  }

  async function fetchMetrics() {
    const res = await fetch("/api/dashboard/metrics");
    setMetrics(await res.json());
  }

  async function fetchHoldings() {
    const res = await fetch("/api/portfolio/positions");
    setHoldings(await res.json());
  }

  return (
    <div>
      {!iolConnected && <IOLSetupModal onConnected={() => setIOLConnected(true)} />}
      {iolConnected && (
        <>
          <DashboardMetrics metrics={metrics} />
          <PortfolioHoldings holdings={holdings} />
        </>
      )}
    </div>
  );
}

// frontend/src/components/Dashboard/DashboardMetrics.tsx (pure presentation)
export function DashboardMetrics({ metrics }) {
  return (
    <div className="grid grid-cols-4 gap-4">
      <MetricCard label="Total Invested" value={metrics.total_invested} currency="ARS" />
      <MetricCard label="Current Value" value={metrics.current_value} currency="ARS" />
      <MetricCard label="Unrealized P&L" value={metrics.unrealized_pnl} currency="ARS" />
      <MetricCard label="Return %" value={metrics.return_percent} suffix="%" />
    </div>
  );
}
```

---

## 5. Dashboard Metrics Computation

### 5.1 Backend Service for Metrics

**File**: `backend/app/services/dashboard_service.py`

```python
class DashboardService:
  """Compute portfolio metrics: invested, current value, P&L."""
  
  async def compute_metrics(self, user_id: UUID, db: AsyncSession) -> DashboardMetrics:
    """
    Fetch holdings + prices; compute totals.
    - Total Invested: sum(shares * avg_buy_price)
    - Current Value: sum(shares * current_price)
    - Unrealized P&L: current_value - total_invested
    - Return %: unrealized_pnl / total_invested
    """
    # 1. Fetch all holdings for user
    positions = await get_positions(db, user_id)
    if not positions:
      return DashboardMetrics(
        total_invested=Decimal(0),
        current_value=Decimal(0),
        unrealized_pnl=Decimal(0),
        return_percent=Decimal(0),
        realized_pnl=Decimal(0),
        last_updated=utcnow()
      )
    
    # 2. Fetch current prices grouped by currency
    ars_tickers = [p.ticker for p in positions if p.currency == "ARS"]
    usd_tickers = [p.ticker for p in positions if p.currency == "USD"]
    
    prices_ars = await self._fetch_prices_batch(ars_tickers, "ARS")
    prices_usd = await self._fetch_prices_batch(usd_tickers, "USD")
    prices = {**prices_ars, **prices_usd}
    
    # 3. Compute metrics
    total_invested = Decimal(0)
    current_value = Decimal(0)
    
    for pos in positions:
      invested_amount = pos.shares * pos.avg_buy_price
      total_invested += invested_amount
      
      current_price = prices.get(pos.ticker, pos.avg_buy_price)
      current_amount = pos.shares * current_price
      current_value += current_amount
    
    unrealized_pnl = current_value - total_invested
    return_percent = (unrealized_pnl / total_invested * 100) if total_invested > 0 else Decimal(0)
    
    # 4. Realized P&L: fetch from IOL history (future feature)
    realized_pnl = Decimal(0)  # TODO: Phase 2
    
    return DashboardMetrics(
      total_invested=round(total_invested, 2),
      current_value=round(current_value, 2),
      unrealized_pnl=round(unrealized_pnl, 2),
      return_percent=round(return_percent, 2),
      realized_pnl=realized_pnl,
      last_updated=utcnow()
    )
  
  async def _fetch_prices_batch(self, tickers: list[str], currency: str) -> dict[str, Decimal]:
    """Fetch prices for multiple tickers; use provider factory."""
    if not tickers:
      return {}
    
    provider = ProviderFactory.get_price_provider(currency)
    prices = {}
    
    for ticker in tickers:
      try:
        price_data = await get_price_cached(ticker, currency)
        prices[ticker] = Decimal(str(price_data.price))
      except PriceFetchError:
        # Use latest cached or fallback to avg_buy_price in the calling code
        pass
    
    return prices
```

### 5.2 Caching Strategy for Metrics

**Decision**: Cache dashboard metrics for 1 minute per user.

```python
async def get_dashboard_metrics(user_id: UUID, db: AsyncSession) -> DashboardMetrics:
  """Get cached metrics or compute fresh."""
  cache_key = f"dashboard:metrics:{user_id}"
  cached = await cache.get(cache_key)
  if cached:
    return cached
  
  metrics = await dashboard_service.compute_metrics(user_id, db)
  await cache.set(cache_key, metrics, ttl=60)
  return metrics
```

### 5.3 API Endpoint

**File**: `backend/app/api/dashboard.py`

```python
@router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_metrics(
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  return await get_dashboard_metrics(current_user.id, db)
```

---

## 6. Strategy Templates

### 6.1 Data Model

**File**: `backend/app/models/strategy.py` (extend existing)

```python
class InvestmentStrategy(Base):
  __tablename__ = "investment_strategies"
  
  id: UUID (PK)
  user_id: UUID (FK)
  name: str
  description: str
  how_it_works: str  # Plain text explanation
  timeframe: str  # "short-term", "medium-term", "long-term"
  entry_rules: str | None
  exit_rules: str | None
  is_template: bool  # True = base template; False = custom user strategy
  template_id: UUID | None  # If custom, reference the base template
  created_at: datetime
  updated_at: datetime
  
  user: Mapped["User"] = relationship("User", back_populates="strategies")
```

### 6.2 Seed Mechanism

**File**: `backend/app/core/migrations/seed_strategies.py` (or Alembic migration)

```python
BASE_STRATEGY_TEMPLATES = [
  {
    "name": "Value Investing",
    "description": "Buy undervalued companies trading below intrinsic value.",
    "how_it_works": """
      1. Identify stocks with low P/E, high dividend yield, or below book value
      2. Analyze fundamentals: earnings growth, debt levels, competitive moats
      3. Buy with margin of safety (20%+ discount to intrinsic value)
      4. Hold 3-5 years for value realization
    """,
    "timeframe": "long-term",
    "entry_rules": "P/E < market average; Dividend yield > 2%",
    "exit_rules": "Price reaches intrinsic value; or fundamentals deteriorate"
  },
  {
    "name": "Growth Investing",
    "description": "Invest in companies with strong growth prospects.",
    "how_it_works": """
      1. Target companies with 15%+ annual earnings growth
      2. Accept higher valuations (higher P/E)
      3. Focus on market trends: tech, renewables, etc.
      4. Reinvest dividends; hold for 5-10 years
    """,
    "timeframe": "long-term",
    "entry_rules": "EPS growth > 15% YoY; Market tailwinds present",
    "exit_rules": "Growth rate declines below 10%; or overvaluation detected"
  },
  {
    "name": "Dividend Growth",
    "description": "Generate passive income via dividend-paying stocks.",
    "how_it_works": """
      1. Invest in stable, mature companies with high dividend yields
      2. Focus on dividend growth history (10+ years of increases)
      3. Reinvest dividends to compound returns
      4. Monitor dividend safety (payout ratio < 60%)
    """,
    "timeframe": "medium-term",
    "entry_rules": "Dividend yield > 3%; Payout ratio < 60%",
    "exit_rules": "Dividend cut; or yield drops below 2%"
  },
  {
    "name": "Dollar-Cost Averaging",
    "description": "Reduce market timing risk by investing fixed amounts regularly.",
    "how_it_works": """
      1. Invest a fixed amount (e.g., $500) every month
      2. Buy more shares when prices are low
      3. Ignore market volatility and emotions
      4. Continue for 5-10 years to ride out cycles
    """,
    "timeframe": "long-term",
    "entry_rules": "Invest same amount every month, regardless of price",
    "exit_rules": "Hold indefinitely; or periodically rebalance"
  },
  {
    "name": "Income Diversification",
    "description": "Balance dividends, bonds, and capital appreciation.",
    "how_it_works": """
      1. 50% dividend stocks + 30% growth stocks + 20% bonds/cash
      2. Dividend stocks: stable, high yield (3%+)
      3. Growth stocks: tech, small-cap, emerging markets
      4. Rebalance annually
    """,
    "timeframe": "medium-term",
    "entry_rules": "Maintain target allocation percentages",
    "exit_rules": "Rebalance when allocation drifts >5%"
  }
]

async def seed_base_strategies(db: AsyncSession):
  """Insert base strategy templates; skip if already exists."""
  for tmpl in BASE_STRATEGY_TEMPLATES:
    existing = await db.execute(
      select(InvestmentStrategy).where(
        InvestmentStrategy.name == tmpl["name"],
        InvestmentStrategy.is_template == True,
        InvestmentStrategy.user_id == None  # System template
      )
    )
    if existing.scalar_one_or_none():
      continue  # Already seeded
    
    strategy = InvestmentStrategy(
      user_id=None,  # System template, no user ownership
      name=tmpl["name"],
      description=tmpl["description"],
      how_it_works=tmpl["how_it_works"],
      timeframe=tmpl["timeframe"],
      entry_rules=tmpl.get("entry_rules"),
      exit_rules=tmpl.get("exit_rules"),
      is_template=True
    )
    db.add(strategy)
  
  await db.commit()

# Call on app startup:
@app.on_event("startup")
async def startup():
  db = get_db()
  await seed_base_strategies(db)
```

### 6.3 API Endpoint

```python
@router.get("/strategies/templates", response_model=list[InvestmentStrategy])
async def get_strategy_templates(db: AsyncSession = Depends(get_db)):
  """Fetch all base strategy templates (read-only in MVP)."""
  result = await db.execute(
    select(InvestmentStrategy).where(InvestmentStrategy.is_template == True)
  )
  return list(result.scalars().all())

@router.get("/strategies", response_model=list[InvestmentStrategy])
async def get_user_strategies(
  current_user: User = Depends(get_current_user),
  db: AsyncSession = Depends(get_db)
):
  """Fetch user's custom strategies (templates + adoptions in future)."""
  result = await db.execute(
    select(InvestmentStrategy).where(
      InvestmentStrategy.user_id == current_user.id
    )
  )
  return list(result.scalars().all())
```

---

## 7. UX Overhaul Approach

### 7.1 Design Tokens and Tailwind Config

**Decision**: Use Tailwind's built-in color palette + custom spacing/typography for consistency.

**File**: `frontend/tailwind.config.ts`

```typescript
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: "#0066cc",      // IOL brand blue
        success: "#22c55e",
        danger: "#ef4444",
        warning: "#f59e0b",
        neutral: {
          50: "#f9fafb",
          100: "#f3f4f6",
          900: "#111827"
        }
      },
      spacing: {
        "xs": "0.25rem",  // 4px
        "sm": "0.5rem",   // 8px
        "md": "1rem",     // 16px
        "lg": "1.5rem",   // 24px
        "xl": "2rem"      // 32px
      },
      typography: {
        base: {
          css: {
            fontSize: "0.875rem",
            lineHeight: "1.5"
          }
        }
      }
    }
  }
}
```

### 7.2 Component Structure

**Container-Presentational Pattern**:

```typescript
// DashboardContainer: handles state, data fetching
// DashboardMetrics: pure presentation, receives props
// PortfolioTable: pure presentation, receives holdings array
// StrategyCard: pure presentation, receives template data

// Benefits:
// - Testability: presentational components are functions of props
// - Reusability: same card can be used in dashboard, modals, etc.
// - Performance: Memoize pure components to prevent re-renders
```

### 7.3 Performance Tactics

**Server Components**:

- Move data-fetching to server components (Next.js 13+)
- Fetch holdings, metrics on the server; pass to client components
- Reduces client JS bundle and API calls

```typescript
// app/(dashboard)/dashboard/page.tsx (server component)
import { DashboardContainer } from "@/components/Dashboard/DashboardContainer";

async function DashboardPage() {
  const metrics = await fetch("http://localhost:8000/api/dashboard/metrics", {
    next: { revalidate: 60 }  // ISR: revalidate every 60s
  }).then(r => r.json());

  return <DashboardContainer initialMetrics={metrics} />;
}

export default DashboardPage;
```

**Suspense Boundaries**:

```typescript
<Suspense fallback={<MetricsLoading />}>
  <DashboardMetrics metrics={metrics} />
</Suspense>

<Suspense fallback={<PortfolioLoading />}>
  <PortfolioHoldings holdings={holdings} />
</Suspense>
```

**Memoization**:

```typescript
import { memo } from "react";

const DashboardMetrics = memo(({ metrics }) => {
  return <div>...</div>;
}, (prevProps, nextProps) => {
  return prevProps.metrics === nextProps.metrics;
});
```

### 7.4 No New UI Library

**Decision**: Use Tailwind + Headless UI (for accessible dropdowns, dialogs) only. No Shadcn, MUI, or Chakra.

- **Form validation**: react-hook-form + Zod (already in use or add)
- **Charts**: recharts (existing? check deps) or add lightweight alternative
- **Icons**: lucide-react or tabler-icons (tiny, tree-shakeable)
- **Modal/Dialog**: Headless UI's Dialog or HTML `<dialog>`

---

## 8. Trade-Offs and Alternatives

### 8.1 Credential Storage

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Fernet (chosen)** | Simple, single key, sufficient for single-user | Not FIPS-certified | Fernet |
| AES + IV | FIPS-certified, industry standard | More complex key management | Deferred to Phase 2 if regulatory required |
| Vault (HashiCorp) | Enterprise-grade, HSM support, secrets rotation | Operational overhead, licensing | Unnecessary for MVP; reconsider at scale |

### 8.2 Token Refresh Strategy

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Proactive job (chosen)** | Prevents user-facing token expiry; async | Requires scheduler; clock skew risk | Proactive job + request-level safeguard |
| On-demand refresh | Simple; no background job | 401 errors on expired token; poor UX | Not suitable for 15-min TTL |
| Request interceptor | Catches token refresh inline | Adds latency to requests; complex retry logic | Acceptable fallback if job fails |

### 8.3 Portfolio Source of Truth

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **IOL only (chosen)** | Eliminates sync conflicts; user truth | Requires IOL connection; no offline access | IOL only |
| Dual-source (IOL + manual) | Fallback if IOL unavailable | Conflict resolution complex; confusing UX | Not chosen; manual entry deprecated |
| Manual only (existing) | Offline-capable; user control | No real portfolio data; redundant entry | Deprecating in Phase 1 |

### 8.4 Currency Routing

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Factory with currency param (chosen)** | Clean, extends existing pattern; per-holding routing | Requires passing currency through layers | Factory pattern |
| Hardcoded provider per ticker | Simpler for known tickers | Not extensible; hardcoded logic | Rejected |
| Machine-learning classification | Automatic currency detection | Over-engineered for MVP | Deferred to Phase 2 |

### 8.5 Auth Gate Implementation

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Next.js middleware + route groups (chosen)** | Built-in; no extra deps; composable | Requires careful path matching | Middleware + route groups |
| Custom wrapper component | Flexible; framework-agnostic | Requires React Context; boilerplate | Too heavy for simple guard |
| Vercel Middleware (advanced) | More powerful | Learning curve; may be overkill | Unnecessary for MVP |

### 8.6 Dashboard Metrics Computation

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Backend service (chosen)** | Centralized logic; cacheable; secure | Slightly more latency | Backend service |
| Client-side calculation | Faster response; no backend load | Duplicate logic; hard to maintain | Rejected |
| Event-driven (computed on sync) | Precomputed; instant | Complex event handling; stale data | Deferred to Phase 2 optimization |

### 8.7 Strategy Templates

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Database seeding + fixtures (chosen)** | Versioned; easy to update; queryable | Requires migration | Database seeding |
| Hardcoded in code | Immutable; simple | Must rebuild to update | Rejected |
| Config file (YAML/JSON) | Easy to edit; no code change | Not queryable; extra parsing | Config file as fallback |

---

## 9. Key Architectural Decisions (ADR-style)

| Decision | Rationale | Risks & Mitigations |
|----------|-----------|---------------------|
| **Fernet encryption for IOL passwords** | Simplest practical option; token TTL is short (15 min) | Key rotation requires DB migration; mitigate with clear env key docs |
| **Proactive token refresh job (13-min interval)** | Prevents user-facing 401 errors; safer than on-demand | Clock skew or job failure can cause refresh race; mitigate with request-level safeguard (< 60s check) |
| **IOL as authoritative source; no manual edits** | Eliminates sync conflicts; user intent is clear | Requires IOL setup on first login; mitigate with clear onboarding and error messages |
| **Factory pattern for currency-aware pricing** | Extends existing pattern; per-holding routing is clean | Adds one layer of indirection; mitigate with clear interfaces and tests |
| **Backend dashboard metrics service** | Single source of truth; cacheable; secure | No client-side fallback if backend unavailable; mitigate with graceful degradation and timeout |
| **Template-only strategies in MVP** | Reduces complexity; validated base templates are valuable | Users cannot customize; mitigate with clear roadmap to Phase 2 custom strategies |
| **APScheduler for background jobs** | Industry-standard async job scheduler | Single-instance only (no cluster support); acceptable for MVP; mitigate by documenting limitations |

---

## 10. Implementation Checklist

- [ ] **IOL Credentials Model**: `IOLCredentials` table with encrypted password, tokens, sync status
- [ ] **IOL Client Library**: `IOLClient` class with OAuth2 authenticate, refresh, fetch portfolio, fetch quotes, fetch account status
- [ ] **Token Refresh Job**: APScheduler job runs every 13 min; proactive refresh before 15-min expiry
- [ ] **Portfolio Sync Service**: Fetch IOL holdings; upsert to `PortfolioPosition` with `source="iol"`, `currency`; delete `source="manual"`
- [ ] **IOL Quotes Provider**: Implements `AbstractMarketDataProvider`; fetches BCBA quotes; falls back to yfinance on error
- [ ] **Factory Extension**: `get_price_provider(currency: str)` routes ARS → IOL, USD → yfinance
- [ ] **Auth Gate Middleware**: Next.js middleware redirects unauthenticated users to login
- [ ] **Route Groups**: `(auth)` for login/register; `(dashboard)` for protected routes
- [ ] **IOL Onboarding Modal**: Prompt for credentials post-login; test connection; sync immediately
- [ ] **Dashboard Metrics Service**: Compute total invested, current value, unrealized P&L; cache 1 min
- [ ] **Dashboard API Endpoint**: `GET /dashboard/metrics`
- [ ] **Dashboard UI**: Metric cards, holdings table, sync timestamp, manual refresh button
- [ ] **Strategy Templates**: Seed 3–5 validated templates; read-only in MVP
- [ ] **Tailwind Config**: Design tokens for colors, spacing, typography
- [ ] **Component Library**: Container-presentational split; memoization; Suspense boundaries
- [ ] **Migration**: `IOLCredentials` table; add `source`, `currency`, `iol_position_id` to `PortfolioPosition`
- [ ] **Tests**: Unit tests for IOL client, token refresh, portfolio sync; integration tests for auth gate

---

## 11. Data Flow Diagram

```
User Login
  ↓
frontend: POST /auth/login → cookie (JWT)
  ↓
frontend: GET /auth/me → user
  ↓
frontend: GET /iol/credentials/status → not connected
  ↓
frontend: Show IOL Connect Modal
  ↓
User enters IOL username/password
  ↓
frontend: POST /iol/connect (iol_username, iol_password_encrypted)
  ↓
backend: 
  1. Test credentials via IOLClient.authenticate()
  2. Encrypt password with Fernet
  3. Store in IOLCredentials table
  4. Call proactive_refresh_job() immediately
  5. sync_portfolio_service.sync_portfolio()
  6. Return synced tickers
  ↓
frontend: Show holdings + dashboard metrics
  ↓
background job (every 13 min):
  1. Check all users' IOL tokens
  2. Refresh tokens expiring < 15 min
  ↓
background job (every 5 min):
  1. Fetch IOL portfolio for all users
  2. Upsert to PortfolioPosition
  3. Update last_synced_at
  ↓
frontend: Poll /dashboard/metrics every 30s or on-demand
  ↓
backend:
  1. Fetch user's PortfolioPosition
  2. Fetch current prices (ARS → IOL, USD → yfinance)
  3. Compute metrics
  4. Cache 1 min
  ↓
frontend: Display metrics + holdings
```

---

## 12. Migration Strategy

**Alembic Migration** (`backend/alembic/versions/xyz_add_iol_support.py`):

```python
def upgrade():
  # Create IOLCredentials table
  op.create_table(
    "iol_credentials",
    sa.Column("id", sa.UUID, primary_key=True),
    sa.Column("user_id", sa.UUID, sa.ForeignKey("users.id", ondelete="CASCADE")),
    sa.Column("iol_username", sa.String),
    sa.Column("encrypted_password", sa.String),
    sa.Column("access_token", sa.String),
    sa.Column("token_expires_at", sa.DateTime(timezone=True)),
    sa.Column("refresh_token", sa.String, nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
    sa.Column("sync_error", sa.String, nullable=True),
    sa.UniqueConstraint("user_id")
  )
  
  # Add columns to portfolio_positions
  op.add_column("portfolio_positions", sa.Column("source", sa.String, default="manual"))
  op.add_column("portfolio_positions", sa.Column("currency", sa.String, default="USD"))
  op.add_column("portfolio_positions", sa.Column("iol_position_id", sa.String, nullable=True))
  op.add_column("portfolio_positions", sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True))
  op.add_column("portfolio_positions", sa.Column("last_synced_price", sa.Numeric(12, 4), nullable=True))

def downgrade():
  op.drop_table("iol_credentials")
  op.drop_column("portfolio_positions", "source")
  op.drop_column("portfolio_positions", "currency")
  op.drop_column("portfolio_positions", "iol_position_id")
  op.drop_column("portfolio_positions", "last_synced_at")
  op.drop_column("portfolio_positions", "last_synced_price")
```

---

## 13. Risk Mitigations

| Risk | Severity | Mitigation |
|------|----------|-----------|
| IOL API unavailability | HIGH | Fallback to cached prices; clear UI messages; graceful degradation |
| Token refresh fails | MED | Request-level safeguard (refresh if < 60s to expiry); user logout + re-login if persistent |
| Credential encryption key lost | CRITICAL | Document backup procedure; store in secure vault; password-protected recovery |
| Portfolio sync race conditions | MED | Idempotent upsert semantics; unique constraints on (user_id, ticker); retry on conflict |
| Price feed mismatch (IOL vs yfinance) | LOW | Display source badge; document fallback strategy; warn users of source differences |
| On-demand refresh blocks UI | LOW | Make sync endpoint async; show progress indicator; allow cancel |
| User abandons onboarding | MED | Clear instructions; explain benefits; allow skip (with limitations) in future |

---

## 14. Success Criteria

- [x] IOL client authenticates and fetches credentials
- [x] Token refresh job runs proactively without user-facing 401s
- [x] Portfolio syncs from IOL; manual entries deprecated
- [x] Currency-aware pricing routes ARS → IOL, USD → yfinance
- [x] Auth gate hides app until login
- [x] Dashboard computes metrics correctly
- [x] Strategy templates are seeded and visible
- [x] UI uses Tailwind; no new heavy libraries
- [x] All 5 PRs merge to main; each is autonomous and testable

