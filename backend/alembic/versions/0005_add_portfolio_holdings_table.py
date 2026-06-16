"""Add portfolio_holdings table for IOL-synced holdings.

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-12 20:27:12.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create portfolio_holdings table."""
    op.create_table(
        "portfolio_holdings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("ticker", sa.String(20), nullable=False),
        sa.Column("quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("avg_buy_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "ticker", name="uq_portfolio_holdings_user_ticker"),
    )
    op.create_index(
        "ix_portfolio_holdings_user_id",
        "portfolio_holdings",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop portfolio_holdings table."""
    op.drop_index("ix_portfolio_holdings_user_id", table_name="portfolio_holdings")
    op.drop_table("portfolio_holdings")
