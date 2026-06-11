from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation

from app.providers.base import AbstractMarketDataProvider
from app.schemas.ingestion import (
    NormalizedCompanyInfo,
    NormalizedDividend,
    NormalizedFundamentals,
    NormalizedPriceBar,
    NormalizedPriceData,
)


class YFinanceProvider(AbstractMarketDataProvider):
    name = "yfinance"
    requires_api_key = False

    @staticmethod
    def _get_ticker(ticker: str):
        import yfinance as yf
        return yf.Ticker(ticker)

    async def fetch_price(self, ticker: str) -> NormalizedPriceData:
        t = self._get_ticker(ticker)
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
        t = self._get_ticker(ticker)
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

    async def fetch_price_history(
        self, ticker: str, period: str = "1y"
    ) -> list[NormalizedPriceBar]:
        import math

        t = self._get_ticker(ticker)
        hist = t.history(period=period, interval="1d")
        now = datetime.now(timezone.utc)
        bars: list[NormalizedPriceBar] = []

        for idx, row in hist.iterrows():
            open_ = row.get("Open")
            high = row.get("High")
            low = row.get("Low")
            close = row.get("Close")

            # Skip rows where any OHLC value is NaN
            if any(v is None or (isinstance(v, float) and math.isnan(v)) for v in [open_, high, low, close]):
                continue

            volume_raw = row.get("Volume")
            volume = int(volume_raw) if volume_raw is not None and not (isinstance(volume_raw, float) and math.isnan(volume_raw)) else None

            bar_date = idx.to_pydatetime().date()

            bars.append(
                NormalizedPriceBar(
                    ticker=ticker.upper(),
                    date=bar_date,
                    open=Decimal(str(round(float(open_), 4))),
                    high=Decimal(str(round(float(high), 4))),
                    low=Decimal(str(round(float(low), 4))),
                    close=Decimal(str(round(float(close), 4))),
                    volume=volume,
                    source=self.name,
                    fetched_at=now,
                )
            )

        return bars

    async def fetch_dividends(
        self, ticker: str
    ) -> list[NormalizedDividend]:
        t = self._get_ticker(ticker)
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
        t = self._get_ticker(ticker)
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
