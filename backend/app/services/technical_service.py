from datetime import datetime, timezone
from decimal import Decimal

import pandas as pd

from app.schemas.analysis import (
    BollingerData,
    EmaData,
    FiftyTwoWeekData,
    MacdData,
    RelativeVolumeData,
    RsiData,
    TechnicalIndicators,
)


def _compute_rsi(close: pd.Series, period: int = 14) -> RsiData:
    """Compute RSI using Wilder's smoothing method."""
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Wilder's smoothing = EWM with alpha=1/period (adjust=False, min_periods=period)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()

    # When avg_loss == 0 (pure uptrend), RSI = 100; avoid division by zero/NaN.
    last_gain = float(avg_gain.iloc[-1])
    last_loss = float(avg_loss.iloc[-1])
    if last_loss == 0:
        current = 100.0 if last_gain > 0 else 50.0
        rsi_series = avg_gain.copy()
        rsi_series[:] = float("nan")
        rsi_series.iloc[-1] = current
    else:
        rs = avg_gain / avg_loss
        rsi_series = 100 - (100 / (1 + rs))

    current = float(rsi_series.iloc[-1])

    if current < 30:
        zone = "oversold"
    elif current > 70:
        zone = "overbought"
    else:
        zone = "neutral"

    # Trend over last 5 periods
    recent = rsi_series.dropna().iloc[-5:]
    if len(recent) >= 2:
        first, last = float(recent.iloc[0]), float(recent.iloc[-1])
        if last - first > 1.0:
            trend = "rising"
        elif first - last > 1.0:
            trend = "falling"
        else:
            trend = "steady"
    else:
        trend = "steady"

    return RsiData(
        value=Decimal(str(round(current, 4))),
        zone=zone,
        trend=trend,
    )


def _compute_macd(close: pd.Series) -> MacdData:
    """Compute MACD (12/26/9)."""
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line

    m = float(macd_line.iloc[-1])
    s = float(signal_line.iloc[-1])
    h = float(histogram.iloc[-1])

    if m > s:
        crossover = "bullish"
    elif m < s:
        crossover = "bearish"
    else:
        crossover = "neutral"

    return MacdData(
        macd_line=Decimal(str(round(m, 6))),
        signal_line=Decimal(str(round(s, 6))),
        histogram=Decimal(str(round(h, 6))),
        crossover=crossover,
    )


def _compute_ema(close: pd.Series) -> EmaData:
    """Compute EMA 9, 21, 50, 200 and detect crosses."""
    ema_9 = close.ewm(span=9, adjust=False).mean()
    ema_21 = close.ewm(span=21, adjust=False).mean()
    ema_50 = close.ewm(span=50, adjust=False).mean()
    ema_200 = close.ewm(span=200, adjust=False).mean()

    current_price = float(close.iloc[-1])
    e9 = float(ema_9.iloc[-1])
    e21 = float(ema_21.iloc[-1])
    e50 = float(ema_50.iloc[-1])
    e200 = float(ema_200.iloc[-1])

    # Golden/death cross: EMA 50 crosses EMA 200
    # Check if a crossover happened in the last 5 bars
    golden_cross = False
    death_cross = False
    if len(ema_50) >= 2 and len(ema_200) >= 2:
        prev_50 = float(ema_50.iloc[-2])
        prev_200 = float(ema_200.iloc[-2])
        if prev_50 <= prev_200 and e50 > e200:
            golden_cross = True
        elif prev_50 >= prev_200 and e50 < e200:
            death_cross = True

    return EmaData(
        ema_9=Decimal(str(round(e9, 4))),
        ema_21=Decimal(str(round(e21, 4))),
        ema_50=Decimal(str(round(e50, 4))),
        ema_200=Decimal(str(round(e200, 4))),
        price_vs_ema_9="above" if current_price >= e9 else "below",
        price_vs_ema_200="above" if current_price >= e200 else "below",
        golden_cross=golden_cross,
        death_cross=death_cross,
    )


