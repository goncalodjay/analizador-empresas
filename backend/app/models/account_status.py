"""Account status model for IOL account snapshots."""
from datetime import datetime
from decimal import Decimal
import uuid

from sqlalchemy import String, Numeric, DateTime, func, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base


class AccountStatus(Base):
    """Account status snapshot from IOL."""

    __tablename__ = "user_account_status"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True
    )
    cash_balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    buying_power: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    total_balance: Mapped[Decimal | None] = mapped_column(Numeric(15, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default="ARS")
    synced_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="account_status")
