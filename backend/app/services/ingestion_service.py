import asyncio
import json
from datetime import datetime, timezone

from app.providers.factory import ProviderFactory
from app.schemas.ingestion import IngestionResult
from app.services.cache_service import CacheService
from app.services.portfolio_service import get_positions


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

    @staticmethod
    async def _fetch_and_serialize(coro):
        result = await coro
        return json.loads(result.model_dump_json())
