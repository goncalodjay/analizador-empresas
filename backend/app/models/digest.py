import uuid
from datetime import datetime, date

from sqlalchemy import String, DateTime, Date, JSON, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class DailyDigest(Base):
    __tablename__ = "daily_digests"
    __table_args__ = (UniqueConstraint("user_id", "digest_date", name="uix_digest_user_date"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    digest_date: Mapped[date] = mapped_column(Date, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    content: Mapped[dict] = mapped_column(JSON, nullable=False)
    email_sent: Mapped[bool] = mapped_column(default=False)
    email_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="daily_digests")
