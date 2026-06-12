# Spec: Currency-Aware Pricing (ARS/USD)

**Capability**: currency-aware-pricing  
**Status**: Pending Implementation  
**Scope**: Price source selection by currency (ARS via IOL BCBA quotes, USD via yfinance), price source indicator in UI, fallback strategy, applies to analysis page and dashboard  
**Out of Scope**: Real-time price subscriptions, technical analysis, charting beyond existing integrations, currency conversion  

---

## Delta Requirements

### DeltaR1: Currency-Based Price Provider Selection
**Requirement**: The price factory MUST route price requests based on the holding's currency: ARS holdings use IOL BCBA quotes as the primary source with yfinance as fallback; USD holdings use yfinance directly. The selection is transparent to the caller; the price factory handles routing internally.

**Rationale**: IOL BCBA quotes are accurate for ARS CEDEARs listed on the Buenos Aires Exchange. yfinance covers USD ADRs and international symbols. Using the correct source per currency reduces pricing errors and P&L miscalculation.

**Acceptance Criteria**:
- Price factory implementation includes a `get_price(ticker, currency)` method
- For ARS holdings:
  - Primary: IOL GET /cotizaciones endpoint (BCBA quotes)
  - Fallback: yfinance (if IOL returns no quote or error)
- For USD holdings:
  - Use yfinance directly
- Factory returns a tuple: `(price, source, timestamp)` where source is `"iol"` or `"yfinance"`
- Caller can inspect the source and adjust display/calculations if needed (e.g., flag if source is fallback)

### DeltaR2: IOL BCBA Quotes Endpoint Integration
**Requirement**: The backend MUST integrate with IOL GET /cotizaciones endpoint to fetch real-time or near-real-time BCBA (Buenos Aires Exchange) quotes for ARS-denominated holdings. Quotes include bid, ask, and last trade price. The app uses the last trade price as the market price.

**Rationale**: BCBA quotes are the official price source for CEDEARs and local ARS stocks. This ensures accurate portfolio valuation for ARS holdings.

**Acceptance Criteria**:
- Backend implements `IOLQuoteProvider.get_price(tickers: list[str])` method
- Method calls IOL GET /cotizaciones with a list of tickers (e.g., GGAL, YPFD)
- IOL returns quote data:
  ```json
  {
    "GGAL": {
      "last_price": 250.50,
      "bid": 250.25,
      "ask": 250.75,
      "timestamp": "2026-06-12T17:45:00Z"
    }
  }
  ```
- Backend extracts the `last_price` and stores it in Redis cache with 1-minute TTL (BCBA updates every minute during trading hours)
- If IOL API returns no quote for a ticker (e.g., ticker not found on BCBA), the method returns `None` and falls back to yfinance

### DeltaR3: Price Source Indicator in UI
**Requirement**: The frontend MUST display a visual indicator showing which price source was used for each holding (IOL, yfinance, or stale). The indicator is shown next to the current price on the dashboard and analysis pages.

**Rationale**: Users need transparency about data quality. A fallback price from yfinance may differ from actual IOL quotes; displaying the source allows users to judge confidence in the price.

**Acceptance Criteria**:
- Dashboard portfolio table includes a "Price Source" column or badge next to each holding's current price
- Source badge displays:
  - "IOL" (green badge) if price is from IOL BCBA quotes
  - "yfinance" (blue badge) if price is from yfinance fallback
  - "Stale" (orange badge) if price is older than 60 minutes
- On hover (or in a tooltip), display the price timestamp and source
- Analysis page price display includes the same source indicator
- Source is determined by the `source` field in the price response from the factory

### DeltaR4: Fallback Strategy and Stale Price Handling
**Requirement**: If the primary price source (IOL for ARS, yfinance) fails or returns no quote, the app MUST fall back to the other source. If both sources fail or return stale data (>60 min old), the app MUST use the last cached price and mark it as "Stale".

**Rationale**: Market data is critical for P&L calculations; graceful degradation ensures the app remains usable even if one price source is temporarily down.

**Acceptance Criteria**:
- Price factory attempts primary source first; if it fails or times out (>5 sec), it logs the error and attempts fallback
- If both primary and fallback fail, the factory returns the last cached price (Redis key: `price:{ticker}:{currency}:last_known`)
- If no cached price exists, the factory returns `None` and the UI displays "Price Unavailable"
- Stale price (>60 min old) is marked with a "Stale" badge; calculation proceeds but the user is aware of data age
- Fallback attempts are logged (structured logging): `"Primary price source failed for GGAL (ARS); using fallback yfinance"`

### DeltaR5: Price Caching Strategy
**Requirement**: Prices from both IOL and yfinance MUST be cached to reduce API load and improve response time. Cache TTLs are: IOL BCBA quotes 1 minute (trading hours) / 5 minutes (after hours), yfinance 5 minutes, stale price threshold 60 minutes.

**Rationale**: Caching reduces external API calls during the day and ensures consistent pricing within a short window.

**Acceptance Criteria**:
- Price factory stores prices in Redis with the schema: `price:{ticker}:{currency}` = `{price, source, timestamp}`
- IOL BCBA quotes: 1-minute TTL during trading hours (09:00–17:00 ARS time), 5-minute TTL after hours
- yfinance: 5-minute TTL (always)
- Last-known price is stored with a longer TTL (24 hours) for fallback use
- Cache keys include a hash of the source (to distinguish IOL from yfinance) if both are cached
- Cache is warmed on app startup or via a scheduled job (e.g., every 5 minutes for top 10 holdings)

