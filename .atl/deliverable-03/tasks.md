# Tasks: Data Ingestion Layer (Deliverable 3)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1,290 |
| 400-line budget risk | HIGH |
| Chained PRs required | Yes |
| Delivery strategy | PR 5a (Provider base + yfinance + cache) → PR 5b (Finnhub + AlphaVantage + NewsAPI + factory) → PR 5c (Ingestion service + API + tests) |

---

## PR 5a: Provider Base + YFinance + Cache (~350 lines)

### Task 5a.1 — Ingestion data models
**Files:** `schemas/ingestion.py`
- `NormalizedPriceData` (ticker, date, OHLCV, source, fetched_at)
- `NormalizedFundamentals` (P/E, P/B, market cap, sector, beta, EPS)
- `NormalizedDividend` (ex_date, amount, yield_pct)
- `NormalizedCompanyInfo` (name, sector, country, description)
- `IngestionResult`, `CacheStatus`
- **Verification:** model instantiation tests

### Task 5a.2 — Abstract provider base
**Files:** `providers/__init__.py`, `providers/base.py`
- `AbstractMarketDataProvider` ABC with async methods
- Class attrs: `name`, `rate_limit_per_minute`, `requires_api_key`
- Each method returns appropriate Normalized model
- **Verification:** ABC cannot be instantiated

### Task 5a.3 — YFinance provider
**Files:** `providers/yfinance_provider.py`
- `fetch_price(ticker)` → `NormalizedPriceData` using `yfinance.Ticker`
- `fetch_fundamentals(ticker)` → `NormalizedFundamentals`
- `fetch_dividends(ticker)` → `list[NormalizedDividend]`
- `fetch_company_info(ticker)` → `NormalizedCompanyInfo`
- Add `yfinance` to requirements.txt
- **Verification:** mock-based unit tests

### Task 5a.4 — Redis cache service
**Files:** `services/cache_service.py`
- `CacheService` class with async get/set/delete
- TTL mapping dict
- Cache key builder: `{provider}:{method}:{ticker}`
- JSON serialization for Redis storage
- **Verification:** integration test with redis or mock

---

## PR 5b: Finnhub + AlphaVantage + NewsAPI + Factory (~380 lines)

### Task 5b.1 — Finnhub provider
**Files:** `providers/finnhub_provider.py`
- `fetch_analyst_ratings(ticker)` — analyst consensus
- `fetch_insider_transactions(ticker)` — insider activity
- `fetch_earnings_surprises(ticker)` — earnings vs estimates
- Rate limit handling: 60 calls/min
- Feature-flagged: disabled without API key
- Add `finnhub-python` to requirements.txt
- **Verification:** mock-based tests

### Task 5b.2 — Alpha Vantage provider
**Files:** `providers/alphavantage_provider.py`
- `fetch_rsi(ticker)`, `fetch_macd(ticker)`, `fetch_ema(ticker)`
- Rate limit handling: 25 calls/day free tier
- Feature-flagged: disabled without API key
- **Verification:** mock-based tests

### Task 5b.3 — NewsAPI provider
**Files:** `providers/newsapi_provider.py`
- `fetch_news(ticker, limit=10)` — headlines for ticker
- `fetch_sector_news(sector, limit=10)` — sector news
- Rate limit handling: 100 calls/day free tier
- Feature-flagged: disabled without API key
- **Verification:** mock-based tests

### Task 5b.4 — Provider factory
**Files:** `providers/factory.py`
- `ProviderFactory` static methods returning appropriate providers
- Feature flag checks (API key presence in settings)
- Graceful degradation: return None if disabled
- **Verification:** factory returns correct provider types

---

## PR 5c: Ingestion Service + API + Tests (~560 lines)

### Task 5c.1 — Ingestion service
**Files:** `services/ingestion_service.py`
- `ingest_ticker(ticker, user_id)` — fetch price + fundamentals, cache, return result
- `ingest_portfolio(user_id)` — fetch all user portfolio tickers
- Non-blocking: failed provider doesn't break ingestion
- Background trigger: callable from portfolio save
- **Verification:** integration test with mock providers

### Task 5c.2 — Portfolio save trigger
**Files:** `api/portfolio.py` (modify), `api/watchlists.py` (modify)
- After `create_position` and `update_position`, fire background ingestion
- `asyncio.create_task(ingestion_service.ingest_ticker(...))`
- Does not block the HTTP response
- **Verification:** integration test confirms trigger fires

### Task 5c.3 — Ingestion API endpoints
**Files:** `api/ingestion.py` + wire in `main.py`
- `POST /ingestion/trigger` — ingest all portfolio tickers
- `POST /ingestion/trigger/{ticker}` — ingest single ticker
- `GET /ingestion/status/{ticker}` — check cache freshness
- All require auth via `get_current_user`
- **Verification:** integration test with test client

### Task 5c.4 — Config additions
**Files:** `core/config.py` (modify), `.env.example` (modify)
- `ALPHA_VANTAGE_API_KEY: str = ""`
- `FINNHUB_API_KEY: str = ""`
- `NEWSAPI_API_KEY: str = ""`
- All optional, empty string = disabled
- **Verification:** config loads with/without keys

### Task 5c.5 — Integration tests
**Files:** `tests/test_ingestion.py`, `tests/conftest.py` (modify)
- Test yfinance provider with mocks
- Test cache service hit/miss
- Test ingestion service orchestrates correctly
- Test ingestion API endpoints with auth
- Test feature flag behavior (providers disabled without keys)
- Test background trigger on portfolio save
- **Verification:** pytest passes all tests
