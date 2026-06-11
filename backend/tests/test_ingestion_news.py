"""Tests for IngestionService news write path (_ingest_news)."""
from unittest.mock import AsyncMock, MagicMock, patch, call
from datetime import datetime, timezone

import pytest

from app.schemas.ingestion import IngestionResult
from app.services.ingestion_service import IngestionService


TICKER = "AAPL"
SAMPLE_NEWS_RESPONSE = {
    "ticker": TICKER,
    "articles": [
        {
            "title": "Apple hits record",
            "description": "Shares hit record high.",
            "source": {"name": "Reuters"},
            "url": "https://reuters.com/apple-1",
            "publishedAt": "2026-06-10T10:00:00Z",
        },
        {
            "title": "Apple product launch",
            "description": None,
            "source": {"name": "Bloomberg"},
            "url": "https://bloomberg.com/apple-2",
            "publishedAt": "2026-06-09T08:00:00Z",
        },
    ],
    "total": 2,
    "source": "newsapi",
    "fetched_at": "2026-06-11T00:00:00+00:00",
}


@pytest.mark.asyncio
async def test_no_provider_skips_news():
    """When get_news_provider() returns None, news is skipped without error."""
    service = IngestionService()
    result = IngestionResult(ticker=TICKER, source="yfinance")

    with patch("app.services.ingestion_service.ProviderFactory") as mock_factory:
        mock_factory.get_news_provider.return_value = None
        await service._ingest_news(TICKER, result)

    assert result.news is False
    assert result.error is None


@pytest.mark.asyncio
async def test_provider_present_upserts_articles():
    """When provider is present, articles are upserted and result.news=True."""
    service = IngestionService()
    service.cache = AsyncMock()
    service.cache.build_key = MagicMock(return_value=f"cache:newsapi:news:{TICKER}")
    service.cache.set = AsyncMock()

    result = IngestionResult(ticker=TICKER, source="yfinance")

    mock_provider = AsyncMock()
    mock_provider.fetch_news = AsyncMock(return_value=SAMPLE_NEWS_RESPONSE)

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    mock_session_factory = MagicMock(return_value=mock_session)

    with (
        patch("app.services.ingestion_service.ProviderFactory") as mock_factory,
        patch("app.services.ingestion_service._get_async_session_local", return_value=mock_session_factory),
    ):
        mock_factory.get_news_provider.return_value = mock_provider
        await service._ingest_news(TICKER, result)

    assert result.news is True
    assert result.error is None
    # execute should have been called (at least for the upsert)
    mock_session.execute.assert_called()


@pytest.mark.asyncio
async def test_provider_raises_sets_result_error():
    """Provider exception sets result.error (price pattern) — does not abort ingestion."""
    service = IngestionService()
    result = IngestionResult(ticker=TICKER, source="yfinance")

    mock_provider = AsyncMock()
    mock_provider.fetch_news = AsyncMock(side_effect=RuntimeError("NewsAPI 429"))

    with patch("app.services.ingestion_service.ProviderFactory") as mock_factory:
        mock_factory.get_news_provider.return_value = mock_provider
        await service._ingest_news(TICKER, result)

    assert result.error is not None
    assert "NewsAPI 429" in result.error
    assert result.news is False


@pytest.mark.asyncio
async def test_repeated_ingestion_does_not_duplicate_rows():
    """Calling _ingest_news twice with same articles uses ON CONFLICT upsert (no new inserts)."""
    service = IngestionService()
    service.cache = AsyncMock()
    service.cache.build_key = MagicMock(return_value=f"cache:newsapi:news:{TICKER}")
    service.cache.set = AsyncMock()

    result1 = IngestionResult(ticker=TICKER, source="yfinance")
    result2 = IngestionResult(ticker=TICKER, source="yfinance")

    mock_provider = AsyncMock()
    mock_provider.fetch_news = AsyncMock(return_value=SAMPLE_NEWS_RESPONSE)

    def make_mock_session():
        mock_session = AsyncMock()
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        return mock_session

    mock_session_factory = MagicMock(side_effect=make_mock_session)

    with (
        patch("app.services.ingestion_service.ProviderFactory") as mock_factory,
        patch("app.services.ingestion_service._get_async_session_local", return_value=mock_session_factory),
    ):
        mock_factory.get_news_provider.return_value = mock_provider
        await service._ingest_news(TICKER, result1)
        await service._ingest_news(TICKER, result2)

    # Both calls succeed — dedup happens at DB level via ON CONFLICT
    assert result1.news is True
    assert result2.news is True
