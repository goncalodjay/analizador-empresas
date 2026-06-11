import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.news import NewsFeedResponse
from app.services.cache_service import CacheService
from app.services.news_service import NewsService

router = APIRouter(prefix="/news", tags=["news"])

_TICKER_RE = re.compile(r"^[A-Za-z0-9]{1,10}$")


@router.get("/{ticker}", response_model=NewsFeedResponse)
async def get_ticker_news(
    ticker: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return the latest news for a ticker.

    Cache-first: Redis (live) → Postgres fallback (stale) → empty response when
    no provider is configured. Never returns 404 or 500 for missing data.
    """
    if not _TICKER_RE.match(ticker):
        raise HTTPException(
            status_code=422,
            detail="Ticker must be alphanumeric and at most 10 characters.",
        )

    cache = CacheService()
    service = NewsService()
    return await service.get_news(ticker, db, cache)
