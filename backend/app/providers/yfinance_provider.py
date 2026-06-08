from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation

import yfinance as yf

from app.providers.base import AbstractMarketDataProvider
from app.schemas.ingestion import (
    NormalizedCompanyInfo,
    NormalizedDividend,
    NormalizedFundamentals,
    NormalizedPriceData,
)


class YFinanceProvider(AbstractMarketDataProvider):
    name = "yfinance"
    requires_api_key = False

    async def fetch_price(self, ticker: str) -> NormalizedPriceData:
        t = yf.Ticker(ticker)
        hist = t.history(period="1d")
        now = datetime.now(timezone.utc)

        if hist.empty:
            raise ValueError(f"No price data for {ticker}")

        row = hist.iloc[-1]
        return NormalizedPriceData(
            ticker=ticker.upper(),
            date=now,
            open=Decimal(str(round(row["Open"], 4))),
            high=Decimal(str(round(row["High"], 4))),
            low=Decimal(str(round(row["Low"], 4))),
            close=Decimal(str(round(row["Close"], 4))),
            volume=int(row["Volume"]),
            source=self.name,
            fetched_at=now,
        )

    async def fetch_fundamentals(
        self, ticker: str
    ) -> NormalizedFundamentals:
        t = yf.Ticker(ticker)
        info = t.info or {}
        now = datetime.now(timezone.utc)

        return NormalizedFundamentals(
            ticker=ticker.upper(),
            pe_ratio=self._safe_decimal(info.get("trailingPE")),
            pb_ratio=self._safe_decimal(info.get("priceToBook")),
            market_cap=info.get("marketCap"),
            sector=info.get("sector"),
            industry=info.get("industry"),
            beta=self._safe_decimal(info.get("beta")),
            eps=self._safe_decimal(info.get("trailingEps")),
            source=self.name,
            fetched_at=now,
        )

    async def fetch_dividends(
        self, ticker: str
    ) -> list[NormalizedDividend]:
        t = yf.Ticker(ticker)
        div_history = t.dividends
        info = t.info or {}
        now = datetime.now(timezone.utc)
        div_yield = self._safe_decimal(info.get("dividendYield"))

        results: list[NormalizedDividend] = []
        for dt, amount in div_history.tail(12).items():
            if hasattr(dt, "to_pydatetime"):
                dt = dt.to_pydatetime().date()
            elif isinstance(dt, datetime):
                dt = dt.date()

            results.append(
                NormalizedDividend(
                    ticker=ticker.upper(),
                    ex_date=dt,
                    amount=Decimal(str(round(float(amount), 4))),
                    yield_pct=div_yield,
                    source=self.name,
                    fetched_at=now,
                )
            )
        return results

    async def fetch_company_info(
        self, ticker: str
    ) -> NormalizedCompanyInfo:
        t = yf.Ticker(ticker)
        info = t.info or {}
        now = datetime.now(timezone.utc)

        return NormalizedCompanyInfo(
            ticker=ticker.upper(),
            name=info.get("longName") or info.get("shortName") or ticker,
            sector=info.get("sector"),
            industry=info.get("industry"),
            country=info.get("country"),
            employees=info.get("fullTimeEmployees"),
            description=info.get("longBusinessSummary"),
            source=self.name,
            fetched_at=now,
        )

    @staticmethod
    def _safe_decimal(value) -> Decimal | None:
        if value is None:
            return None
        try:
            d = Decimal(str(value))
            return d if d.is_finite() else None
        except InvalidOperation:
            return None
