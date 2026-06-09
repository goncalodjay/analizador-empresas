# Design: Technical Analysis + TradingView (Deliverable 5)

## Technical Approach

Technical indicators are computed locally using yfinance historical OHLCV data + pandas/numpy. No external API calls for indicators — Alpha Vantage is optional (D3 already built the provider). The TradingView widget is a pure client-side embed via `<script>` tag. Technical data is added to the existing `AnalysisResponse` model as an optional `technical` field.

## Architecture

```
api/analysis.py                    ← modified: adds technical to response
      │
      ▼
services/technical_service.py      ← NEW: compute all indicators from yfinance history
      │
      └──▶ yfinance (history)      ← fetch 1y daily OHLCV
      │
      ├── RSI (Wilder's 14)
      ├── MACD (EMA 12/26/9)
      ├── EMA (9, 21, 50, 200)
      ├── Bollinger Bands (SMA 20 ± 2σ)
      ├── 52-week range
      └── Relative volume
```

## Data Models (extend schemas/analysis.py)

```python
class TechnicalIndicators(BaseModel):
    rsi: RsiData | None
    macd: MacdData | None
    ema: EmaData | None
    bollinger: BollingerData | None
    fifty_two_week: FiftyTwoWeekData | None
    relative_volume: RelativeVolumeData | None
    source: str = "yfinance"
    computed_at: datetime

class RsiData(BaseModel):
    value: Decimal
    zone: str        # "oversold" | "neutral" | "overbought"
    trend: str       # "rising" | "falling" | "steady"

class MacdData(BaseModel):
    macd_line: Decimal
    signal_line: Decimal
    histogram: Decimal
    crossover: str   # "bullish" | "bearish" | "neutral"

class EmaData(BaseModel):
    ema_9: Decimal
    ema_21: Decimal
    ema_50: Decimal
    ema_200: Decimal
    price_vs_ema_9: str      # "above" | "below"
    price_vs_ema_200: str
    golden_cross: bool
    death_cross: bool

class BollingerData(BaseModel):
    upper_band: Decimal
    middle_band: Decimal
    lower_band: Decimal
    bandwidth: Decimal
    squeeze: bool

class FiftyTwoWeekData(BaseModel):
    high: Decimal
    low: Decimal
    current: Decimal
    position_pct: Decimal

class RelativeVolumeData(BaseModel):
    ratio: Decimal
    label: str  # "low" | "average" | "high"
```

## Extended AnalysisResponse

Add one field to existing `AnalysisResponse`:
```python
class AnalysisResponse(BaseModel):
    ...
    technical: TechnicalIndicators | None = None
```

## TradingView Widget

Client-side embed — no backend changes needed. The widget uses a `<div>` with a `<script>` from `tradingview.com`. The ticker is passed as a prop.

```tsx
// components/analysis/TradingViewChart.tsx
export function TradingViewChart({ ticker }: { ticker: string }) {
  // Embed via TradingView widget script
  // Uses free TradingView Advanced Chart widget
}
```

## Technical Service

```python
# services/technical_service.py
class TechnicalService:
    async def compute(ticker: str) -> TechnicalIndicators | None:
        # 1. Fetch 1y daily history from yfinance
        # 2. Compute RSI, MACD, EMA, Bollinger, 52-week, relative volume
        # 3. Return TechnicalIndicators model
```

## Indicator Formulas

**RSI (Wilder's):**
- `gain = avg(close − prev_close, 14) where close > prev_close`
- `loss = avg(prev_close − close, 14) where close < prev_close`
- `rs = gain / loss`
- `rsi = 100 − (100 / (1 + rs))`

**MACD:**
- `ema_12 = close.ewm(span=12).mean()`
- `ema_26 = close.ewm(span=26).mean()`
- `macd_line = ema_12 − ema_26`
- `signal = macd_line.ewm(span=9).mean()`
- `histogram = macd_line − signal`

**EMA:** pandas `ewm(span=N).mean()`
**Bollinger:** `sma_20 = close.rolling(20).mean()` ± `2 * close.rolling(20).std()`
**52-week:** `max(high, 252 periods)`, `min(low, 252 periods)`
**Relative Volume:** `volume[-1] / volume[-21:-1].mean()`

## Dependencies

Add to `requirements.txt`:
- `pandas` (already installed via yfinance)
- `numpy` (already installed via pgvector)

## Directory Structure

```
backend/app/
├── services/technical_service.py    # New
├── schemas/analysis.py              # Modified: add TechnicalIndicators + extend AnalysisResponse

frontend/src/
├── components/analysis/
│   ├── TradingViewChart.tsx         # New
│   ├── TechnicalPanel.tsx           # New
│   ├── RsiGauge.tsx                 # New
│   └── MacdSummary.tsx              # New
├── app/analysis/[ticker]/page.tsx   # Modified: add technical panels
```

## Review Workload Forecast

| Layer | Files | Est. Lines |
|-------|-------|-----------|
| Schemas (extend) | 1 modified | ~80 |
| Technical service | 1 | ~200 |
| Analysis API (modify) | 1 | ~20 |
| Frontend components | 4 | ~250 |
| Analysis page (modify) | 1 | ~40 |
| Tests | 2 | ~200 |
| **Total** | **10 files** | **~790 lines** |

> Risk: MEDIUM. Could be 1 PR but close to 800 lines. Split into 2:
> - **PR 7a:** Backend (schemas + technical service + API, ~300 lines)
> - **PR 7b:** Frontend + tests (components + TradingView + tests, ~490 lines)
