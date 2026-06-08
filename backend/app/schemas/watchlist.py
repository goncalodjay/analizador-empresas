import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_serializer


class WatchlistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class WatchlistUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None


class WatchlistTickerOut(BaseModel):
    ticker: str
    added_at: datetime

    model_config = {"from_attributes": True}


class WatchlistOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    ticker_count: int
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("id")
    def serialize_id(self, value: uuid.UUID) -> str:
        return str(value)


class WatchlistDetail(WatchlistOut):
    tickers: list[WatchlistTickerOut]


class WatchlistTickerAdd(BaseModel):
    ticker: str = Field(min_length=1, max_length=10)
