# Spec: Technical Analysis + TradingView (Deliverable 5)

## Intent
Compute technical indicators locally from yfinance historical price data, display them on the company detail page alongside fundamentals, and embed an interactive TradingView candlestick chart. Technical signals are supporting context — not primary decision drivers.

## Requirements

### R1 — Price Range & 52-Week Levels
**R1.1** Compute 52-week high and low from 1-year historical data.
**R1.2** Show current price position as a percentage within the 52-week range (0% = low, 100% = high).
**R1.3** Each value labeled with data source and timestamp.

### R2 — RSI (14-Period)
**R2.1** Compute using Wilder's smoothing method over 14 periods.
**R2.2** Classify zone: oversold (<30), neutral (30-70), overbought (>70).
**R2.3** Show trend direction (rising/falling) over last 5 periods.

### R3 — MACD
**R3.1** Compute MACD line (EMA 12 − EMA 26), signal line (EMA 9 of MACD), histogram.
**R3.2** Detect crossover status: bullish (MACD > signal), bearish (MACD < signal).

### R4 — Exponential Moving Averages
**R4.1** Compute EMA 9, EMA 21, EMA 50, EMA 200.
**R4.2** Show price position relative to each EMA (above/below, percentage distance).
**R4.3** Detect golden cross (EMA 50 crosses above EMA 200) and death cross (EMA 50 crosses below EMA 200).

### R5 — Bollinger Bands
**R5.1** Compute using SMA 20 ± 2 standard deviations.
**R5.2** Show bandwidth (upper − lower) / middle.
**R5.3** Detect squeeze: bandwidth at 6-month minimum (compression precedes expansion).

### R6 — Relative Volume
**R6.1** Compute today's volume vs. 20-day average volume as a ratio.
**R6.2** Classify as: low (<0.5), average (0.5-1.5), high (>1.5).

### R7 — Extend Analysis API
**R7.1** Add `technical` field to existing `GET /analysis/{ticker}` response.
**R7.2** Technical indicators computed locally from yfinance history (not calling Alpha Vantage).
**R7.3** Store computed signals in `technical_signals` DB table with timestamp.

### R8 — TradingView Widget
**R8.1** Embed TradingView Advanced Chart widget on the company detail page.
**R8.2** Pre-configured with ticker symbol, candlestick chart, and indicator overlays.
**R8.3** Client-side only — no server involvement beyond passing the ticker.

### R9 — Frontend Technical Panel
**R9.1** Technical metrics displayed in a collapsible panel below fundamentals.
**R9.2** RSI shown as a gauge bar (0-100) with zone coloring.
**R9.3** MACD and EMA data in a labeled summary card.
**R9.4** DataFreshnessTag on every technical panel.

## Scenarios

### S1: Compute RSI
```
GIVEN 6 months of AAPL daily close prices from yfinance
WHEN RSI is computed with 14-period Wilder's smoothing
THEN RSI value is between 0-100, zone is classified, trend direction shown
```

### S2: Detect golden cross
```
GIVEN EMA 50 just crossed above EMA 200
WHEN technical signals are computed
THEN golden_cross = true, signal shown on the analysis page
```

### S3: TradingView embed
```
GIVEN user is viewing /analysis/AAPL
WHEN the page loads
THEN TradingView chart widget renders with candlestick chart for AAPL
```

### S4: Bollinger squeeze
```
GIVEN bandwidth is at 6-month minimum
WHEN indicators are computed
THEN squeeze_detected = true, shown as a visual alert
```

### S5: Extend analysis response
```
GIVEN GET /analysis/AAPL returns fundamentals + health score
WHEN technical indicators are also available
THEN response includes "technical" object with all indicators
```
