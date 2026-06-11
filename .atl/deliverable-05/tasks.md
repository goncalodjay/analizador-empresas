# Tasks: Technical Analysis + TradingView (Deliverable 5)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~790 |
| 400-line budget risk | MEDIUM |
| Chained PRs | 2 |
| Strategy | PR 7a (Backend) → PR 7b (Frontend + tests) |

---

## PR 7a: Backend Technical Analysis (~300 lines)

### Task 7a.1 — Technical indicator schemas
**Files:** `schemas/analysis.py` (modify)
- Add `RsiData`, `MacdData`, `EmaData`, `BollingerData`, `FiftyTwoWeekData`, `RelativeVolumeData`
- Add `TechnicalIndicators` container model
- Add `technical: TechnicalIndicators | None` to `AnalysisResponse`
- **Verification:** model instantiation tests

### Task 7a.2 — Technical service
**Files:** `services/technical_service.py`
- `compute(ticker)` → `TechnicalIndicators | None`
- Fetch 1y OHLCV history from yfinance
- Compute RSI (Wilder's 14), MACD (12/26/9), EMA (9/21/50/200)
- Compute Bollinger Bands (20 SMA ± 2σ), 52-week range, relative volume
- Golden/death cross detection, squeeze detection
- Return None if no history available
- **Verification:** unit tests with known price series

### Task 7a.3 — Extend analysis API
**Files:** `api/analysis.py` (modify)
- Call `TechnicalService.compute(ticker)` alongside existing services
- Include `technical` in `AnalysisResponse`
- **Verification:** integration test

---

## PR 7b: Frontend + Tests (~490 lines)

### Task 7b.1 — Backend tests
**Files:** `tests/test_technical.py`
- Test RSI computation with known prices
- Test MACD computation
- Test Bollinger Bands computation
- Test golden cross / death cross detection
- Test 52-week range and relative volume
- **Verification:** pytest passes

### Task 7b.2 — TradingView chart widget
**Files:** `components/analysis/TradingViewChart.tsx`
- Embed TradingView Advanced Chart via `<script>` tag
- Configure with ticker symbol, theme, interval
- Responsive container
- **Verification:** Next.js build, widget container renders

### Task 7b.3 — Technical panel components
**Files:** `components/analysis/TechnicalPanel.tsx`, `RsiGauge.tsx`, `MacdSummary.tsx`
- `TechnicalPanel` — collapsible wrapper for all technical indicators
- `RsiGauge` — horizontal bar 0-100 with red/yellow/green zones
- `MacdSummary` — MACD line + signal + histogram with bullish/bearish label
- EMA and Bollinger data shown in label-value pairs
- **Verification:** Next.js build

### Task 7b.4 — Update analysis page
**Files:** `app/analysis/[ticker]/page.tsx` (modify)
- Add TradingViewChart at top
- Add TechnicalPanel below fundamentals
- Integrate RsiGauge and MacdSummary
- **Verification:** Next.js build, all sections render

---

## Fix batch (post-verify)

### Fix W1 — EMA % distance (R4.2)
**Status:** [x] done — commit 7b3eaba
- Extended `EmaData` with `price_vs_ema_21`, `price_vs_ema_50`, and `pct_distance_ema_{9,21,50,200}`
- `_compute_ema()` computes `(price - ema) / ema * 100` for each period
- `TechnicalPanel.tsx` renders all four EMAs with direction + % distance
- 2 new tests added; deterministic golden-cross test replaces skip fallback

### Fix W2 — Persist technical signals (R7.3)
**Status:** [x] done — commit c86caca
- `TechnicalSignal` ORM model and `technical_signals` table were already in `0001_initial_schema.py`
- Added `persist_technical_signal()` in `technical_service.py`
- Wired non-blocking persistence in `GET /analysis/{ticker}`; failure logs and does not break response

### Fix S1 — Remove dead widgetRef
**Status:** [x] done (included in commit 7b3eaba)

### Fix S2 — Deterministic golden-cross test
**Status:** [x] done (included in commit 7b3eaba)
