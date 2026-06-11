"""Tests for GET /prices/{ticker} endpoint.

Covers SC-04 (200 + correct body), SC-05 (200 empty points for unknown ticker),
SC-06 (401 no token), SC-07 (400 from>to).
"""
from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.schemas.prices import PricePoint, PriceSeriesResponse


SAMPLE_POINTS = [
    PricePoint(
        date=date(2025, 6, 10),
        open=Decimal("150.0000"),
        high=Decimal("155.0000"),
        low=Decimal("149.0000"),
        close=Decimal("153.0000"),
        volume=1_000_000,
    ),
    PricePoint(
        date=date(2025, 6, 11),
        open=Decimal("153.0000"),
        high=Decimal("158.0000"),
        low=Decimal("152.0000"),
        close=Decimal("156.0000"),
        volume=1_200_000,
    ),
]

SAMPLE_RESPONSE = PriceSeriesResponse(
    ticker="AAPL",
    points=SAMPLE_POINTS,
    from_date=date(2025, 6, 10),
    to_date=date(2025, 6, 11),
    count=2,
    source="yfinance",
    freshness="fresh",
    fetched_at=datetime(2025, 6, 11, 12, 0, 0, tzinfo=timezone.utc),
)

EMPTY_RESPONSE = PriceSeriesResponse(
    ticker="FAKE",
    points=[],
    from_date=date(2025, 1, 1),
    to_date=date(2025, 12, 31),
    count=0,
    source="yfinance",
    freshness="stale",
    fetched_at=None,
)


@pytest.mark.asyncio
async def test_prices_endpoint_requires_auth(async_client):
    """SC-06: Unauthenticated request returns 401."""
    response = await async_client.get("/prices/AAPL")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_prices_endpoint_returns_200_with_series(async_client):
    """SC-04: Authenticated request returns 200 with correct body."""
    from app.api.deps import get_current_user
    from app.main import app

    mock_user = MagicMock()
    mock_user.id = "user-1"

    with patch(
        "app.api.prices.PriceHistoryService.get_series",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = SAMPLE_RESPONSE
        app.dependency_overrides[get_current_user] = lambda: mock_user

        try:
            response = await async_client.get(
                "/prices/AAPL?from=2025-06-10&to=2025-06-11"
            )
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "AAPL"
    assert body["source"] == "yfinance"
    assert "points" in body
    assert len(body["points"]) == 2


@pytest.mark.asyncio
async def test_prices_endpoint_returns_200_empty_for_unknown_ticker(async_client):
    """SC-05: Unknown ticker returns 200 with empty points array."""
    from app.api.deps import get_current_user
    from app.main import app

    mock_user = MagicMock()
    mock_user.id = "user-1"

    with patch(
        "app.api.prices.PriceHistoryService.get_series",
        new_callable=AsyncMock,
    ) as mock_get:
        mock_get.return_value = EMPTY_RESPONSE
        app.dependency_overrides[get_current_user] = lambda: mock_user

        try:
            response = await async_client.get("/prices/FAKE")
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "FAKE"
    assert body["points"] == []
    assert body["count"] == 0


@pytest.mark.asyncio
async def test_prices_endpoint_rejects_invalid_date_range(async_client):
    """SC-07: from > to returns 400."""
    from app.api.deps import get_current_user
    from app.main import app

    mock_user = MagicMock()
    app.dependency_overrides[get_current_user] = lambda: mock_user

    try:
        response = await async_client.get("/prices/AAPL?from=2025-12-31&to=2025-01-01")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 400
