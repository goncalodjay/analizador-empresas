from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class PricePoint(BaseModel):
    date: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int | None = None


class PriceSeriesResponse(BaseModel):
    ticker: str
    points: list[PricePoint]
    from_date: date
    to_date: date
    count: int
    source: str
    freshness: str
    fetched_at: datetime | None = None
