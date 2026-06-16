"""Add user_account_status table for IOL account status snapshots.

Revision ID: 0006
Revises: 0005
Create Date: 2026-06-12 20:27:13.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create user_account_status table."""
    op.create_table(
        "user_account_status",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("cash_balance", sa.Numeric(15, 2), nullable=False),
        sa.Column("buying_power", sa.Numeric(15, 2), nullable=True),
        sa.Column("total_balance", sa.Numeric(15, 2), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="ARS"),
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
        sa.UniqueConstraint("user_id", name="uq_user_account_status_user_id"),
    )
    op.create_index(
        "ix_user_account_status_user_id",
        "user_account_status",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop user_account_status table."""
    op.drop_index("ix_user_account_status_user_id", table_name="user_account_status")
    op.drop_table("user_account_status")
