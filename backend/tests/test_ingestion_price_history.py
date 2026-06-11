"""Tests for IngestionService._persist_price_history (RED — method not yet implemented).

Covers:
  SC-01: first ingest calls with period='1y' and upserts rows
  SC-02: re-ingest calls with period='7d' and performs ON CONFLICT upsert
  SC-03: provider exception sets result.error, does not raise
"""
from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest

from app.schemas.ingestion import IngestionResult, NormalizedPriceBar


TICKER = "AAPL"


def _make_bars(n: int, period_start: date = date(2025, 1, 2)) -> list[NormalizedPriceBar]:
    bars = []
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    for i in range(n):
        d = period_start
        bars.append(
            NormalizedPriceBar(
                ticker=TICKER,
                date=d,
                open=Decimal("150.0000"),
                high=Decimal("155.0000"),
                low=Decimal("149.0000"),
                close=Decimal("153.0000"),
                volume=1_000_000,
                source="yfinance",
                fetched_at=now,
            )
        )
        period_start = period_start.replace(day=period_start.day + 1) if period_start.day < 28 else date(period_start.year, period_start.month + 1, 1)
    return bars


@pytest.mark.asyncio
async def test_first_ingest_fetches_1y_and_upserts():
    """SC-01: first ingest (no rows) fetches 1y, upserts ~252 rows, sets result.price_history=True."""
    from app.services.ingestion_service import IngestionService

    service = IngestionService()
    result = IngestionResult(ticker=TICKER, source="yfinance")
    bars = _make_bars(252)

    mock_provider = AsyncMock()
    mock_provider.fetch_price_history = AsyncMock(return_value=bars)

    mock_session = AsyncMock()
    # Simulate first ingest: SELECT returns no rows (fetchone returns None)
    mock_execute_result = MagicMock()
    mock_execute_result.fetchone.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_execute_result)
    mock_session.commit = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_session_factory = MagicMock(return_value=mock_session)

    with (
        patch("app.services.ingestion_service.ProviderFactory") as mock_factory,
        patch("app.services.ingestion_service._get_async_session_local", return_value=mock_session_factory),
    ):
        mock_factory.get_price_provider.return_value = mock_provider
        await service._persist_price_history(TICKER, result)

    # Provider must have been called with period="1y"
    mock_provider.fetch_price_history.assert_called_once_with(TICKER, "1y")
    assert result.price_history is True
    assert result.error is None
    # execute must have been called at least twice: SELECT + INSERT upsert
    assert mock_session.execute.call_count >= 2


@pytest.mark.asyncio
async def test_reingest_fetches_7d_and_upserts():
    """SC-02: re-ingest (rows exist) fetches 7d, upserts with ON CONFLICT."""
    from app.services.ingestion_service import IngestionService

    service = IngestionService()
    result = IngestionResult(ticker=TICKER, source="yfinance")
    bars = _make_bars(7)

    mock_provider = AsyncMock()
    mock_provider.fetch_price_history = AsyncMock(return_value=bars)

    mock_session = AsyncMock()
    # Simulate re-ingest: SELECT returns an existing row
    mock_execute_result = MagicMock()
    mock_execute_result.fetchone.return_value = (1,)
    mock_session.execute = AsyncMock(return_value=mock_execute_result)
    mock_session.commit = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_session_factory = MagicMock(return_value=mock_session)

    with (
        patch("app.services.ingestion_service.ProviderFactory") as mock_factory,
        patch("app.services.ingestion_service._get_async_session_local", return_value=mock_session_factory),
    ):
        mock_factory.get_price_provider.return_value = mock_provider
        await service._persist_price_history(TICKER, result)

    mock_provider.fetch_price_history.assert_called_once_with(TICKER, "7d")
    assert result.price_history is True


@pytest.mark.asyncio
async def test_provider_exception_sets_result_error_does_not_raise():
    """SC-03: provider exception sets result.error, does not raise."""
    from app.services.ingestion_service import IngestionService

    service = IngestionService()
    result = IngestionResult(ticker=TICKER, source="yfinance")

    mock_provider = AsyncMock()
    mock_provider.fetch_price_history = AsyncMock(
        side_effect=RuntimeError("yfinance network error")
    )

    mock_session = AsyncMock()
    mock_execute_result = MagicMock()
    mock_execute_result.fetchone.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_execute_result)
    mock_session.commit = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_session_factory = MagicMock(return_value=mock_session)

    with (
        patch("app.services.ingestion_service.ProviderFactory") as mock_factory,
        patch("app.services.ingestion_service._get_async_session_local", return_value=mock_session_factory),
    ):
        mock_factory.get_price_provider.return_value = mock_provider
        # Must NOT raise
        await service._persist_price_history(TICKER, result)

    assert result.error is not None
    assert "yfinance network error" in result.error
    assert result.price_history is False


@pytest.mark.asyncio
async def test_empty_bars_list_skips_upsert():
    """When provider returns empty bars, no upsert statement is executed."""
    from app.services.ingestion_service import IngestionService

    service = IngestionService()
    result = IngestionResult(ticker=TICKER, source="yfinance")

    mock_provider = AsyncMock()
    mock_provider.fetch_price_history = AsyncMock(return_value=[])

    mock_session = AsyncMock()
    mock_execute_result = MagicMock()
    mock_execute_result.fetchone.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_execute_result)
    mock_session.commit = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_session_factory = MagicMock(return_value=mock_session)

    with (
        patch("app.services.ingestion_service.ProviderFactory") as mock_factory,
        patch("app.services.ingestion_service._get_async_session_local", return_value=mock_session_factory),
    ):
        mock_factory.get_price_provider.return_value = mock_provider
        await service._persist_price_history(TICKER, result)

    # Only the SELECT check was executed (1 call), no INSERT
    assert mock_session.execute.call_count == 1
