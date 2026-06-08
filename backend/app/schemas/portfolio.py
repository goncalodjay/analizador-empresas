import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_serializer


class PortfolioPositionCreate(BaseModel):
    ticker: str = Field(min_length=1, max_length=10)
    shares: Decimal
    avg_buy_price: Decimal
    sector: str | None = None
    notes: str | None = None


class PortfolioPositionUpdate(BaseModel):
    ticker: str | None = Field(default=None, min_length=1, max_length=10)
    shares: Decimal | None = None
    avg_buy_price: Decimal | None = None
    sector: str | None = None
    notes: str | None = None


class PortfolioPositionOut(BaseModel):
    id: uuid.UUID
    ticker: str
    shares: Decimal
    avg_buy_price: Decimal
    sector: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("id")
    def serialize_id(self, value: uuid.UUID) -> str:
        return str(value)

    @field_serializer("shares", "avg_buy_price")
    def serialize_decimal(self, value: Decimal) -> str:
        return str(value)
