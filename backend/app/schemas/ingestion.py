from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class NormalizedPriceData(BaseModel):
    ticker: str
    date: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    source: str
    fetched_at: datetime


class NormalizedFundamentals(BaseModel):
    ticker: str
    pe_ratio: Decimal | None = None
    pb_ratio: Decimal | None = None
    market_cap: int | None = None
    sector: str | None = None
    industry: str | None = None
    beta: Decimal | None = None
    eps: Decimal | None = None
    source: str
    fetched_at: datetime


class NormalizedDividend(BaseModel):
    ticker: str
    ex_date: date
    amount: Decimal
    yield_pct: Decimal | None = None
    source: str
    fetched_at: datetime


class NormalizedCompanyInfo(BaseModel):
    ticker: str
    name: str
    sector: str | None = None
    industry: str | None = None
    country: str | None = None
    employees: int | None = None
    description: str | None = None
    source: str
    fetched_at: datetime


class IngestionResult(BaseModel):
    ticker: str
    price: bool = False
    fundamentals: bool = False
    news: bool = False
    source: str
    cached: bool = False
    error: str | None = None


class CacheStatus(BaseModel):
    ticker: str
    price_fresh: bool = False
    fundamentals_fresh: bool = False
    price_cached_at: datetime | None = None
    fundamentals_cached_at: datetime | None = None
