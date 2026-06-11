"""Tests for NormalizedPriceBar schema (RED — not yet added to ingestion.py)."""
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest


def test_normalized_price_bar_exists():
    """NormalizedPriceBar must be importable from app.schemas.ingestion."""
    from app.schemas.ingestion import NormalizedPriceBar  # noqa: F401


def test_normalized_price_bar_date_is_date_type():
    """NormalizedPriceBar.date must be a calendar date (not datetime)."""
    from app.schemas.ingestion import NormalizedPriceBar

    bar = NormalizedPriceBar(
        ticker="AAPL",
        date=date(2025, 6, 10),
        open=Decimal("150.0000"),
        high=Decimal("155.0000"),
        low=Decimal("149.0000"),
        close=Decimal("153.0000"),
        volume=1_000_000,
        source="yfinance",
        fetched_at=datetime.now(timezone.utc),
    )
    assert isinstance(bar.date, date)
    # Ensure it is NOT a datetime (datetime is a subclass of date)
    assert type(bar.date) is date, f"Expected date, got {type(bar.date)}"


def test_normalized_price_bar_ohlc_decimal():
    """OHLC fields must be Decimal."""
    from app.schemas.ingestion import NormalizedPriceBar

    bar = NormalizedPriceBar(
        ticker="AAPL",
        date=date(2025, 6, 10),
        open=Decimal("150.0000"),
        high=Decimal("155.0000"),
        low=Decimal("149.0000"),
        close=Decimal("153.0000"),
        volume=None,
        source="yfinance",
        fetched_at=datetime.now(timezone.utc),
    )
    assert isinstance(bar.open, Decimal)
    assert isinstance(bar.high, Decimal)
    assert isinstance(bar.low, Decimal)
    assert isinstance(bar.close, Decimal)


def test_normalized_price_bar_volume_optional():
    """volume must be optional (None allowed)."""
    from app.schemas.ingestion import NormalizedPriceBar

    bar = NormalizedPriceBar(
        ticker="MSFT",
        date=date(2025, 6, 10),
        open=Decimal("300.0000"),
        high=Decimal("305.0000"),
        low=Decimal("298.0000"),
        close=Decimal("302.0000"),
        volume=None,
        source="yfinance",
        fetched_at=datetime.now(timezone.utc),
    )
    assert bar.volume is None


def test_normalized_price_bar_has_source_and_fetched_at():
    """source and fetched_at fields must be present and correctly typed."""
    from app.schemas.ingestion import NormalizedPriceBar

    now = datetime.now(timezone.utc)
    bar = NormalizedPriceBar(
        ticker="GOOG",
        date=date(2025, 6, 10),
        open=Decimal("100.0"),
        high=Decimal("101.0"),
        low=Decimal("99.0"),
        close=Decimal("100.5"),
        volume=500_000,
        source="yfinance",
        fetched_at=now,
    )
    assert bar.source == "yfinance"
    assert bar.fetched_at == now
