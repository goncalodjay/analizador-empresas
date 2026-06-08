import uuid
from datetime import datetime, date

from sqlalchemy import String, Numeric, DateTime, Date, BigInteger, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base


class FundamentalSnapshot(Base):
    __tablename__ = "fundamental_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ticker: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    pe_ratio: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    forward_pe: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    pb_ratio: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    eps_ttm: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    eps_growth_yoy: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    revenue_ttm: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    revenue_growth_yoy: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    gross_margin: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    operating_margin: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    net_margin: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    roe: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    debt_to_equity: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    current_ratio: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    free_cash_flow: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    market_cap: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    enterprise_value: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class TechnicalSignal(Base):
    __tablename__ = "technical_signals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ticker: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    price: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    week_52_high: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    week_52_low: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    rsi_14: Mapped[float | None] = mapped_column(Numeric(6, 2), nullable=True)
    macd: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    macd_signal: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    macd_histogram: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    ema_9: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    ema_21: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    ema_50: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    ema_200: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    bollinger_upper: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    bollinger_middle: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    bollinger_lower: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    volume: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    avg_volume_20d: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    signal_label: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class AnalystRating(Base):
    __tablename__ = "analyst_ratings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ticker: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    buy_count: Mapped[int | None] = mapped_column(nullable=True)
    hold_count: Mapped[int | None] = mapped_column(nullable=True)
    sell_count: Mapped[int | None] = mapped_column(nullable=True)
    strong_buy_count: Mapped[int | None] = mapped_column(nullable=True)
    strong_sell_count: Mapped[int | None] = mapped_column(nullable=True)
    price_target_median: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    price_target_high: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    price_target_low: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    last_rating_change: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class InsiderTransaction(Base):
    __tablename__ = "insider_transactions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ticker: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    transaction_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    insider_name: Mapped[str | None] = mapped_column(String, nullable=True)
    insider_role: Mapped[str | None] = mapped_column(String, nullable=True)
    transaction_type: Mapped[str | None] = mapped_column(String, nullable=True)
    shares: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    price: Mapped[float | None] = mapped_column(Numeric(10, 4), nullable=True)
    value: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    shares_after: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class EarningsHistory(Base):
    __tablename__ = "earnings_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ticker: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    period: Mapped[str | None] = mapped_column(String, nullable=True)
    report_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    eps_estimate: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    eps_actual: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    eps_surprise_pct: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    revenue_estimate: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    revenue_actual: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    revenue_surprise_pct: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    next_earnings_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class DividendHistory(Base):
    __tablename__ = "dividend_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ticker: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[str] = mapped_column(String, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    current_yield: Mapped[float | None] = mapped_column(Numeric(6, 4), nullable=True)
    annual_dividend: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    payout_ratio: Mapped[float | None] = mapped_column(Numeric(6, 4), nullable=True)
    consecutive_growth_years: Mapped[int | None] = mapped_column(nullable=True)
    ex_dividend_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class HealthScore(Base):
    __tablename__ = "health_scores"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ticker: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    fundamental_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    earnings_momentum_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    analyst_sentiment_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    technical_momentum_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    composite_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    verdict: Mapped[str | None] = mapped_column(String, nullable=True)
    top_drivers: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    narrative: Mapped[str | None] = mapped_column(String, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="health_scores")
