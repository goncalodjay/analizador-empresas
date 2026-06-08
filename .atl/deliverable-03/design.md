# Design: Data Ingestion Layer (Deliverable 3)

## Technical Approach

Deliverable 3 builds the data pipeline that feeds all subsequent analysis features. It uses the Strategy pattern: an abstract provider interface (`AbstractMarketDataProvider`) with 4 concrete implementations, a Redis-backed cache decorator that wraps providers transparently, a normalizer that maps raw responses to consistent domain models, and an ingestion service that orchestrates fetch → cache → normalize → persist.

## Architecture

```
api/ingestion.py
        │
        ▼
services/ingestion_service.py     ← orchestrator
        │
        ├──▶ services/cache_service.py     ← Redis TTL cache
        │
        └──▶ providers/
              ├── base.py                  ← AbstractMarketDataProvider
              ├── yfinance_provider.py     
              ├── finnhub_provider.py      
              ├── alphavantage_provider.py 
              ├── newsapi_provider.py      
              └── factory.py               ← ProviderFactory
                    │
                    ▼
              schemas/ingestion.py         ← Normalized DTOs
```

## Provider Interface

```python
# providers/base.py
class AbstractMarketDataProvider(ABC):
    name: str                          # "yfinance", "finnhub", etc.
    rate_limit_per_minute: int | None  # None = no limit
    requires_api_key: bool

    @abstractmethod
    async def fetch_price(self, ticker: str) -> NormalizedPriceData: ...
    @abstractmethod
    async def fetch_fundamentals(self, ticker: str) -> NormalizedFundamentals: ...
    @abstractmethod
    async def fetch_dividends(self, ticker: str) -> list[NormalizedDividend]: ...
    @abstractmethod
    async def fetch_company_info(self, ticker: str) -> NormalizedCompanyInfo: ...
```

## Normalized Data Models (schemas/ingestion.py)

```python
class NormalizedPriceData(BaseModel):
    ticker: str
    date: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    source: str           # "yfinance"
    fetched_at: datetime

class NormalizedFundamentals(BaseModel):
    ticker: str
    pe_ratio: Decimal | None
    pb_ratio: Decimal | None
    market_cap: int | None
    sector: str | None
    industry: str | None
    beta: Decimal | None
    eps: Decimal | None
    source: str
    fetched_at: datetime

class NormalizedDividend(BaseModel):
    ticker: str
    ex_date: date
    amount: Decimal
    yield_pct: Decimal | None
    source: str
    fetched_at: datetime

class NormalizedCompanyInfo(BaseModel):
    ticker: str
    name: str
    sector: str | None
    industry: str | None
    country: str | None
    employees: int | None
    description: str | None
    source: str
    fetched_at: datetime
```

## Cache Service

```python
# services/cache_service.py
CACHE_TTLS = {
    "price": 900,             # 15 min
    "fundamentals": 21600,    # 6 hours
    "dividends": 21600,       # 6 hours
    "company_info": 86400,    # 24 hours
    "analyst_ratings": 86400, # 24 hours
    "insider": 86400,         # 24 hours
    "earnings": 86400,        # 24 hours
    "news": 1800,             # 30 min
    "technical": 900,         # 15 min
}

class CacheService:
    async def get(self, key: str) -> dict | None: ...
    async def set(self, key: str, value: dict, ttl: int): ...
    async def delete(self, key: str): ...
    def build_key(provider: str, method: str, ticker: str) -> str: ...
```

## Ingestion Service

```python
# services/ingestion_service.py
class IngestionService:
    async def ingest_ticker(self, ticker: str, user_id: str) -> IngestionResult: ...
    async def ingest_portfolio(self, user_id: str) -> list[IngestionResult]: ...
    async def ingest_all_tickers(self, tickers: list[str], user_id: str) -> list[IngestionResult]: ...

class IngestionResult(BaseModel):
    ticker: str
    price: bool          # success/fail
    fundamentals: bool
    source: str
    cached: bool         # was cache hit?
    error: str | None
```

## Provider Factory

```python
# providers/factory.py
class ProviderFactory:
    @staticmethod
    def get_price_provider() -> AbstractMarketDataProvider:  # yfinance (always available)
    @staticmethod
    def get_fundamentals_provider() -> AbstractMarketDataProvider:  # yfinance
    @staticmethod
    def get_analyst_provider() -> AbstractMarketDataProvider | None:  # Finnhub (if key)
    @staticmethod
    def get_technical_provider() -> AbstractMarketDataProvider | None:  # Alpha Vantage (if key)
    @staticmethod
    def get_news_provider() -> AbstractMarketDataProvider | None:  # NewsAPI (if key)
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/ingestion/trigger` | Yes | Ingest all portfolio tickers |
| POST | `/ingestion/trigger/{ticker}` | Yes | Ingest single ticker |
| GET | `/ingestion/status/{ticker}` | Yes | Check cache freshness for a ticker |

## Config (.env additions)

```env
ALPHA_VANTAGE_API_KEY=     # optional
FINNHUB_API_KEY=           # optional
NEWSAPI_API_KEY=           # optional
```

## Dependencies

Add to `requirements.txt`:
- `yfinance>=0.2.40`
- `finnhub-python>=2.4.22`
- `alpha-vantage>=2.3.1` (or direct HTTP)

## Directory Structure

```
backend/app/
├── providers/
│   ├── __init__.py
│   ├── base.py
│   ├── yfinance_provider.py
│   ├── finnhub_provider.py
│   ├── alphavantage_provider.py
│   ├── newsapi_provider.py
│   └── factory.py
├── schemas/
│   └── ingestion.py        # New: NormalizedPriceData, etc.
├── services/
│   ├── cache_service.py     # New: Redis caching
│   └── ingestion_service.py # New: Orchestrator
├── api/
│   └── ingestion.py         # New: Ingestion endpoints
└── main.py                  # Modified: wire ingestion router
```

## Review Workload Forecast

| Layer | Files | Est. Lines |
|-------|-------|-----------|
| Provider base + 4 impls | 6 | ~500 |
| Cache service | 1 | ~80 |
| Ingestion models | 1 | ~100 |
| Ingestion service | 1 | ~120 |
| Ingestion API | 1 | ~60 |
| Config + factory | 2 | ~80 |
| Tests | 4 | ~350 |
| **Total** | **16 files** | **~1,290 lines** |

> Risk: HIGH — exceeds 400-line budget. Split into 3 chained PRs:
> - **PR 5a:** Provider base + yfinance + cache (~350 lines)
> - **PR 5b:** Finnhub + Alpha Vantage + NewsAPI + factory (~380 lines)
> - **PR 5c:** Ingestion service + API + tests (~560 lines)
