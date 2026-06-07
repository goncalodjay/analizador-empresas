"""initial schema

Revision ID: 0001
Revises:
Create Date: 2024-06-07 00:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("timezone", sa.String(), server_default="America/Argentina/Buenos_Aires", nullable=False),
        sa.Column("digest_time", sa.Time(), server_default="06:00:00", nullable=False),
        sa.Column("risk_tolerance", sa.String(), server_default="moderate", nullable=False),
        sa.Column("email_notifications", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=False)

    # portfolio_positions
    op.create_table(
        "portfolio_positions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ticker", sa.String(), nullable=False),
        sa.Column("shares", sa.Numeric(14, 4), nullable=False),
        sa.Column("avg_buy_price", sa.Numeric(12, 4), nullable=False),
        sa.Column("sector", sa.String(), nullable=True),
        sa.Column("notes", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "ticker", name="uix_portfolio_user_ticker"),
    )

    # watchlists
    op.create_table(
        "watchlists",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # watchlist_tickers
    op.create_table(
        "watchlist_tickers",
        sa.Column("watchlist_id", sa.Uuid(), sa.ForeignKey("watchlists.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ticker", sa.String(), nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("watchlist_id", "ticker"),
    )

    # investment_strategies
    op.create_table(
        "investment_strategies",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("style", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("rules", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("is_primary", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_training_ready", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # fundamental_snapshots
    op.create_table(
        "fundamental_snapshots",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("ticker", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("pe_ratio", sa.Numeric(10, 2), nullable=True),
        sa.Column("forward_pe", sa.Numeric(10, 2), nullable=True),
        sa.Column("pb_ratio", sa.Numeric(10, 2), nullable=True),
        sa.Column("eps_ttm", sa.Numeric(10, 4), nullable=True),
        sa.Column("eps_growth_yoy", sa.Numeric(8, 4), nullable=True),
        sa.Column("revenue_ttm", sa.BigInteger(), nullable=True),
        sa.Column("revenue_growth_yoy", sa.Numeric(8, 4), nullable=True),
        sa.Column("gross_margin", sa.Numeric(8, 4), nullable=True),
        sa.Column("operating_margin", sa.Numeric(8, 4), nullable=True),
        sa.Column("net_margin", sa.Numeric(8, 4), nullable=True),
        sa.Column("roe", sa.Numeric(8, 4), nullable=True),
        sa.Column("debt_to_equity", sa.Numeric(8, 4), nullable=True),
        sa.Column("current_ratio", sa.Numeric(8, 4), nullable=True),
        sa.Column("free_cash_flow", sa.BigInteger(), nullable=True),
        sa.Column("market_cap", sa.BigInteger(), nullable=True),
        sa.Column("enterprise_value", sa.BigInteger(), nullable=True),
        sa.Column("raw_data", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # technical_signals
    op.create_table(
        "technical_signals",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("ticker", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("price", sa.Numeric(12, 4), nullable=True),
        sa.Column("week_52_high", sa.Numeric(12, 4), nullable=True),
        sa.Column("week_52_low", sa.Numeric(12, 4), nullable=True),
        sa.Column("rsi_14", sa.Numeric(6, 2), nullable=True),
        sa.Column("macd", sa.Numeric(10, 4), nullable=True),
        sa.Column("macd_signal", sa.Numeric(10, 4), nullable=True),
        sa.Column("macd_histogram", sa.Numeric(10, 4), nullable=True),
        sa.Column("ema_9", sa.Numeric(12, 4), nullable=True),
        sa.Column("ema_21", sa.Numeric(12, 4), nullable=True),
        sa.Column("ema_50", sa.Numeric(12, 4), nullable=True),
        sa.Column("ema_200", sa.Numeric(12, 4), nullable=True),
        sa.Column("bollinger_upper", sa.Numeric(12, 4), nullable=True),
        sa.Column("bollinger_middle", sa.Numeric(12, 4), nullable=True),
        sa.Column("bollinger_lower", sa.Numeric(12, 4), nullable=True),
        sa.Column("volume", sa.BigInteger(), nullable=True),
        sa.Column("avg_volume_20d", sa.BigInteger(), nullable=True),
        sa.Column("signal_label", sa.String(), nullable=True),
        sa.Column("raw_data", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # analyst_ratings
    op.create_table(
        "analyst_ratings",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("ticker", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("buy_count", sa.Integer(), nullable=True),
        sa.Column("hold_count", sa.Integer(), nullable=True),
        sa.Column("sell_count", sa.Integer(), nullable=True),
        sa.Column("strong_buy_count", sa.Integer(), nullable=True),
        sa.Column("strong_sell_count", sa.Integer(), nullable=True),
        sa.Column("price_target_median", sa.Numeric(10, 2), nullable=True),
        sa.Column("price_target_high", sa.Numeric(10, 2), nullable=True),
        sa.Column("price_target_low", sa.Numeric(10, 2), nullable=True),
        sa.Column("last_rating_change", sa.JSON(), nullable=True),
        sa.Column("raw_data", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # insider_transactions
    op.create_table(
        "insider_transactions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("ticker", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=True),
        sa.Column("insider_name", sa.String(), nullable=True),
        sa.Column("insider_role", sa.String(), nullable=True),
        sa.Column("transaction_type", sa.String(), nullable=True),
        sa.Column("shares", sa.BigInteger(), nullable=True),
        sa.Column("price", sa.Numeric(10, 4), nullable=True),
        sa.Column("value", sa.BigInteger(), nullable=True),
        sa.Column("shares_after", sa.BigInteger(), nullable=True),
        sa.Column("raw_data", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # earnings_history
    op.create_table(
        "earnings_history",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("ticker", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("period", sa.String(), nullable=True),
        sa.Column("report_date", sa.Date(), nullable=True),
        sa.Column("eps_estimate", sa.Numeric(8, 4), nullable=True),
        sa.Column("eps_actual", sa.Numeric(8, 4), nullable=True),
        sa.Column("eps_surprise_pct", sa.Numeric(8, 4), nullable=True),
        sa.Column("revenue_estimate", sa.BigInteger(), nullable=True),
        sa.Column("revenue_actual", sa.BigInteger(), nullable=True),
        sa.Column("revenue_surprise_pct", sa.Numeric(8, 4), nullable=True),
        sa.Column("next_earnings_date", sa.Date(), nullable=True),
        sa.Column("raw_data", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # dividend_history
    op.create_table(
        "dividend_history",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("ticker", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("current_yield", sa.Numeric(6, 4), nullable=True),
        sa.Column("annual_dividend", sa.Numeric(8, 4), nullable=True),
        sa.Column("payout_ratio", sa.Numeric(6, 4), nullable=True),
        sa.Column("consecutive_growth_years", sa.Integer(), nullable=True),
        sa.Column("ex_dividend_date", sa.Date(), nullable=True),
        sa.Column("payment_date", sa.Date(), nullable=True),
        sa.Column("raw_data", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # health_scores
    op.create_table(
        "health_scores",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("ticker", sa.String(), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("computed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("fundamental_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("earnings_momentum_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("analyst_sentiment_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("technical_momentum_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("composite_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("verdict", sa.String(), nullable=True),
        sa.Column("top_drivers", sa.JSON(), nullable=True),
        sa.Column("narrative", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # generated_signals
    op.create_table(
        "generated_signals",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("ticker", sa.String(), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("strategy_id", sa.Uuid(), sa.ForeignKey("investment_strategies.id", ondelete="SET NULL"), nullable=True),
        sa.Column("generated_by", sa.String(), nullable=False),
        sa.Column("signal_type", sa.String(), nullable=False),
        sa.Column("entry_price_low", sa.Numeric(12, 4), nullable=True),
        sa.Column("entry_price_high", sa.Numeric(12, 4), nullable=True),
        sa.Column("stop_loss", sa.Numeric(12, 4), nullable=True),
        sa.Column("take_profit_1", sa.Numeric(12, 4), nullable=True),
        sa.Column("take_profit_2", sa.Numeric(12, 4), nullable=True),
        sa.Column("take_profit_3", sa.Numeric(12, 4), nullable=True),
        sa.Column("position_size_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("reasoning", sa.String(), nullable=True),
        sa.Column("confidence", sa.Numeric(4, 3), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("outcome_label", sa.String(), nullable=True),
        sa.Column("outcome_labeled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_return_pct", sa.Numeric(8, 4), nullable=True),
        sa.Column("included_in_training", sa.Boolean(), server_default="false", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # news_items
    op.create_table(
        "news_items",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("ticker", sa.String(), nullable=True),
        sa.Column("sector", sa.String(), nullable=True),
        sa.Column("headline", sa.String(), nullable=False),
        sa.Column("summary", sa.String(), nullable=True),
        sa.Column("source_name", sa.String(), nullable=False),
        sa.Column("url", sa.String(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sentiment", sa.String(), nullable=True),
        sa.Column("sentiment_score", sa.Numeric(4, 3), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # daily_digests
    op.create_table(
        "daily_digests",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("digest_date", sa.Date(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("content", sa.JSON(), nullable=False),
        sa.Column("email_sent", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("email_sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "digest_date", name="uix_digest_user_date"),
    )

    # model_versions
    op.create_table(
        "model_versions",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("strategy_id", sa.Uuid(), sa.ForeignKey("investment_strategies.id", ondelete="SET NULL"), nullable=True),
        sa.Column("base_model", sa.String(), nullable=False),
        sa.Column("version_tag", sa.String(), nullable=False),
        sa.Column("training_samples", sa.Integer(), nullable=True),
        sa.Column("hf_repo", sa.String(), nullable=True),
        sa.Column("adapter_path", sa.String(), nullable=True),
        sa.Column("training_job_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(), server_default="pending", nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # backtest_results
    op.create_table(
        "backtest_results",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("strategy_id", sa.Uuid(), sa.ForeignKey("investment_strategies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ticker", sa.String(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("total_return_pct", sa.Numeric(8, 4), nullable=True),
        sa.Column("annualized_return_pct", sa.Numeric(8, 4), nullable=True),
        sa.Column("win_rate", sa.Numeric(5, 4), nullable=True),
        sa.Column("avg_win_pct", sa.Numeric(6, 4), nullable=True),
        sa.Column("avg_loss_pct", sa.Numeric(6, 4), nullable=True),
        sa.Column("max_drawdown_pct", sa.Numeric(6, 4), nullable=True),
        sa.Column("sharpe_ratio", sa.Numeric(6, 4), nullable=True),
        sa.Column("total_trades", sa.Integer(), nullable=True),
        sa.Column("equity_curve", sa.JSON(), nullable=True),
        sa.Column("trade_log", sa.JSON(), nullable=True),
        sa.Column("run_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # indexes
    op.create_index("idx_fundamental_ticker_fetched", "fundamental_snapshots", ["ticker", sa.text("fetched_at DESC")], unique=False)
    op.create_index("idx_technical_ticker_fetched", "technical_signals", ["ticker", sa.text("fetched_at DESC")], unique=False)
    op.create_index("idx_signals_user_ticker", "generated_signals", ["user_id", "ticker", sa.text("generated_at DESC")], unique=False)
    op.create_index("idx_signals_unlabeled", "generated_signals", ["user_id"], unique=False, postgresql_where=sa.text("outcome_label IS NULL"))
    op.create_index("idx_news_ticker_published", "news_items", ["ticker", sa.text("published_at DESC")], unique=False)
    op.execute("CREATE INDEX idx_news_embedding ON news_items USING ivfflat (embedding vector_cosine_ops)")
    op.create_index("idx_health_ticker_user", "health_scores", ["ticker", "user_id", sa.text("computed_at DESC")], unique=False)


def downgrade() -> None:
    op.drop_index("idx_health_ticker_user", table_name="health_scores")
    op.execute("DROP INDEX IF EXISTS idx_news_embedding")
    op.drop_index("idx_news_ticker_published", table_name="news_items")
    op.drop_index("idx_signals_unlabeled", table_name="generated_signals")
    op.drop_index("idx_signals_user_ticker", table_name="generated_signals")
    op.drop_index("idx_technical_ticker_fetched", table_name="technical_signals")
    op.drop_index("idx_fundamental_ticker_fetched", table_name="fundamental_snapshots")

    op.drop_table("backtest_results")
    op.drop_table("model_versions")
    op.drop_table("daily_digests")
    op.drop_table("news_items")
    op.drop_table("generated_signals")
    op.drop_table("health_scores")
    op.drop_table("dividend_history")
    op.drop_table("earnings_history")
    op.drop_table("insider_transactions")
    op.drop_table("analyst_ratings")
    op.drop_table("technical_signals")
    op.drop_table("fundamental_snapshots")
    op.drop_table("investment_strategies")
    op.drop_table("watchlist_tickers")
    op.drop_table("watchlists")
    op.drop_table("portfolio_positions")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
