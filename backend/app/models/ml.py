import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, Integer, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    strategy_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("investment_strategies.id", ondelete="SET NULL"), nullable=True
    )
    base_model: Mapped[str] = mapped_column(String, nullable=False)
    version_tag: Mapped[str] = mapped_column(String, nullable=False)
    training_samples: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hf_repo: Mapped[str | None] = mapped_column(String, nullable=True)
    adapter_path: Mapped[str | None] = mapped_column(String, nullable=True)
    training_job_id: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")
    metrics: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="model_versions")
    strategy: Mapped["InvestmentStrategy"] = relationship(
        "InvestmentStrategy", back_populates="model_versions"
    )
