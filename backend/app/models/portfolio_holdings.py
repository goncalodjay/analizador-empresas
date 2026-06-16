"""Portfolio holdings model for IOL-synced positions."""
from datetime import datetime
from decimal import Decimal
import uuid

from sqlalchemy import String, Numeric, DateTime, func, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base


class PortfolioHolding(Base):
    """Portfolio holding synced from IOL."""

    __tablename__ = "portfolio_holdings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ticker: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    avg_buy_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="portfolio_holdings")

    __table_args__ = (
        Index("uq_portfolio_holdings_user_ticker", "user_id", "ticker", unique=True),
    )
