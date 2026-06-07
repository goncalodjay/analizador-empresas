import uuid
from datetime import datetime

from sqlalchemy import String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class GeneratedSignal(Base):
    __tablename__ = "generated_signals"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    ticker: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    strategy_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("investment_strategies.id", ondelete="SET NULL"), nullable=True
    )
    generated_by: Mapped[str] = mapped_column(String, nullable=False)
    signal_type: Mapped[str] = mapped_column(String, nullable=False)
    entry_price_low: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    entry_price_high: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    stop_loss: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    take_profit_1: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    take_profit_2: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    take_profit_3: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True)
    position_size_pct: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    reasoning: Mapped[str | None] = mapped_column(String, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Numeric(4, 3), nullable=True)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    outcome_label: Mapped[str | None] = mapped_column(String, nullable=True)
    outcome_labeled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_return_pct: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    included_in_training: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship("User", back_populates="generated_signals")
    strategy: Mapped["InvestmentStrategy"] = relationship(
        "InvestmentStrategy", back_populates="generated_signals"
    )
