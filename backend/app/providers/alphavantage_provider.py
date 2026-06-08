from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

import httpx

from app.core.config import settings
from app.providers.base import AbstractMarketDataProvider
from app.schemas.ingestion import NormalizedPriceData

ALPHA_VANTAGE_BASE = "https://www.alphavantage.co/query"


class AlphaVantageProvider(AbstractMarketDataProvider):
    name = "alphavantage"
    rate_limit_per_minute = 25
    requires_api_key = True

    @property
    def _api_key(self) -> str:
        return settings.ALPHA_VANTAGE_API_KEY

    async def _get(self, function: str, symbol: str, **extra) -> dict:
        if not self._api_key:
            raise ValueError("Alpha Vantage API key not configured")

        params = {
            "function": function,
            "symbol": symbol.upper(),
            "apikey": self._api_key,
            **extra,
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                ALPHA_VANTAGE_BASE, params=params, timeout=15
            )
            resp.raise_for_status()
            data = resp.json()
            if "Error Message" in data or "Note" in data:
                raise ValueError(
                    data.get("Error Message") or data.get("Note", "API limit reached")
                )
            return data

    async def fetch_price(self, ticker: str) -> NormalizedPriceData:
        raise NotImplementedError("Use YFinance provider for prices")

    async def fetch_fundamentals(self, ticker: str):
        raise NotImplementedError("Use YFinance provider for fundamentals")

    async def fetch_rsi(self, ticker: str) -> dict:
        data = await self._get("RSI", ticker, interval="daily", time_period=14, series_type="close")
        return {"ticker": ticker.upper(), "rsi": data, "source": self.name}

    async def fetch_macd(self, ticker: str) -> dict:
        data = await self._get("MACD", ticker, interval="daily", series_type="close")
        return {"ticker": ticker.upper(), "macd": data, "source": self.name}

    async def fetch_ema(self, ticker: str) -> dict:
        data = await self._get("EMA", ticker, interval="daily", time_period=50, series_type="close")
        return {"ticker": ticker.upper(), "ema": data, "source": self.name}

    async def fetch_sma(self, ticker: str) -> dict:
        data = await self._get("SMA", ticker, interval="daily", time_period=50, series_type="close")
        return {"ticker": ticker.upper(), "sma": data, "source": self.name}
