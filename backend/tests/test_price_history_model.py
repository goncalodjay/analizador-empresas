"""Tests for PriceHistory SQLAlchemy model structure (RED — model not yet created)."""
import uuid
from datetime import date, datetime

import pytest
from sqlalchemy import inspect, UniqueConstraint
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool


TEST_DATABASE_URL = "sqlite+aiosqlite://"


@pytest.mark.asyncio
async def test_price_history_table_name():
    """PriceHistory.__tablename__ must be 'price_history'."""
    from app.models.price_history import PriceHistory
    assert PriceHistory.__tablename__ == "price_history"


@pytest.mark.asyncio
async def test_price_history_columns_exist():
    """PriceHistory must have the required columns."""
    from app.models.price_history import PriceHistory

    mapper = inspect(PriceHistory)
    column_names = {c.key for c in mapper.columns}
    required = {"id", "ticker", "date", "open", "high", "low", "close", "volume", "source", "fetched_at"}
    assert required.issubset(column_names), f"Missing columns: {required - column_names}"


@pytest.mark.asyncio
async def test_price_history_id_is_uuid():
    """id column must default to a UUID value."""
    from app.models.price_history import PriceHistory

    mapper = inspect(PriceHistory)
    id_col = mapper.columns["id"]
    assert id_col.primary_key is True


@pytest.mark.asyncio
async def test_price_history_unique_constraint():
    """Table must have UniqueConstraint on (ticker, date) named 'uix_price_history_ticker_date'."""
    from app.models.price_history import PriceHistory

    table = PriceHistory.__table__
    unique_constraints = [
        c for c in table.constraints
        if isinstance(c, UniqueConstraint)
    ]
    names = {c.name for c in unique_constraints}
    assert "uix_price_history_ticker_date" in names, (
        f"Expected constraint 'uix_price_history_ticker_date', found: {names}"
    )


@pytest.mark.asyncio
async def test_price_history_create_table():
    """PriceHistory table can be created in a SQLite in-memory DB."""
    from app.core.base import Base
    from sqlalchemy import text
    # Import the model so it registers with metadata
    import app.models.price_history  # noqa: F401

    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='price_history'")
        )
        rows = result.fetchall()
        assert len(rows) == 1, "price_history table was not created"

    await engine.dispose()


@pytest.mark.asyncio
async def test_price_history_instantiation():
    """PriceHistory can be instantiated with expected fields."""
    from app.models.price_history import PriceHistory
    from decimal import Decimal

    bar = PriceHistory(
        ticker="AAPL",
        date=date(2025, 1, 15),
        open=Decimal("150.0000"),
        high=Decimal("155.0000"),
        low=Decimal("149.0000"),
        close=Decimal("153.0000"),
        volume=1_000_000,
        source="yfinance",
    )
    assert bar.ticker == "AAPL"
    assert bar.date == date(2025, 1, 15)
    assert bar.close == Decimal("153.0000")
    assert bar.source == "yfinance"
