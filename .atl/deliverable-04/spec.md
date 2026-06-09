# Spec: Fundamental Analysis (Deliverable 4)

## Intent
Build the analysis engine that computes comprehensive fundamental metrics for any ticker, ranks companies against sector peers, generates a composite health score from four sub-scores, and displays results on a frontend company detail page with DataFreshnessTag.

## Requirements

### R1 — Fundamental Metrics Computation
**R1.1** Compute P/E ratio (trailing and forward), P/B ratio, revenue growth (YoY/QoQ), EPS trend (last 8 quarters), debt-to-equity, current ratio, free cash flow (TTM).
**R1.2** All metrics include `source` (provider name) and `fetched_at` timestamp.
**R1.3** Metrics distinguish between "data-driven" (from API) and "computed" (derived by engine).

### R2 — Earnings & Dividend Data
**R2.1** Display historical earnings surprises (actual vs estimate, last 4 quarters).
**R2.2** Display dividend history: current yield, payout ratio, years of growth, next ex-date.
**R2.3** Show upcoming earnings date.

### R3 — Analyst & Insider Activity
**R3.1** Analyst consensus: buy/hold/sell count, median price target, target range.
**R3.2** Most recent rating change (upgrade/downgrade/initiated).
**R3.3** Insider transactions: last 90 days, type, shares, value, role.

### R4 — Peer Comparison
**R4.1** Rank ticker vs 5 closest sector peers on: P/E, revenue growth, ROE, debt-to-equity.
**R4.2** Show peer ranking with percentile position within the group.

### R5 — Health Score Engine
**R5.1** Composite score 0-100 from four equally-weighted sub-scores.
**R5.2** Sub-scores: Fundamental Quality, Earnings Momentum, Analyst Sentiment, Technical Momentum.
**R5.3** Map score to verdict: Strong Buy (80-100), Accumulate (65-79), Hold (45-64), Reduce (30-44), Avoid (0-29).
**R5.4** Store in DB (`health_scores` table) with computation timestamp.

### R6 — API Endpoint
**R6.1** `GET /analysis/{ticker}` returns full fundamental analysis package.
**R6.2** Response includes all metrics, peer comparison, health score, dividend/earnings data.
**R6.3** Uses cached data from ingestion layer. Does NOT call external APIs directly.

### R7 — Frontend Company Detail Page
**R7.1** `/analysis/[ticker]` displays all metrics in cards.
**R7.2** Health score shown as a gauge/circular progress with verdict.
**R7.3** DataFreshnessTag on every metric panel.
**R7.4** Peer comparison shown as a ranking table.

## Scenarios

### S1: Fetch analysis for a ticker
```
GIVEN AAPL data cached from ingestion
WHEN GET /analysis/AAPL
THEN 200 returned with P/E, P/B, revenue growth, EPS trend, health score, peer rank
```

### S2: Health score verdict
```
GIVEN AAPL has strong fundamentals and good analyst sentiment
WHEN health score is computed
THEN composite score >= 80, verdict "Strong Buy", with top 3 driving metrics
```

### S3: Peer comparison
```
GIVEN AAPL is in sector Technology
WHEN peer comparison runs
THEN ranked vs 5 tech peers on P/E, ROE, revenue growth, D/E with percentile
```

### S4: No cached data
```
GIVEN no ingested data for ticker XYZ
WHEN GET /analysis/XYZ
THEN 503 with detail "No data available — run ingestion first"
```

### S5: DataFreshness indicators
```
GIVEN AAPL data cached 2 hours ago
WHEN company detail page loads
THEN DataFreshnessTag shows "cached" status with fetch timestamp on every panel
```
