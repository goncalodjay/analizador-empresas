from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.providers.base import AbstractMarketDataProvider
from app.schemas.ingestion import NormalizedFundamentals, NormalizedPriceData

NEWSAPI_BASE = "https://newsapi.org/v2"


class NewsAPIProvider(AbstractMarketDataProvider):
    name = "newsapi"
    requires_api_key = True

    @property
    def _api_key(self) -> str:
        return settings.NEWSAPI_API_KEY

    async def _get(self, endpoint: str, params: dict) -> dict:
        if not self._api_key:
            raise ValueError("NewsAPI key not configured")

        params["apiKey"] = self._api_key
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{NEWSAPI_BASE}{endpoint}", params=params, timeout=15
            )
            resp.raise_for_status()
            return resp.json()

    async def fetch_price(self, ticker: str) -> NormalizedPriceData:
        raise NotImplementedError("NewsAPI does not provide price data")

    async def fetch_fundamentals(self, ticker: str) -> NormalizedFundamentals:
        raise NotImplementedError("NewsAPI does not provide fundamental data")

    async def fetch_news(
        self, ticker: str, limit: int = 10
    ) -> dict:
        ticker_upper = ticker.upper()
        data = await self._get(
            "/everything",
            {
                "q": ticker_upper,
                "pageSize": limit,
                "sortBy": "publishedAt",
                "language": "en",
            },
        )
        return {
            "ticker": ticker_upper,
            "articles": data.get("articles", []),
            "total": data.get("totalResults", 0),
            "source": self.name,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }

    async def fetch_sector_news(
        self, sector: str, limit: int = 10
    ) -> dict:
        data = await self._get(
            "/everything",
            {
                "q": f"{sector} stocks market",
                "pageSize": limit,
                "sortBy": "publishedAt",
                "language": "en",
            },
        )
        return {
            "sector": sector,
            "articles": data.get("articles", []),
            "total": data.get("totalResults", 0),
            "source": self.name,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
