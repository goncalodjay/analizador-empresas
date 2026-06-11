"""NewsService — cache-first read path for news items.

Follows the established read-service pattern (FundamentalService, TechnicalService).
Cache-first: Redis (live) → Postgres fallback (stale) → empty when neither available.

NOTE: News sentiment is NOT wired into health_score/analyst_sentiment in v1.
TODO(v2): feed sentiment_score into HealthScoreEngine when sentiment analysis is added.
"""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.news import NewsItem
from app.schemas.news import NewsFeedResponse, NewsItemOut
from app.services.cache_service import CacheService


class NewsService:

    @staticmethod
    def _build_cache_key(cache: CacheService, ticker: str) -> str:
        return cache.build_key("newsapi", "news", ticker.upper())

    @staticmethod
    def _parse_cached_items(articles: list[dict]) -> list[NewsItemOut]:
        items = []
        for article in articles:
            try:
                published_raw = article.get("publishedAt") or article.get("published_at")
                published_at = None
                if published_raw:
                    if isinstance(published_raw, str):
                        published_at = datetime.fromisoformat(
                            published_raw.replace("Z", "+00:00")
                        )
                    elif isinstance(published_raw, datetime):
                        published_at = published_raw

                items.append(
                    NewsItemOut(
                        headline=article.get("title") or article.get("headline", ""),
                        summary=article.get("description") or article.get("summary"),
                        source_name=(
                            article.get("source", {}).get("name")
                            if isinstance(article.get("source"), dict)
                            else article.get("source_name", "")
                        ),
                        url=article.get("url"),
                        published_at=published_at,
                    )
                )
            except Exception:
                # Skip malformed articles — never crash the read path
                continue
        return items

    async def get_news(
        self,
        ticker: str,
        db: AsyncSession,
        cache: CacheService,
    ) -> NewsFeedResponse:
        ticker_upper = ticker.upper()
        cache_key = self._build_cache_key(cache, ticker_upper)

        # 1. Cache-first: check Redis
        cached = await cache.get(cache_key)
        if cached is not None:
            articles = cached.get("articles", [])
            items = self._parse_cached_items(articles)
            cached_at_raw = cached.get("_cached_at")
            cached_at = None
            if cached_at_raw:
                try:
                    cached_at = datetime.fromisoformat(
                        cached_at_raw.replace("Z", "+00:00")
                    )
                except (ValueError, AttributeError):
                    pass
            return NewsFeedResponse(
                ticker=ticker_upper,
                available=True,
                source="cache",
                items=items,
                cached_at=cached_at,
                freshness="live",
                count=len(items),
            )

        # 2. Cache miss: fall back to Postgres
        stmt = (
            select(NewsItem)
            .where(NewsItem.ticker == ticker_upper)
            .order_by(NewsItem.published_at.desc().nulls_last())
            .limit(20)
        )
        result = await db.execute(stmt)
        rows = result.scalars().all()

        if not rows:
            return NewsFeedResponse(
                ticker=ticker_upper,
                available=False,
                source="none",
                items=[],
                cached_at=None,
                freshness=None,
                count=0,
            )

        items = [
            NewsItemOut(
                headline=row.headline,
                summary=row.summary,
                source_name=row.source_name,
                url=row.url,
                published_at=row.published_at,
            )
            for row in rows
        ]

        return NewsFeedResponse(
            ticker=ticker_upper,
            available=True,
            source="db",
            items=items,
            cached_at=None,
            freshness="stale",
            count=len(items),
        )
