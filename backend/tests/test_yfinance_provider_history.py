"""Tests for YFinanceProvider.fetch_price_history (RED — method not yet implemented)."""
from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
import pandas as pd
import numpy as np


def _make_hist_df(rows: list[dict]) -> pd.DataFrame:
    """Build a fake yfinance history DataFrame."""
    index = pd.DatetimeIndex(
        [pd.Timestamp(r["date"], tz="UTC") for r in rows]
    )
    data = {
        "Open": [r["open"] for r in rows],
        "High": [r["high"] for r in rows],
        "Low": [r["low"] for r in rows],
        "Close": [r["close"] for r in rows],
        "Volume": [r["volume"] for r in rows],
    }
    return pd.DataFrame(data, index=index)


SAMPLE_ROWS = [
    {"date": "2025-01-02", "open": 150.0, "high": 155.0, "low": 149.0, "close": 153.0, "volume": 1_000_000},
    {"date": "2025-01-03", "open": 153.0, "high": 158.0, "low": 152.0, "close": 156.0, "volume": 1_200_000},
    {"date": "2025-01-06", "open": 156.0, "high": 160.0, "low": 155.0, "close": 159.0, "volume": 900_000},
]

NAN_ROW = {"date": "2025-01-07", "open": float("nan"), "high": float("nan"), "low": float("nan"), "close": float("nan"), "volume": 0}


@pytest.mark.asyncio
async def test_fetch_price_history_returns_list_of_bars():
    """fetch_price_history returns a list of NormalizedPriceBar."""
    from app.providers.yfinance_provider import YFinanceProvider
    from app.schemas.ingestion import NormalizedPriceBar

    mock_ticker = MagicMock()
    mock_ticker.history.return_value = _make_hist_df(SAMPLE_ROWS)

    with patch.object(YFinanceProvider, "_get_ticker", return_value=mock_ticker):
        provider = YFinanceProvider()
        bars = await provider.fetch_price_history("AAPL", "1y")

    assert isinstance(bars, list)
    assert len(bars) == 3
    assert all(isinstance(b, NormalizedPriceBar) for b in bars)


@pytest.mark.asyncio
async def test_fetch_price_history_date_is_calendar_date():
    """Each bar's date must be a calendar date (not datetime)."""
    from app.providers.yfinance_provider import YFinanceProvider

    mock_ticker = MagicMock()
    mock_ticker.history.return_value = _make_hist_df(SAMPLE_ROWS)

    with patch.object(YFinanceProvider, "_get_ticker", return_value=mock_ticker):
        provider = YFinanceProvider()
        bars = await provider.fetch_price_history("AAPL", "1y")

    for bar in bars:
        assert type(bar.date) is date, f"Expected date, got {type(bar.date)}"


@pytest.mark.asyncio
async def test_fetch_price_history_ohlc_are_decimal():
    """OHLC values must be Decimal."""
    from app.providers.yfinance_provider import YFinanceProvider

    mock_ticker = MagicMock()
    mock_ticker.history.return_value = _make_hist_df(SAMPLE_ROWS)

    with patch.object(YFinanceProvider, "_get_ticker", return_value=mock_ticker):
        provider = YFinanceProvider()
        bars = await provider.fetch_price_history("AAPL", "1y")

    bar = bars[0]
    assert isinstance(bar.open, Decimal)
    assert isinstance(bar.close, Decimal)


@pytest.mark.asyncio
async def test_fetch_price_history_skips_nan_rows():
    """Rows with NaN OHLC values must be skipped."""
    from app.providers.yfinance_provider import YFinanceProvider

    rows_with_nan = SAMPLE_ROWS + [NAN_ROW]
    mock_ticker = MagicMock()
    mock_ticker.history.return_value = _make_hist_df(rows_with_nan)

    with patch.object(YFinanceProvider, "_get_ticker", return_value=mock_ticker):
        provider = YFinanceProvider()
        bars = await provider.fetch_price_history("AAPL", "1y")

    # NaN row must be skipped — only 3 valid rows
    assert len(bars) == 3


@pytest.mark.asyncio
async def test_fetch_price_history_calls_ticker_history_with_period():
    """provider.fetch_price_history must call Ticker.history(period=..., interval='1d')."""
    from app.providers.yfinance_provider import YFinanceProvider

    mock_ticker = MagicMock()
    mock_ticker.history.return_value = _make_hist_df(SAMPLE_ROWS)

    with patch.object(YFinanceProvider, "_get_ticker", return_value=mock_ticker):
        provider = YFinanceProvider()
        await provider.fetch_price_history("AAPL", "7d")

    mock_ticker.history.assert_called_once_with(period="7d", interval="1d")


@pytest.mark.asyncio
async def test_fetch_price_is_unaffected():
    """fetch_price (existing hot path) must still work correctly."""
    from app.providers.yfinance_provider import YFinanceProvider
    from app.schemas.ingestion import NormalizedPriceData

    mock_ticker = MagicMock()
    mock_ticker.history.return_value = _make_hist_df([SAMPLE_ROWS[-1]])

    with patch.object(YFinanceProvider, "_get_ticker", return_value=mock_ticker):
        provider = YFinanceProvider()
        price = await provider.fetch_price("AAPL")

    assert isinstance(price, NormalizedPriceData)
    assert price.ticker == "AAPL"
    assert isinstance(price.date, datetime)
