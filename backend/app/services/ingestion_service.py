import asyncio
import json
import logging
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.core.database import _get_async_session_local
from app.models.news import NewsItem
from app.models.price_history import PriceHistory
from app.providers.factory import ProviderFactory
from app.schemas.ingestion import IngestionResult
from app.services.cache_service import CacheService
from app.services.portfolio_service import get_positions

logger = logging.getLogger(__name__)


class IngestionService:

    def __init__(self):
        self.cache = CacheService()

    async def ingest_ticker(self, ticker: str, user_id: str) -> IngestionResult:
        ticker_upper = ticker.upper()
        result = IngestionResult(ticker=ticker_upper, source="yfinance")
        provider = ProviderFactory.get_price_provider()

        try:
            price_key = self.cache.build_key(provider.name, "price", ticker_upper)
            price_result = await self.cache.get_or_fetch(
                price_key,
                "price",
                lambda: self._fetch_and_serialize(
                    provider.fetch_price(ticker_upper)
                ),
            )
            result.price = True
            result.cached = price_result["cached"]
        except Exception as e:
            result.error = str(e)

        try:
            fund_provider = ProviderFactory.get_fundamentals_provider()
            fund_key = self.cache.build_key(fund_provider.name, "fundamentals", ticker_upper)
            await self.cache.get_or_fetch(
                fund_key,
                "fundamentals",
                lambda: self._fetch_and_serialize(
                    fund_provider.fetch_fundamentals(ticker_upper)
                ),
            )
            result.fundamentals = True
        except Exception:
            pass

        await self._ingest_news(ticker_upper, result)

        try:
            await self._persist_price_history(ticker_upper, result)
        except Exception as e:
            logger.error("Price history ingestion failed for %s: %s", ticker_upper, e)
            result.error = str(e)

        return result

    async def ingest_portfolio(self, user_id: str) -> list[IngestionResult]:
        positions = await get_positions(None, user_id)
        tickers = {p.ticker for p in positions}
        tasks = [
            self.ingest_ticker(ticker, user_id)
            for ticker in tickers
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [
            r if not isinstance(r, BaseException) else IngestionResult(
                ticker="unknown", source="error", error=str(r)
            )
            for r in results
        ]

    async def ingest_all_tickers(
        self, tickers: list[str], user_id: str
    ) -> list[IngestionResult]:
        tasks = [self.ingest_ticker(t, user_id) for t in tickers]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [
            r if not isinstance(r, BaseException) else IngestionResult(
                ticker="unknown", source="error", error=str(r)
            )
            for r in results
        ]

    async def get_cache_status(self, ticker: str) -> dict:
        ticker_upper = ticker.upper()
        provider = ProviderFactory.get_price_provider()
        price_key = self.cache.build_key(provider.name, "price", ticker_upper)

        price_cached = await self.cache.get(price_key)
        fund_cached = await self.cache.get(
            self.cache.build_key(provider.name, "fundamentals", ticker_upper)
        )

        return {
            "ticker": ticker_upper,
            "price_cached": price_cached is not None,
            "fundamentals_cached": fund_cached is not None,
        }

    async def _ingest_news(self, ticker: str, result: IngestionResult) -> None:
        """Fetch, upsert, and cache news articles for a ticker.

        Uses the price error pattern: exceptions set result.error — they do NOT
        abort the price/fundamentals that already completed. Never bare-except.
        Opens its own DB session (ADR-2) so it is safe under asyncio.gather.
        """
        provider = ProviderFactory.get_news_provider()
        if provider is None:
            result.news = False
            return

        try:
            news_data = await provider.fetch_news(ticker, limit=20)
            articles = news_data.get("articles", [])

            # Persist articles with a URL via ON CONFLICT upsert
            session_factory = _get_async_session_local()
            async with session_factory() as session:
                for article in articles:
                    url = article.get("url")
                    if not url:
                        # Skip articles without a URL — they cannot be deduped
                        continue

                    published_raw = article.get("publishedAt") or article.get("published_at")
                    published_at = None
                    if published_raw:
                        try:
                            if isinstance(published_raw, str):
                                published_at = datetime.fromisoformat(
                                    published_raw.replace("Z", "+00:00")
                                )
                            elif isinstance(published_raw, datetime):
                                published_at = published_raw
                        except (ValueError, TypeError):
                            pass

                    source_raw = article.get("source", {})
                    source_name = (
                        source_raw.get("name", "") if isinstance(source_raw, dict)
                        else str(source_raw)
                    )
                    headline = article.get("title") or article.get("headline", "")
                    summary = article.get("description") or article.get("summary")

                    stmt = pg_insert(NewsItem).values(
                        ticker=ticker,
                        headline=headline,
                        summary=summary,
                        source_name=source_name,
                        url=url,
                        published_at=published_at,
                        fetched_at=datetime.now(timezone.utc),
                    ).on_conflict_do_update(
                        index_elements=["ticker", "url"],
                        set_={
                            "headline": headline,
                            "summary": summary,
                            "source_name": source_name,
                            "published_at": published_at,
                            "fetched_at": datetime.now(timezone.utc),
                        },
                    )
                    await session.execute(stmt)

                await session.commit()

            # Write the full fetch payload to cache
            cache_key = self.cache.build_key("newsapi", "news", ticker)
            await self.cache.set(cache_key, news_data, "news")

            result.news = True

        except Exception as e:
            # Price pattern: record error, do not raise — price/fundamentals already done
            logger.error("News ingestion failed for %s: %s", ticker, e)
            result.error = str(e)
            result.news = False

    async def _persist_price_history(self, ticker: str, result: IngestionResult) -> None:
        """Fetch and upsert OHLC price history for a ticker.

        First-ingest detection: no rows → 1y backfill; existing rows → 7d refresh.
        Uses ON CONFLICT (ticker, date) DO UPDATE semantics.
        Follows the price error pattern: exceptions set result.error, do NOT raise.
        Opens its own DB session (ADR-2) safe under asyncio.gather.
        """
        provider = ProviderFactory.get_price_provider()

        try:
            session_factory = _get_async_session_local()
            async with session_factory() as session:
                # First-ingest detection
                check_stmt = text(
                    "SELECT 1 FROM price_history WHERE ticker = :ticker LIMIT 1"
                )
                check_result = await session.execute(check_stmt, {"ticker": ticker})
                existing = check_result.fetchone()
                period = "7d" if existing else "1y"

            bars = await provider.fetch_price_history(ticker, period)

            if not bars:
                return

            rows = [
                {
                    "ticker": bar.ticker,
                    "date": bar.date,
                    "open": bar.open,
                    "high": bar.high,
                    "low": bar.low,
                    "close": bar.close,
                    "volume": bar.volume,
                    "source": bar.source,
                    "fetched_at": bar.fetched_at,
                }
                for bar in bars
            ]

            async with session_factory() as session:
                stmt = pg_insert(PriceHistory).values(rows)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["ticker", "date"],
                    set_={
                        "open": stmt.excluded.open,
                        "high": stmt.excluded.high,
                        "low": stmt.excluded.low,
                        "close": stmt.excluded.close,
                        "volume": stmt.excluded.volume,
                        "source": stmt.excluded.source,
                        "fetched_at": stmt.excluded.fetched_at,
                    },
                )
                await session.execute(stmt)
                await session.commit()

            result.price_history = True

        except Exception as e:
            logger.error("Price history ingestion failed for %s: %s", ticker, e)
            result.error = str(e)
            result.price_history = False

    @staticmethod
    async def _fetch_and_serialize(coro):
        result = await coro
        return json.loads(result.model_dump_json())
