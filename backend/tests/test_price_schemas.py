"""Tests for PricePoint and PriceSeriesResponse schemas (RED — file not yet created)."""
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest


def test_price_point_exists():
    """PricePoint must be importable from app.schemas.prices."""
    from app.schemas.prices import PricePoint  # noqa: F401


def test_price_series_response_exists():
    """PriceSeriesResponse must be importable from app.schemas.prices."""
    from app.schemas.prices import PriceSeriesResponse  # noqa: F401


def test_price_point_fields():
    """PricePoint must have date (date), OHLC Decimal, optional volume."""
    from app.schemas.prices import PricePoint

    pt = PricePoint(
        date=date(2025, 6, 10),
        open=Decimal("150.0000"),
        high=Decimal("155.0000"),
        low=Decimal("149.0000"),
        close=Decimal("153.0000"),
        volume=1_000_000,
    )
    assert pt.date == date(2025, 6, 10)
    assert isinstance(pt.open, Decimal)
    assert isinstance(pt.close, Decimal)
    assert pt.volume == 1_000_000


def test_price_point_volume_optional():
    """PricePoint.volume must be optional."""
    from app.schemas.prices import PricePoint

    pt = PricePoint(
        date=date(2025, 6, 10),
        open=Decimal("150.0000"),
        high=Decimal("155.0000"),
        low=Decimal("149.0000"),
        close=Decimal("153.0000"),
        volume=None,
    )
    assert pt.volume is None


def test_price_series_response_fields():
    """PriceSeriesResponse must have ticker, points, from_date, to_date, count, source, freshness, fetched_at."""
    from app.schemas.prices import PricePoint, PriceSeriesResponse

    now = datetime.now(timezone.utc)
    resp = PriceSeriesResponse(
        ticker="AAPL",
        points=[
            PricePoint(
                date=date(2025, 6, 10),
                open=Decimal("150.0000"),
                high=Decimal("155.0000"),
                low=Decimal("149.0000"),
                close=Decimal("153.0000"),
                volume=1_000_000,
            )
        ],
        from_date=date(2025, 1, 1),
        to_date=date(2025, 6, 10),
        count=1,
        source="yfinance",
        freshness="fresh",
        fetched_at=now,
    )
    assert resp.ticker == "AAPL"
    assert len(resp.points) == 1
    assert resp.count == 1
    assert resp.source == "yfinance"
    assert resp.freshness == "fresh"
    assert resp.fetched_at == now


def test_price_series_response_fetched_at_optional():
    """PriceSeriesResponse.fetched_at must be optional."""
    from app.schemas.prices import PriceSeriesResponse

    resp = PriceSeriesResponse(
        ticker="AAPL",
        points=[],
        from_date=date(2025, 1, 1),
        to_date=date(2025, 6, 10),
        count=0,
        source="yfinance",
        freshness="stale",
        fetched_at=None,
    )
    assert resp.fetched_at is None
