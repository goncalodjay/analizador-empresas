"""Tests for portfolio sync endpoints."""
import pytest
from datetime import datetime, timezone
from decimal import Decimal

SYNC_NOW_URL = "/iol/sync-now"
HOLDINGS_URL = "/iol/holdings"
ACCOUNT_STATUS_URL = "/iol/account-status"

REGISTER_URL = "/auth/register"
LOGIN_URL = "/auth/login"

TEST_USER = {"email": "test@example.com", "password": "securepassword123"}


@pytest.mark.asyncio
async def test_holdings_endpoint_requires_auth(async_client):
    """Test that /iol/holdings requires authentication."""
    response = await async_client.get(HOLDINGS_URL)

    # Should redirect or return 401 depending on middleware config
    assert response.status_code in (401, 302, 307)


@pytest.mark.asyncio
async def test_holdings_endpoint_returns_empty_list(async_client):
    """Test that /iol/holdings returns empty list for new user."""
    # Register and login
    await async_client.post(REGISTER_URL, json=TEST_USER)
    login_resp = await async_client.post(LOGIN_URL, json=TEST_USER)

    # Get holdings
    response = await async_client.get(
        HOLDINGS_URL,
        cookies=dict(login_resp.cookies),
    )

    assert response.status_code == 200
    data = response.json()
    assert "holdings" in data
    assert data["holdings"] == []


@pytest.mark.asyncio
async def test_account_status_endpoint_requires_auth(async_client):
    """Test that /iol/account-status requires authentication."""
    response = await async_client.get(ACCOUNT_STATUS_URL)

    # Should redirect or return 401
    assert response.status_code in (401, 302, 307)


@pytest.mark.asyncio
async def test_account_status_endpoint_returns_empty(async_client):
    """Test that /iol/account-status returns empty data for new user."""
    # Register and login
    await async_client.post(REGISTER_URL, json=TEST_USER)
    login_resp = await async_client.post(LOGIN_URL, json=TEST_USER)

    # Get account status
    response = await async_client.get(
        ACCOUNT_STATUS_URL,
        cookies=dict(login_resp.cookies),
    )

    assert response.status_code == 200
    data = response.json()
    assert "cash_balance" in data
    assert data["cash_balance"] == 0.0
    assert data["currency"] == "ARS"


@pytest.mark.asyncio
async def test_sync_now_endpoint_requires_auth(async_client):
    """Test that /iol/sync-now requires authentication."""
    response = await async_client.post(SYNC_NOW_URL)

    # Should redirect or return 401
    assert response.status_code in (401, 302, 307)
