"""add unique constraint on news_items(ticker, url)

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-11 00:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use a partial unique index WHERE url IS NOT NULL to avoid conflicts on NULL url values.
    # NULL-url articles are non-dedupable and will be skipped during ingestion upsert.
    # The UniqueConstraint on the model is for ORM awareness; the real enforcement is this index.
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_news_ticker_url "
        "ON news_items (ticker, url) WHERE url IS NOT NULL"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS uq_news_ticker_url")
