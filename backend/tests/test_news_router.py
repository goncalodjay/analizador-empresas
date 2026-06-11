"""Tests for GET /news/{ticker} router."""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from app.schemas.news import NewsFeedResponse, NewsItemOut


SAMPLE_ITEMS = [
    NewsItemOut(
        headline="Apple hits record",
        summary="Shares soared.",
        source_name="Reuters",
        url="https://reuters.com/apple-1",
        published_at=datetime(2026, 6, 10, 10, 0, 0, tzinfo=timezone.utc),
    )
]

CACHE_HIT_RESPONSE = NewsFeedResponse(
    ticker="AAPL",
    available=True,
    source="cache",
    items=SAMPLE_ITEMS,
    cached_at=datetime(2026, 6, 10, 9, 0, 0, tzinfo=timezone.utc),
    freshness="live",
    count=1,
)

DB_FALLBACK_RESPONSE = NewsFeedResponse(
    ticker="MSFT",
    available=True,
    source="db",
    items=SAMPLE_ITEMS,
    cached_at=None,
    freshness="stale",
    count=1,
)

EMPTY_RESPONSE = NewsFeedResponse(
    ticker="TSLA",
    available=False,
    source="none",
    items=[],
    cached_at=None,
    freshness=None,
    count=0,
)


@pytest.mark.asyncio
async def test_news_router_requires_auth(async_client):
    """Unauthenticated request to /news/AAPL must return 401."""
    response = await async_client.get("/news/AAPL")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_news_router_cache_hit(async_client):
    """Authenticated request with cache hit returns 200 with source='cache'."""
    from app.api.deps import get_current_user
    from app.core.database import get_db
    from app.main import app

    mock_user = MagicMock()
    mock_user.id = "test-user-id"

    with patch("app.api.news.NewsService.get_news", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = CACHE_HIT_RESPONSE
        app.dependency_overrides[get_current_user] = lambda: mock_user

        try:
            response = await async_client.get("/news/AAPL")
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["source"] == "cache"
    assert data["freshness"] == "live"
    assert len(data["items"]) == 1


@pytest.mark.asyncio
async def test_news_router_db_fallback(async_client):
    """Cache miss path returns 200 with source='db'."""
    from app.api.deps import get_current_user
    from app.main import app

    mock_user = MagicMock()
    mock_user.id = "test-user-id"

    with patch("app.api.news.NewsService.get_news", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = DB_FALLBACK_RESPONSE
        app.dependency_overrides[get_current_user] = lambda: mock_user

        try:
            response = await async_client.get("/news/MSFT")
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    data = response.json()
    assert data["source"] == "db"
    assert data["freshness"] == "stale"


@pytest.mark.asyncio
async def test_news_router_empty_no_provider(async_client):
    """No provider, no data: returns 200 with empty items and source='none'."""
    from app.api.deps import get_current_user
    from app.main import app

    mock_user = MagicMock()
    mock_user.id = "test-user-id"

    with patch("app.api.news.NewsService.get_news", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = EMPTY_RESPONSE
        app.dependency_overrides[get_current_user] = lambda: mock_user

        try:
            response = await async_client.get("/news/TSLA")
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["source"] == "none"
    assert data["available"] is False


@pytest.mark.asyncio
async def test_news_router_invalid_ticker_too_long(async_client):
    """Ticker longer than 10 chars returns 422."""
    from app.api.deps import get_current_user
    from app.main import app

    mock_user = MagicMock()
    mock_user.id = "test-user-id"
    app.dependency_overrides[get_current_user] = lambda: mock_user

    try:
        response = await async_client.get("/news/TOOLONGTICKERX")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_news_router_invalid_ticker_non_alphanumeric(async_client):
    """Non-alphanumeric ticker returns 422."""
    from app.api.deps import get_current_user
    from app.main import app

    mock_user = MagicMock()
    mock_user.id = "test-user-id"
    app.dependency_overrides[get_current_user] = lambda: mock_user

    try:
        response = await async_client.get("/news/AA!PL")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 422