def _compute_bollinger(close: pd.Series, window: int = 20) -> BollingerData:
    """Compute Bollinger Bands (SMA 20 ± 2σ) and detect squeeze."""
    sma = close.rolling(window).mean()
    std = close.rolling(window).std()

    upper = sma + 2 * std
    lower = sma - 2 * std

    mid = float(sma.iloc[-1])
    up = float(upper.iloc[-1])
    lo = float(lower.iloc[-1])
    bw = (up - lo) / mid if mid != 0 else 0.0

    # Squeeze: current bandwidth at 6-month minimum (≈ 126 trading days)
    bw_series = (upper - lower) / sma.replace(0, float("nan"))
    lookback = min(126, len(bw_series))
    recent_bw = bw_series.dropna().iloc[-lookback:]
    squeeze = bool(len(recent_bw) > 1 and bw <= float(recent_bw.min()) * 1.02)

    return BollingerData(
        upper_band=Decimal(str(round(up, 4))),
        middle_band=Decimal(str(round(mid, 4))),
        lower_band=Decimal(str(round(lo, 4))),
        bandwidth=Decimal(str(round(bw, 6))),
        squeeze=squeeze,
    )


def _compute_fifty_two_week(high: pd.Series, low: pd.Series, close: pd.Series) -> FiftyTwoWeekData:
    """Compute 52-week high/low and price position."""
    wk_high = float(high.iloc[-252:].max())
    wk_low = float(low.iloc[-252:].min())
    current = float(close.iloc[-1])

    rng = wk_high - wk_low
    position_pct = ((current - wk_low) / rng * 100) if rng > 0 else 50.0

    return FiftyTwoWeekData(
        high=Decimal(str(round(wk_high, 4))),
        low=Decimal(str(round(wk_low, 4))),
        current=Decimal(str(round(current, 4))),
        position_pct=Decimal(str(round(position_pct, 2))),
    )


def _compute_relative_volume(volume: pd.Series) -> RelativeVolumeData:
    """Compute today's volume vs 20-day average."""
    today_vol = float(volume.iloc[-1])
    avg_vol = float(volume.iloc[-21:-1].mean()) if len(volume) > 21 else float(volume.mean())

    ratio = today_vol / avg_vol if avg_vol > 0 else 0.0

    if ratio < 0.5:
        label = "low"
    elif ratio > 1.5:
        label = "high"
    else:
        label = "average"

    return RelativeVolumeData(
        ratio=Decimal(str(round(ratio, 4))),
        label=label,
    )


def compute_indicators(df: pd.DataFrame) -> TechnicalIndicators | None:
    """
    Compute all technical indicators from an OHLCV DataFrame.

    Expected columns: Open, High, Low, Close, Volume (case-insensitive).
    Returns None if the DataFrame is empty or has insufficient data.
    This function is intentionally pure (no network calls) so tests can inject
    synthetic price data directly.
    """
    if df is None or df.empty:
        return None

    # Normalise column names to title-case
    df = df.copy()
    df.columns = [c.capitalize() for c in df.columns]

    required = {"Close", "High", "Low", "Volume"}
    if not required.issubset(set(df.columns)):
        return None

    close = df["Close"].dropna()
    high = df["High"].dropna()
    low = df["Low"].dropna()
    volume = df["Volume"].dropna()

    if len(close) < 30:
        return None

    try:
        rsi = _compute_rsi(close)
    except Exception:
        rsi = None

    try:
        macd = _compute_macd(close)
    except Exception:
        macd = None

    try:
        ema = _compute_ema(close)
    except Exception:
        ema = None

    try:
        bollinger = _compute_bollinger(close)
    except Exception:
        bollinger = None

    try:
        fifty_two_week = _compute_fifty_two_week(high, low, close)
    except Exception:
        fifty_two_week = None

    try:
        relative_volume = _compute_relative_volume(volume)
    except Exception:
        relative_volume = None

    return TechnicalIndicators(
        rsi=rsi,
        macd=macd,
        ema=ema,
        bollinger=bollinger,
        fifty_two_week=fifty_two_week,
        relative_volume=relative_volume,
        source="yfinance",
        computed_at=datetime.now(timezone.utc),
    )


class TechnicalService:
    """Fetch 1-year OHLCV history from yfinance and compute technical indicators."""

    async def compute(self, ticker: str) -> TechnicalIndicators | None:
        try:
            import yfinance as yf

            ticker_obj = yf.Ticker(ticker.upper())
            df = ticker_obj.history(period="1y", interval="1d")
        except Exception:
            return None

        return compute_indicators(df)
