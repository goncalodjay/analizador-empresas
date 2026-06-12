"""Tests for portfolio holdings and account status models."""
import pytest
from datetime import datetime, timezone
from decimal import Decimal

from app.models.portfolio_holdings import PortfolioHolding
from app.models.account_status import AccountStatus

REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"

TEST_USER = {"email": "test@example.com", "password": "securepassword123"}


@pytest.mark.asyncio
async def test_portfolio_holding_can_be_instantiated():
    """Test creating a portfolio holding model."""
    from uuid import uuid4

    user_id = uuid4()
    holding = PortfolioHolding(
        user_id=user_id,
        ticker="GGAL",
        quantity=Decimal("50.00"),
        avg_buy_price=Decimal("250.00"),
        currency="ARS",
        synced_at=datetime.now(timezone.utc),
    )

    assert holding.ticker == "GGAL"
    assert holding.quantity == Decimal("50.00")
    assert holding.avg_buy_price == Decimal("250.00")
    assert holding.currency == "ARS"


@pytest.mark.asyncio
async def test_account_status_can_be_instantiated():
    """Test creating an account status model."""
    from uuid import uuid4

    user_id = uuid4()
    status = AccountStatus(
        user_id=user_id,
        cash_balance=Decimal("50000.00"),
        buying_power=Decimal("100000.00"),
        total_balance=Decimal("150000.00"),
        currency="ARS",
        synced_at=datetime.now(timezone.utc),
    )

    assert status.cash_balance == Decimal("50000.00")
    assert status.buying_power == Decimal("100000.00")
    assert status.total_balance == Decimal("150000.00")
    assert status.currency == "ARS"
