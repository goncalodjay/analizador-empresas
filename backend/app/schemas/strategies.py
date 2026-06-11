"""
Strategy schema contracts for the Strategy Management Module (Deliverable 6).

CONTRACT OWNER: This module owns the D7 signal-engine rules contract.
Any new rule key added here MUST be reviewed against D7's consumption logic.

Comparison semantics (consumed by D7):
- ``max_*`` fields are upper bounds (strategy passes if metric <= threshold).
- ``min_*`` fields are lower bounds (strategy passes if metric >= threshold).
- Boolean flags (``ema_crossover``, ``macd_bullish``) require the condition to be true.
- ``None`` / omitted fields are not enforced — the strategy is unconstrained on that dimension.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class StrategyStyle(str, Enum):
    VALUE = "value"
    GROWTH = "growth"
    MOMENTUM = "momentum"
    DIVIDEND = "dividend"
    HYBRID = "hybrid"


class StrategyRules(BaseModel):
    """Typed, closed rule set for an investment strategy.

    All fields are optional — a strategy may constrain on any subset.
    Unknown keys are rejected (``extra='forbid'``) to prevent silent contract drift.
    """

    model_config = ConfigDict(extra="forbid")

    # --- Fundamental thresholds ---
    max_pe: Decimal | None = Field(default=None, gt=0)
    min_roe: Decimal | None = Field(default=None)  # percent; can be negative
    min_dividend_yield: Decimal | None = Field(default=None, ge=0)
    max_debt_to_equity: Decimal | None = Field(default=None, ge=0)
    min_revenue_growth: Decimal | None = Field(default=None)

    # --- Technical thresholds (aligned with D5 indicators) ---
    rsi_entry_max: Decimal | None = Field(default=None, ge=0, le=100)
    rsi_exit_min: Decimal | None = Field(default=None, ge=0, le=100)
    ema_crossover: bool | None = Field(default=None)  # require golden cross
    macd_bullish: bool | None = Field(default=None)   # require bullish MACD

    # --- Position / risk sizing ---
    max_position_pct: Decimal | None = Field(default=None, gt=0, le=100)
    stop_loss_pct: Decimal | None = Field(default=None, gt=0, le=100)
    take_profit_pct: Decimal | None = Field(default=None, gt=0)


class StrategyBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    style: StrategyStyle
    description: str | None = Field(default=None, max_length=2000)
    rules: StrategyRules


class StrategyCreate(StrategyBase):
    is_active: bool = True
    is_primary: bool = False


class StrategyUpdate(BaseModel):
    """Partial update schema — only supplied fields are applied.

    ``is_active`` and ``is_primary`` are intentionally excluded; use the
    dedicated PATCH endpoints to change those flags.
    """

    name: str | None = Field(default=None, min_length=1, max_length=120)
    style: StrategyStyle | None = None
    description: str | None = Field(default=None, max_length=2000)
    rules: StrategyRules | None = None


class StrategyOut(BaseModel):
    id: uuid.UUID
    name: str
    style: StrategyStyle
    description: str | None
    rules: StrategyRules
    is_active: bool
    is_primary: bool
    is_training_ready: bool  # read-only; toggled by D8
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("id")
    def serialize_id(self, value: uuid.UUID) -> str:
        return str(value)


class ActivateRequest(BaseModel):
    is_active: bool
