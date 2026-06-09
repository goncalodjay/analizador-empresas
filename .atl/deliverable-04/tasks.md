# Tasks: Fundamental Analysis (Deliverable 4)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1,240 |
| 400-line budget risk | HIGH |
| Chained PRs required | Yes |
| Delivery strategy | PR 6a (schemas + fundamental service) → PR 6b (health score + peers + API) → PR 6c (tests + frontend) |

---

## PR 6a: Backend Schemas + Fundamental Service (~300 lines)

### Task 6a.1 — Analysis schemas
**Files:** `schemas/analysis.py`
- `MetricCard` (label, value, category, nature, source, fetched_at)
- `FundamentalMetrics` (P/E, P/B, revenue growth, EPS trend, D/E, current ratio, FCF)
- `EarningsData`, `EarningsSurprise`, `DividendData`, `DividendPayment`
- `AnalystData` (buy/hold/sell counts, median target, range)
- `PeerComparison`, `PeerRank`
- `HealthScoreResult` (composite, verdict, 4 sub-scores, top_drivers)
- `AnalysisResponse` (full package)
- **Verification:** model instantiation tests

### Task 6a.2 — Fundamental metrics service
**Files:** `services/fundamental_service.py`
- `compute_metrics(ticker)` — reads cache, computes all FundamentalMetrics
- Reads price, fundamentals, dividends from Redis (via CacheService from D3)
- Computes derived metrics: P/E forward from growth rate, FCF yield
- Formats every metric as MetricCard with nature/source/timestamp
- Returns `FundamentalMetrics` or None if no cached data
- **Verification:** unit tests with mock cache data

---

## PR 6b: Health Score + Peer Comparison + API (~350 lines)

### Task 6b.1 — Health score engine
**Files:** `services/health_score.py`
- `compute_health_score(ticker)` — 4 sub-scores → composite 0-100
- Fundamental quality (0-25): P/E, P/B, ROE, D/E, FCF yield
- Earnings momentum (0-25): EPS trend, revenue growth, surprise history
- Analyst sentiment (0-25): buy ratio, price target upside
- Technical momentum (0-25): placeholder = 15, implement in D5
- Verdict mapping: Strong Buy / Accumulate / Hold / Reduce / Avoid
- Top 3 drivers extracted from dominant sub-scores
- **Verification:** unit tests with known inputs

### Task 6b.2 — Peer comparison engine
**Files:** `services/peer_comparison.py`
- `compare_peers(ticker, sector)` — find 5 closest sector peers
- Rank on: P/E, revenue growth, ROE, debt-to-equity
- Uses cached fundamentals from Redis for peer tickers
- Returns `PeerComparison` with rankings
- **Verification:** unit tests

### Task 6b.3 — Analysis API endpoint
**Files:** `api/analysis.py` + wire in `main.py`
- `GET /analysis/{ticker}` — full analysis package
- Orchestrates fundamental_service, health_score, peer_comparison
- Returns `AnalysisResponse`
- Returns 503 if no cached data available
- **Verification:** integration test with mock cache

---

## PR 6c: Tests + Frontend (~590 lines)

### Task 6c.1 — Backend integration tests
**Files:** `tests/test_analysis.py`, `tests/test_health_score.py`
- Test health score computation with known inputs
- Test peer comparison logic
- Test analysis API endpoint with mock cache data
- Test 503 response when no data cached
- **Verification:** pytest passes

### Task 6c.2 — Frontend types
**Files:** `lib/types.ts` (modify)
- Add AnalysisResponse, MetricCard, HealthScoreResult, etc. interfaces
- **Verification:** TypeScript compilation

### Task 6c.3 — Frontend components
**Files:** `components/analysis/`
- `MetricCard.tsx` — single metric display
- `HealthScoreGauge.tsx` — circular gauge with verdict
- `PeerRankingTable.tsx` — ranking table
- `FundamentalPanel.tsx` — grouped metric cards by category
- **Verification:** Next.js build

### Task 6c.4 — Company detail page
**Files:** `app/analysis/[ticker]/page.tsx`
- Displays company name, sector, price
- HealthScoreGauge at the top
- Metric cards grouped by category
- Peer ranking table
- DataFreshnessTag on every panel
- **Verification:** Next.js build, renders all sections

### Task 6c.5 — Ticker search/link from portfolio
**Files:** `components/portfolio/PortfolioTable.tsx` (modify)
- Make ticker clickable, linking to `/analysis/{ticker}`
- **Verification:** Next.js build
