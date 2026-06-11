"""Tests for Alembic migration 0003_price_history.

SC-10: alembic upgrade head creates price_history table with constraint;
       alembic downgrade -1 removes it.

These are integration tests that run against live Postgres inside Docker.
"""
import os
import subprocess
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text


DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@db:5432/stockanalyzer",
)


def is_postgres():
    return "postgresql" in DATABASE_URL


async def _table_exists(table_name: str) -> bool:
    engine = create_async_engine(DATABASE_URL)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT 1 FROM information_schema.tables "
                    "WHERE table_name = :tname"
                ),
                {"tname": table_name},
            )
            return result.fetchone() is not None
    finally:
        await engine.dispose()


async def _constraint_exists(table_name: str, constraint_name: str) -> bool:
    engine = create_async_engine(DATABASE_URL)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text(
                    "SELECT 1 FROM information_schema.table_constraints "
                    "WHERE table_name = :tname AND constraint_name = :cname"
                ),
                {"tname": table_name, "cname": constraint_name},
            )
            return result.fetchone() is not None
    finally:
        await engine.dispose()


@pytest.mark.skipif(not is_postgres(), reason="Requires live Postgres DB")
def test_migration_upgrade_creates_price_history_table():
    """After alembic upgrade head, price_history table must exist with the unique constraint."""
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"alembic upgrade failed:\n{result.stderr}"

    assert asyncio.get_event_loop().run_until_complete(
        _table_exists("price_history")
    ), "price_history table not found after upgrade"

    assert asyncio.get_event_loop().run_until_complete(
        _constraint_exists("price_history", "uix_price_history_ticker_date")
    ), "uix_price_history_ticker_date constraint not found after upgrade"


@pytest.mark.skipif(not is_postgres(), reason="Requires live Postgres DB")
def test_migration_downgrade_removes_price_history_table():
    """After alembic downgrade -1, price_history table must not exist."""
    # Ensure we're at head first
    subprocess.run(["alembic", "upgrade", "head"], capture_output=True)

    result = subprocess.run(
        ["alembic", "downgrade", "-1"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"alembic downgrade failed:\n{result.stderr}"

    assert not asyncio.get_event_loop().run_until_complete(
        _table_exists("price_history")
    ), "price_history still exists after downgrade"

    # Re-upgrade so subsequent tests are not broken
    subprocess.run(["alembic", "upgrade", "head"], capture_output=True)
