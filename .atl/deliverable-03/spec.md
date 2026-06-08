# Spec: Data Ingestion Layer (Deliverable 3)

## Intent
Build an extensible provider-based data ingestion system that fetches financial data from 4 external sources, caches responses in Redis with configurable TTLs, normalizes data to a common format, and triggers background ingestion when the user's portfolio changes.

## Requirements

### R1 — Abstract Provider Interface
**R1.1** `AbstractMarketDataProvider` ABC with async methods: `fetch_price(ticker)`, `fetch_fundamentals(ticker)`, `fetch_dividends(ticker)`, `fetch_company_info(ticker)`.
**R1.2** Each method returns a typed dataclass/Pydantic model, not a raw dict.
**R1.3** Providers declare their name, rate limits, and capabilities via class attributes.

### R2 — Four Provider Implementations
**R2.1** **YFinanceProvider** — prices (daily OHLCV), fundamentals (P/E, P/B, market cap, sector), dividends (history, yield).
**R2.2** **FinnhubProvider** — earnings surprises, insider transactions, analyst ratings. Rate limit: 60/min.
**R2.3** **AlphaVantageProvider** — technical indicators (RSI, MACD, EMA, SMA). Rate limit: 25/day free tier. Feature-flagged (disabled by default).
**R2.4** **NewsAPIProvider** — news headlines by ticker and sector. Rate limit: 100/day free tier.

### R3 — Redis Caching Layer
**R3.1** Cache all external API responses in Redis with TTLs:
- Prices: 15 minutes
- Fundamentals: 6 hours
- News: 30 minutes
- Analyst ratings / insider: 24 hours
**R3.2** Cache key format: `{provider}:{method}:{ticker}`.
**R3.3** Never call an external API if a valid cached response exists.
**R3.4** Cached responses include `source_timestamp` and `cache_expires_at`.

### R4 — Data Normalizer
**R4.1** Normalize raw provider responses to common Pydantic models (`NormalizedPriceData`, `NormalizedFundamental`).
**R4.2** Standardize ticker format (uppercase), decimal precision, date formats.
**R4.3** Attach source provider name and fetch timestamp to every data point.

### R5 — Background Ingestion on Portfolio Save
**R5.1** When a position is created or updated, trigger async ingestion for that ticker.
**R5.2** Ingestion fetches price + fundamentals (core data). Technical and news are optional.
**R5.3** Failed ingestion for one ticker must not block other tickers or the portfolio save.

### R6 — Manual Ingestion Endpoint
**R6.1** `POST /ingestion/trigger` — ingests data for all tickers in the user's portfolio.
**R6.2** `POST /ingestion/trigger/{ticker}` — ingests data for a single ticker.
**R6.3** Returns ingestion summary: successes, failures per ticker.

### R7 — Environment & Feature Flags
**R7.1** Alpha Vantage and Finnhub disabled unless API keys are provided in `.env`.
**R7.2** yfinance and NewsAPI free tier work without API keys.

## Scenarios

### S1: Fetch price with cache hit
```
GIVEN AAPL price data cached in Redis (5 min ago, TTL 15 min)
WHEN ingestion is triggered for AAPL
THEN cached data is returned without calling the external API
```

### S2: Fetch price with cache miss
```
GIVEN no cached data for AAPL
WHEN ingestion is triggered
THEN yfinance is called, response cached in Redis with TTL 15 min
```

### S3: Portfolio save triggers ingestion
```
GIVEN user creates a position with ticker NVDA
WHEN POST /portfolio/positions returns 201
THEN background ingestion fetches NVDA price + fundamentals (non-blocking)
```

### S4: Provider fails gracefully
```
GIVEN Finnhub API key is missing or invalid
WHEN ingestion tries to fetch analyst ratings
THEN Finnhub provider is skipped, other providers continue, no error returned to user
```

### S5: Manual ingestion
```
GIVEN user has portfolio with AAPL, MSFT, GOOGL
WHEN POST /ingestion/trigger
THEN all 3 tickers are ingested, summary returned with per-ticker status
```

### S6: Rate limit handling
```
GIVEN Alpha Vantage has been called 25 times today
WHEN another call is attempted
THEN provider returns cached or empty response with status="rate_limited"
```
