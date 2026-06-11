from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class NewsItemOut(BaseModel):
    headline: str
    summary: str | None = None
    source_name: str
    url: str | None = None
    published_at: datetime | None = None

    model_config = {"from_attributes": True}


class NewsFeedResponse(BaseModel):
    ticker: str
    available: bool
    source: str | None = None  # "cache" | "db" | "none" | "newsapi"
    items: list[NewsItemOut] = []
    cached_at: datetime | None = None
    freshness: Literal["live", "stale"] | None = None
    count: int = 0
