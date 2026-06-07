import uuid
from datetime import datetime, date

from sqlalchemy import String, Numeric, Integer, DateTime, Date, JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    strategy_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("investment_strategies.id", ondelete="CASCADE"), nullable=False
    )
    ticker: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_return_pct: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    annualized_return_pct: Mapped[float | None] = mapped_column(Numeric(8, 4), nullable=True)
    win_rate: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    avg_win_pct: Mapped[float | None] = mapped_column(Numeric(6, 4), nullable=True)
    avg_loss_pct: Mapped[float | None] = mapped_column(Numeric(6, 4), nullable=True)
    max_drawdown_pct: Mapped[float | None] = mapped_column(Numeric(6, 4), nullable=True)
    sharpe_ratio: Mapped[float | None] = mapped_column(Numeric(6, 4), nullable=True)
    total_trades: Mapped[int | None] = mapped_column(Integer, nullable=True)
    equity_curve: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    trade_log: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    run_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    strategy: Mapped["InvestmentStrategy"] = relationship(
        "InvestmentStrategy", back_populates="backtest_results"
    )
