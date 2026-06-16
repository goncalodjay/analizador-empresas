import uuid
from datetime import datetime, time

from sqlalchemy import String, Boolean, DateTime, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    timezone: Mapped[str] = mapped_column(
        String, default="America/Argentina/Buenos_Aires"
    )
    digest_time: Mapped[time] = mapped_column(Time, default=time(6, 0))
    risk_tolerance: Mapped[str] = mapped_column(String, default="moderate")
    email_notifications: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    portfolio_positions: Mapped[list["PortfolioPosition"]] = relationship(
        "PortfolioPosition", back_populates="user", cascade="all, delete-orphan"
    )
    watchlists: Mapped[list["Watchlist"]] = relationship(
        "Watchlist", back_populates="user", cascade="all, delete-orphan"
    )
    strategies: Mapped[list["InvestmentStrategy"]] = relationship(
        "InvestmentStrategy", back_populates="user", cascade="all, delete-orphan"
    )
    health_scores: Mapped[list["HealthScore"]] = relationship(
        "HealthScore", back_populates="user", cascade="all, delete-orphan"
    )
    generated_signals: Mapped[list["GeneratedSignal"]] = relationship(
        "GeneratedSignal", back_populates="user", cascade="all, delete-orphan"
    )
    daily_digests: Mapped[list["DailyDigest"]] = relationship(
        "DailyDigest", back_populates="user", cascade="all, delete-orphan"
    )
    model_versions: Mapped[list["ModelVersion"]] = relationship(
        "ModelVersion", back_populates="user", cascade="all, delete-orphan"
    )
    iol_credentials: Mapped["IOLCredentials"] = relationship(
        "IOLCredentials", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    portfolio_holdings: Mapped[list["PortfolioHolding"]] = relationship(
        "PortfolioHolding", back_populates="user", cascade="all, delete-orphan"
    )
    account_status: Mapped["AccountStatus"] = relationship(
        "AccountStatus", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
