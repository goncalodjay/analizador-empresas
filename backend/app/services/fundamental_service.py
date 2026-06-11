import json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from app.providers.factory import ProviderFactory
from app.schemas.analysis import (
    AnalystData,
    DividendData,
    DividendPayment,
    EarningsData,
    EarningsSurprise,
    FundamentalMetrics,
    MetricCard,
)
from app.services.cache_service import CacheService


class FundamentalService:

    def __init__(self):
        self.cache = CacheService()
        self.provider = ProviderFactory.get_price_provider()

    async def compute(self, ticker: str) -> FundamentalMetrics | None:
        ticker_upper = ticker.upper()
        key = self.cache.build_key(self.provider.name, "fundamentals", ticker_upper)
        raw = await self.cache.get(key)

        if raw is None:
            return None

        source = raw.get("source", self.provider.name)
        fetched_at = self._parse_dt(raw.get("fetched_at"))

        return FundamentalMetrics(
            pe_trailing=self._card("P/E (Trailing)", raw.get("pe_ratio"), "valuation", source, fetched_at),
            pe_forward=self._card("P/E (Forward)", self._forward_pe(raw), "valuation", source, fetched_at, "computed"),
            pb_ratio=self._card("P/B Ratio", raw.get("pb_ratio"), "valuation", source, fetched_at),
            eps=self._card("EPS (TTM)", raw.get("eps"), "valuation", source, fetched_at),
            revenue_growth_yoy=self._card("Revenue Growth YoY", raw.get("revenue_growth_yoy"), "growth", source, fetched_at, "computed"),
            debt_to_equity=self._card("Debt/Equity", raw.get("debt_to_equity"), "financial_health", source, fetched_at, "computed"),
            current_ratio=self._card("Current Ratio", raw.get("current_ratio"), "financial_health", source, fetched_at, "computed"),
            free_cash_flow=self._card("Free Cash Flow (TTM)", raw.get("free_cash_flow"), "financial_health", source, fetched_at, "computed"),
            market_cap=self._card("Market Cap", self._format_market_cap(raw.get("market_cap")), "valuation", source, fetched_at),
            beta=self._card("Beta", raw.get("beta"), "valuation", source, fetched_at),
        )

    async def get_dividends(self, ticker: str) -> DividendData:
        ticker_upper = ticker.upper()
        key = self.cache.build_key(self.provider.name, "dividends", ticker_upper)
        raw = await self.cache.get(key)

        if raw is None:
            return DividendData()

        return DividendData(
            current_yield=self._safe_str(raw.get("yield_pct")),
            payout_ratio=None,
            growth_years=0,
            history=[
                DividendPayment(
                    ex_date=d.get("ex_date"),
                    amount=Decimal(str(d.get("amount", 0))),
                )
                for d in (raw if isinstance(raw, list) else [])
                if isinstance(d, dict)
            ],
        )

    async def get_earnings(self, ticker: str) -> EarningsData:
        return EarningsData()

    async def get_analysts(self, ticker: str) -> AnalystData:
        return AnalystData()

    async def get_price(self, ticker: str) -> Decimal | None:
        ticker_upper = ticker.upper()
        key = self.cache.build_key(self.provider.name, "price", ticker_upper)
        raw = await self.cache.get(key)
        if raw is None:
            return None
        try:
            return Decimal(str(raw.get("close", 0)))
        except (InvalidOperation, ValueError):
            return None

    async def get_price_date(self, ticker: str) -> datetime | None:
        ticker_upper = ticker.upper()
        key = self.cache.build_key(self.provider.name, "price", ticker_upper)
        raw = await self.cache.get(key)
        if raw is None:
            return None
        return self._parse_dt(raw.get("fetched_at"))

    @staticmethod
    def _card(
        label: str,
        value,
        category: str,
        source: str,
        fetched_at: datetime | None,
        nature: str = "data_driven",
    ) -> MetricCard:
        str_val = None
        if value is not None:
            try:
                d = Decimal(str(value))
                str_val = str(round(d, 2))
            except (InvalidOperation, ValueError):
                str_val = str(value)
        return MetricCard(
            label=label,
            value=str_val,
            category=category,
            nature=nature,
            source=source,
            fetched_at=fetched_at,
        )

    @staticmethod
    def _forward_pe(raw: dict) -> str | None:
        growth = raw.get("revenue_growth_yoy")
        trailing = raw.get("pe_ratio")
        if growth is None or trailing is None:
            return None
        try:
            g = Decimal(str(growth)) / 100
            t = Decimal(str(trailing))
            forward = t / (1 + g) if g > -1 else None
            return str(round(forward, 2)) if forward and forward > 0 else None
        except (InvalidOperation, ValueError, ZeroDivisionError):
            return None

    @staticmethod
    def _format_market_cap(value) -> str | None:
        if value is None:
            return None
        try:
            cap = int(value)
            if cap >= 1_000_000_000_000:
                return f"${cap / 1_000_000_000_000:.2f}T"
            elif cap >= 1_000_000_000:
                return f"${cap / 1_000_000_000:.2f}B"
            elif cap >= 1_000_000:
                return f"${cap / 1_000_000:.2f}M"
            return f"${cap:,}"
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _parse_dt(val) -> datetime | None:
        if val is None:
            return None
        try:
            return datetime.fromisoformat(str(val))
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_str(val) -> str | None:
        if val is None:
            return None
        return str(val)