### DeltaR6: Applies to Analysis Page and Dashboard
**Requirement**: Currency-aware pricing MUST be applied to the analysis page (stock detail view) and the dashboard (portfolio summary). The analysis page shows the current market price with source indicator; the dashboard shows portfolio holdings with current price and total value per holding.

**Rationale**: Consistent pricing across all pages ensures users see a unified view of their portfolio and analysis.

**Acceptance Criteria**:
- Analysis page ([ticker] route):
  - Displays "Current Price: $X.XX (IOL)" or "Current Price: $X.XX (yfinance)"
  - Price is fetched from the price factory based on currency of the holding (if the user has that holding in their portfolio)
  - If the user does not have that holding, the page shows the USD price (yfinance default for US stocks)
- Dashboard portfolio table:
  - Each holding row includes: ticker, quantity, avg buy price, current price (with source badge), value (quantity × current price)
  - "Current Price" is fetched from the price factory based on the holding's currency
  - Source badge (IOL, yfinance, Stale) is displayed next to the price

---

## Implementation Notes

- **IOL Quote Request**: GET /cotizaciones expects a ticker list parameter (e.g., `?symbols=GGAL,YPFD,TXAR`); returns quote dict or empty for no quotes
- **Price Factory Pattern**: Extend existing `PriceProvider` abstract class with method `get_price(ticker: str, currency: str) -> (float, str, datetime)`
- **Redis Namespace**: Use prefix `price:` for all price keys to isolate from other cache data
- **Timeout Handling**: Set 5-second timeout on external API calls (IOL, yfinance); fail over to fallback if timeout occurs
- **Logging**: Log all fallback events with ticker, currency, reason, and source (e.g., "GGAL/ARS: IOL timeout (5s); falling back to yfinance")
- **Cache Warming**: On app startup, fetch prices for the user's top 5 holdings to pre-populate cache and reduce first-load latency
- **Currency Assumption**: Holdings always have a currency (ARS or USD); if currency is missing, default to USD and log a warning

---

## Database Schema Changes

No new tables; price data is cached in Redis only. Existing `price_history` table (if present) remains unchanged and continues to track historical prices for charting.

---

## Acceptance Scenarios

### Scenario 1: ARS Holding Uses IOL Quotes

**Given** a user has 50 GGAL shares (ARS currency)  
**When** the dashboard loads  
**Then** the price factory calls IOL GET /cotizaciones with ticker=GGAL  
**And** IOL returns: `{"GGAL": {"last_price": 250.50}}`  
**And** the dashboard displays: "Current Price: $250.50 (IOL)"  
**And** the source badge is "IOL" (green)  

---

### Scenario 2: USD Holding Uses yfinance

**Given** a user has 10 AAPL shares (USD currency)  
**When** the dashboard loads  
**Then** the price factory directly calls yfinance for AAPL (no IOL attempt)  
**And** yfinance returns: `AAPL = $150.30`  
**And** the dashboard displays: "Current Price: $150.30 (yfinance)"  
**And** the source badge is "yfinance" (blue)  

---

### Scenario 3: IOL Quote Fails, Fallback to yfinance

**Given** a user has 50 GGAL shares (ARS)  
**And** IOL API is unavailable  
**When** the dashboard loads  
**Then** the price factory calls IOL GET /cotizaciones and receives a 500 error  
**And** the price factory logs: "IOL quote failed for GGAL; falling back to yfinance"  
**And** the price factory calls yfinance for GGAL  
**And** yfinance returns: `GGAL = 248.00`  
**And** the dashboard displays: "Current Price: $248.00 (yfinance)"  
**And** the source badge is "yfinance" (blue, indicating fallback)  

---

### Scenario 4: Both Sources Fail, Use Cached Price

**Given** a user has 50 GGAL shares (ARS)  
**And** the last cached price for GGAL was: `$250.00 (timestamp: 1 hour ago)`  
**When** the dashboard loads  
**And** both IOL and yfinance fail  
**Then** the price factory returns the cached price: `$250.00`  
**And** the dashboard displays: "Current Price: $250.00 (Stale — 1 hour ago)"  
**And** the source badge is "Stale" (orange)  

---

### Scenario 5: Price History on Analysis Page

**Given** a user views the analysis page for GGAL  
**And** the user has GGAL in their portfolio (ARS currency)  
**When** the analysis page loads  
**Then** the current price is fetched from the price factory (IOL with fallback to yfinance)  
**And** the price is displayed with source badge: "Current Price: $250.50 (IOL)"  
**And** historical price chart (if present) continues to show from the existing price_history table  

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| IOL quotes unavailable or inaccurate | Fallback to yfinance; log all fallback events; display source badge for transparency |
| yfinance slow or timeout | Set 5-sec timeout; use cached price if timeout occurs; log timeout events |
| Stale price used for P&L | Mark stale prices with badge; calculate P&L with stale price but flag as potential inaccuracy |
| Cache poisoning (wrong price stored) | Validate price range; log all cache writes; monitor for outliers |
| Different prices on dashboard vs. analysis | Use same price factory for both pages; source badge ensures consistency awareness |
