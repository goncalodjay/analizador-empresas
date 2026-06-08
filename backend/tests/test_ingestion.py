import pytest
from datetime import datetime, timezone
from decimal import Decimal

from app.schemas.ingestion import (
    NormalizedPriceData,
    NormalizedFundamentals,
    NormalizedDividend,
    NormalizedCompanyInfo,
    IngestionResult,
    CacheStatus,
)


def test_price_data_model():
    now = datetime.now(timezone.utc)
    data = NormalizedPriceData(
        ticker="AAPL",
        date=now,
        open=Decimal("150.0"),
        high=Decimal("152.0"),
        low=Decimal("149.0"),
        close=Decimal("151.0"),
        volume=1000000,
        source="yfinance",
        fetched_at=now,
    )
    assert data.ticker == "AAPL"
    assert data.close == Decimal("151.0")


def test_fundamentals_model():
    now = datetime.now(timezone.utc)
    data = NormalizedFundamentals(
        ticker="AAPL",
        pe_ratio=Decimal("28.5"),
        market_cap=2800000000000,
        sector="Technology",
        source="yfinance",
        fetched_at=now,
    )
    assert data.pe_ratio == Decimal("28.5")
    assert data.pb_ratio is None


def test_dividend_model():
    now = datetime.now(timezone.utc)
    data = NormalizedDividend(
        ticker="AAPL",
        ex_date=now.date(),
        amount=Decimal("0.24"),
        yield_pct=Decimal("0.005"),
        source="yfinance",
        fetched_at=now,
    )
    assert data.amount == Decimal("0.24")


def test_company_info_model():
    now = datetime.now(timezone.utc)
    data = NormalizedCompanyInfo(
        ticker="AAPL",
        name="Apple Inc.",
        sector="Technology",
        country="US",
        employees=164000,
        source="yfinance",
        fetched_at=now,
    )
    assert data.name == "Apple Inc."


def test_ingestion_result():
    result = IngestionResult(
        ticker="AAPL", price=True, fundamentals=True, source="yfinance", cached=True
    )
    assert result.price
    assert result.fundamentals
    assert result.cached


def test_cache_status():
    now = datetime.now(timezone.utc)
    status = CacheStatus(
        ticker="AAPL", price_fresh=True, fundamentals_fresh=False, price_cached_at=now
    )
    assert status.price_fresh
    assert not status.fundamentals_fresh
