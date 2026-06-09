# Design: Fundamental Analysis (Deliverable 4)

## Technical Approach

The analysis engine reads cached data from Redis (populated by D3 ingestion layer), computes derived metrics, runs the health score algorithm, and returns a comprehensive analysis package. No external API calls — all data comes from cache. The frontend renders a company detail page with metric cards and DataFreshnessTag.

## Architecture

```
api/analysis.py
      │
      ▼
services/analysis_service.py  ← orchestrator
      │
      ├──▶ services/fundamental_service.py   ← compute metrics from cache
      ├──▶ services/peer_comparison.py       ← rank vs sector peers
      └──▶ services/health_score.py          ← 4 sub-scores → composite
              │
              ▼
schemas/analysis.py           ← AnalysisResponse, MetricCard, HealthScoreResult
schemas/ingestion.py          ← reuse Normalized models from D3
```

## Analysis Response Model

```python
# schemas/analysis.py

class MetricCard(BaseModel):
    label: str
    value: str | None
    category: str         # "valuation", "growth", "financial_health", "dividend"
    nature: str           # "data_driven" | "computed"
    source: str
    fetched_at: datetime | None

class FundamentalMetrics(BaseModel):
    pe_trailing: MetricCard
    pe_forward: MetricCard
    pb_ratio: MetricCard
    revenue_growth_yoy: MetricCard
    eps_trend: list[MetricCard]     # last 8 quarters
    debt_to_equity: MetricCard
    current_ratio: MetricCard
    free_cash_flow: MetricCard

class EarningsData(BaseModel):
    upcoming_date: date | None
    surprises: list[EarningsSurprise]  # last 4 quarters

class DividendData(BaseModel):
    current_yield: str | None
    payout_ratio: str | None
    growth_years: int
    next_ex_date: date | None
    history: list[DividendPayment]

class AnalystData(BaseModel):
    buy_count: int
    hold_count: int
    sell_count: int
    median_target: Decimal | None
    target_range: tuple[Decimal, Decimal] | None

class PeerComparison(BaseModel):
    ticker: str
    sector: str
    peers: list[PeerRank]
    rankings: dict[str, int]  # metric → rank position

class HealthScoreResult(BaseModel):
    composite: int            # 0-100
    verdict: str              # "Strong Buy" | "Accumulate" | ...
    fundamental_quality: int
    earnings_momentum: int
    analyst_sentiment: int
    technical_momentum: int
    top_drivers: list[str]    # top 3 metrics explaining the score
    computed_at: datetime

class AnalysisResponse(BaseModel):
    ticker: str
    company_name: str
    sector: str | None
    price: NormalizedPriceData | None
    fundamentals: FundamentalMetrics | None
    earnings: EarningsData | None
    dividends: DividendData | None
    analysts: AnalystData | None
    peers: PeerComparison | None
    health_score: HealthScoreResult | None
    cached_at: datetime
```

## Health Score Algorithm

Each sub-score = 0-25, summed to composite 0-100.

### Fundamental Quality (0-25)
- P/E scoring: 12-18 ideal (25pts), <12 (15pts), >30 (5pts), negative (0)
- P/B scoring: <3 good, >5 poor
- ROE scoring: >20% good, <5% poor
- D/E: <0.5 good, >2.0 poor
- FCF yield: >5% good

### Earnings Momentum (0-25)
- EPS trend: upward (25), flat (15), declining (5)
- Revenue growth YoY: >15% (25), 5-15% (15), <5% (5)
- Surprise history: >80% beats (25), mixed (15), mostly misses (5)

### Analyst Sentiment (0-25)
- Buy ratio: >70% buy (25), 50-70% (15), <50% (5)
- Price target upside: >20% (25), 10-20% (15), <10% (5)

### Technical Momentum (0-25)
- Placeholder for D5. Default to 15 (neutral) until D5 is implemented.
- After D5: RSI zone, EMA alignment, MACD trend weighting.

## API Endpoint

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/analysis/{ticker}` | Yes | Full fundamental analysis package |

## Frontend Route

| Route | Component | Description |
|-------|-----------|-------------|
| `/analysis/[ticker]` | `app/analysis/[ticker]/page.tsx` | Company detail with metric cards, health score gauge, peer ranking |

## Frontend Components

| Component | Purpose |
|-----------|---------|
| `MetricCard` | Single metric display (label, value, source, freshness) |
| `HealthScoreGauge` | Circular gauge 0-100 with verdict + sub-scores |
| `PeerRankingTable` | Table showing ticker vs peers on key metrics |
| `FundamentalPanel` | Grouped metric cards by category |
| `DataFreshnessTag` | Reuse from D1 — shows data age per card |

## Directory Structure Additions

```
backend/app/
├── schemas/analysis.py          # New: AnalysisResponse, MetricCard, etc.
├── services/
│   ├── fundamental_service.py   # New: compute metrics from cache
│   ├── peer_comparison.py       # New: rank vs sector peers
│   └── health_score.py          # New: 4 sub-scores → composite
├── api/analysis.py              # New: GET /analysis/{ticker}

frontend/src/
├── app/analysis/[ticker]/page.tsx   # New: company detail page
├── components/
│   ├── analysis/
│   │   ├── MetricCard.tsx
│   │   ├── HealthScoreGauge.tsx
│   │   ├── PeerRankingTable.tsx
│   │   └── FundamentalPanel.tsx
│   └── layout/DataFreshnessTag.tsx  # Existing, reused
```

## Review Workload Forecast

| Layer | Files | Est. Lines |
|-------|-------|-----------|
| Schemas (analysis) | 1 | ~120 |
| Fundamental service | 1 | ~180 |
| Peer comparison | 1 | ~100 |
| Health score engine | 1 | ~150 |
| Analysis API | 1 | ~50 |
| Frontend pages | 1 | ~80 |
| Frontend components | 4 | ~200 |
| Types (frontend) | 1 | ~60 |
| Tests (backend) | 3 | ~300 |
| **Total** | **14 files** | **~1,240 lines** |

> Risk: HIGH. Split into 3 chained PRs:
> - **PR 6a:** Backend schemas + fundamental service (~300 lines)
> - **PR 6b:** Backend health score + peer comparison + API (~350 lines)
> - **PR 6c:** Backend tests + Frontend page + components (~590 lines)
