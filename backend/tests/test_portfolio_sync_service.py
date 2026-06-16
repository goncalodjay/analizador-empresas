"""Tests for portfolio sync service."""
import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, patch, MagicMock
import uuid

from app.services.portfolio_sync_service import PortfolioSyncService, PortfolioSyncReport
from app.providers.iol_provider import IOLAuthError, IOLError
from app.models.iol_credentials import IOLCredentials


@pytest.fixture
def sync_service():
    """Create a portfolio sync service."""
    return PortfolioSyncService()


@pytest.mark.asyncio
async def test_sync_portfolio_with_valid_iol_data(sync_service):
    """Test sync_portfolio fetches IOL holdings and returns report."""
    user_id = uuid.uuid4()

    # Mock IOL client and token manager
    mock_iol_client = AsyncMock()
    mock_token_manager = AsyncMock()
    mock_db = AsyncMock()

    # Mock IOL portfolio response
    iol_portfolio = {
        "posiciones": [
            {
                "id": "pos_001",
                "ticker": "GGAL",
                "cantidad": 50,
                "precio_promedio": 250.00,
                "moneda": "ARS",
            },
            {
                "id": "pos_002",
                "ticker": "AAPL",
                "cantidad": 10,
                "precio_promedio": 145.00,
                "moneda": "USD",
            },
        ]
    }

    mock_token_manager.get_valid_token.return_value = "valid_token"
    mock_iol_client.fetch_portfolio.return_value = iol_portfolio

    # Mock database get
    mock_creds = MagicMock(spec=IOLCredentials)
    mock_creds.sync_error = None
    mock_db.execute.return_value = MagicMock()
    mock_db.execute.return_value.scalar_one_or_none.return_value = mock_creds

    with patch.object(sync_service, "iol_client", mock_iol_client):
        with patch.object(sync_service, "iol_token_manager", mock_token_manager):
            report = await sync_service.sync_portfolio(user_id, mock_db)

    # Verify report
    assert report.synced_count == 2
    assert "GGAL" in report.tickers
    assert "AAPL" in report.tickers


@pytest.mark.asyncio
async def test_sync_portfolio_with_iol_auth_error(sync_service):
    """Test sync_portfolio handles IOLAuthError."""
    user_id = uuid.uuid4()

    mock_token_manager = AsyncMock()
    mock_db = AsyncMock()

    # Mock credentials exist but token refresh fails
    mock_creds = MagicMock(spec=IOLCredentials)
    mock_creds.sync_error = None

    # Make execute() return a mock with scalar_one_or_none()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_creds
    mock_db.execute.return_value = mock_result

    mock_token_manager.get_valid_token.side_effect = IOLAuthError("Invalid credentials")

    with patch.object(sync_service, "iol_token_manager", mock_token_manager):
        with pytest.raises(IOLAuthError):
            await sync_service.sync_portfolio(user_id, mock_db)


@pytest.mark.asyncio
async def test_sync_account_status_returns_account_data(sync_service):
    """Test sync_account_status fetches and returns account data."""
    user_id = uuid.uuid4()

    mock_iol_client = AsyncMock()
    mock_token_manager = AsyncMock()
    mock_db = AsyncMock()

    iol_account = {
        "saldo_disponible": 50000.00,
        "poder_compra": 100000.00,
        "patrimonio": 150000.00,
    }

    mock_token_manager.get_valid_token.return_value = "valid_token"
    mock_iol_client.fetch_account_status.return_value = iol_account

    with patch.object(sync_service, "iol_client", mock_iol_client):
        with patch.object(sync_service, "iol_token_manager", mock_token_manager):
            account_status = await sync_service.sync_account_status(user_id, mock_db)

    # Verify account status
    assert account_status.cash_balance == Decimal("50000.00")
    assert account_status.buying_power == Decimal("100000.00")
    assert account_status.total_balance == Decimal("150000.00")
    assert account_status.currency == "ARS"


@pytest.mark.asyncio
async def test_sync_portfolio_report_schema():
    """Test PortfolioSyncReport schema."""
    now = datetime.now(timezone.utc)
    report = PortfolioSyncReport(
        synced_count=3, tickers=["GGAL", "AAPL", "MERV"], synced_at=now
    )

    assert report.synced_count == 3
    assert len(report.tickers) == 3
    assert report.synced_at == now
