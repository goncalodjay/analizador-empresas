"""Tests for NewsService.get_news — cache-first read path."""
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.news import NewsFeedResponse, NewsItemOut
from app.services.news_service import NewsService


TICKER = "AAPL"
CACHE_KEY = f"cache:newsapi:news:{TICKER}"

SAMPLE_ARTICLES = [
    {
        "headline": "Apple hits record high",
        "summary": "Apple shares soared.",
        "source_name": "Reuters",
        "url": "https://reuters.com/apple-1",
        "published_at": "2026-06-10T10:00:00+00:00",
    }
]


@pytest.fixture
def news_service():
    return NewsService()


@pytest.mark.asyncio
async def test_cache_hit_returns_live_source(news_service):
    """Cache hit should return source='cache' and freshness='live'."""
    cached_payload = {
        "ticker": TICKER,
        "articles": SAMPLE_ARTICLES,
        "source": "cache",
        "_cached_at": "2026-06-10T09:00:00+00:00",
    }

    mock_cache = AsyncMock()
    mock_cache.get = AsyncMock(return_value=cached_payload)
    mock_cache.build_key = MagicMock(return_value=CACHE_KEY)

    mock_db = AsyncMock()

    result = await news_service.get_news(TICKER, mock_db, mock_cache)

    assert isinstance(result, NewsFeedResponse)
    assert result.source == "cache"
    assert result.freshness == "live"
    assert result.available is True
    assert len(result.items) == 1
    assert result.items[0].headline == "Apple hits record high"
    # DB should not be queried on cache hit
    mock_db.execute.assert_not_called()


@pytest.mark.asyncio
async def test_cache_miss_queries_db(news_service):
    """Cache miss should fall back to Postgres and return source='db'."""
    from unittest.mock import MagicMock

    mock_cache = AsyncMock()
    mock_cache.get = AsyncMock(return_value=None)
    mock_cache.build_key = MagicMock(return_value=CACHE_KEY)

    # Build a mock news item row
    mock_row = MagicMock()
    mock_row.headline = "Apple earnings beat"
    mock_row.summary = None
    mock_row.source_name = "Bloomberg"
    mock_row.url = "https://bloomberg.com/apple-2"
    mock_row.published_at = datetime(2026, 6, 10, 8, 0, 0, tzinfo=timezone.utc)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_row]

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await news_service.get_news(TICKER, mock_db, mock_cache)

    assert result.source == "db"
    assert result.freshness == "stale"
    assert result.available is True
    assert len(result.items) == 1
    assert result.items[0].headline == "Apple earnings beat"
    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_no_provider_no_rows_returns_empty(news_service):
    """No cache and no DB rows should return available=False, empty items, source='none'."""
    mock_cache = AsyncMock()
    mock_cache.get = AsyncMock(return_value=None)
    mock_cache.build_key = MagicMock(return_value=CACHE_KEY)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    result = await news_service.get_news(TICKER, mock_db, mock_cache)

    assert result.available is False
    assert result.items == []
    assert result.source == "none"
    assert result.cached_at is None
