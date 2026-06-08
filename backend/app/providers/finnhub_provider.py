from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

import httpx

from app.core.config import settings
from app.providers.base import AbstractMarketDataProvider
from app.schemas.ingestion import NormalizedFundamentals, NormalizedPriceData

FINNHUB_BASE = "https://finnhub.io/api/v1"


class FinnhubProvider(AbstractMarketDataProvider):
    name = "finnhub"
    rate_limit_per_minute = 60
    requires_api_key = True

    @property
    def _api_key(self) -> str:
        return settings.FINNHUB_API_KEY

    async def _get(self, endpoint: str, params: dict | None = None) -> dict:
        if not self._api_key:
            raise ValueError("Finnhub API key not configured")

        url = f"{FINNHUB_BASE}{endpoint}"
        req_params = {"token": self._api_key}
        if params:
            req_params.update(params)

        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=req_params, timeout=15)
            resp.raise_for_status()
            return resp.json()

    async def fetch_price(self, ticker: str) -> NormalizedPriceData:
        data = await self._get("/quote", {"symbol": ticker.upper()})
        now = datetime.now(timezone.utc)

        return NormalizedPriceData(
            ticker=ticker.upper(),
            date=now,
            open=Decimal(str(round(data.get("o", 0), 4))),
            high=Decimal(str(round(data.get("h", 0), 4))),
            low=Decimal(str(round(data.get("l", 0), 4))),
            close=Decimal(str(round(data.get("c", 0), 4))),
            volume=int(data.get("v", 0)),
            source=self.name,
            fetched_at=now,
        )

    async def fetch_fundamentals(self, ticker: str) -> NormalizedFundamentals:
        ticker_upper = ticker.upper()
        profile = await self._get("/stock/profile2", {"symbol": ticker_upper})
        metrics = await self._get("/stock/metric", {"symbol": ticker_upper})
        metric_data = metrics.get("metric", {}) if metrics else {}
        now = datetime.now(timezone.utc)

        return NormalizedFundamentals(
            ticker=ticker_upper,
            pe_ratio=self._safe_decimal(metric_data.get("peBasicExclExtraTTM")),
            pb_ratio=self._safe_decimal(metric_data.get("pbAnnual")),
            market_cap=profile.get("marketCapitalization"),
            sector=profile.get("finnhubIndustry"),
            beta=self._safe_decimal(metric_data.get("beta")),
            eps=self._safe_decimal(metric_data.get("epsBasicExclExtraItemsTTM")),
            source=self.name,
            fetched_at=now,
        )

    async def fetch_analyst_ratings(self, ticker: str) -> dict:
        data = await self._get(
            "/stock/recommendation", {"symbol": ticker.upper()}
        )
        return {"ticker": ticker.upper(), "ratings": data, "source": self.name}

    async def fetch_insider_transactions(self, ticker: str) -> dict:
        data = await self._get(
            "/stock/insider-transactions", {"symbol": ticker.upper()}
        )
        return {
            "ticker": ticker.upper(),
            "transactions": data.get("data", []),
            "source": self.name,
        }

    async def fetch_earnings_surprises(self, ticker: str) -> dict:
        data = await self._get(
            "/stock/earnings", {"symbol": ticker.upper()}
        )
        return {
            "ticker": ticker.upper(),
            "earnings": data,
            "source": self.name,
        }

    @staticmethod
    def _safe_decimal(value) -> Decimal | None:
        if value is None:
            return None
        try:
            d = Decimal(str(value))
            return d if d.is_finite() else None
        except InvalidOperation:
            return None
