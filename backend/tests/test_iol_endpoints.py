"""Tests for IOL API endpoints."""
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient
from cryptography.fernet import Fernet

from app.models import User, IOLCredentials
from app.core.security import create_access_token


@pytest.fixture
def encryption_key():
    """Encryption key for testing."""
    return Fernet.generate_key().decode()


@pytest.mark.asyncio
async def test_post_iol_setup_with_valid_credentials(async_client: AsyncClient, encryption_key):
    """Test POST /iol/setup with valid credentials."""
    # Register and login
    register_resp = await async_client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "TestPass123!"},
    )
    assert register_resp.status_code == 201

    login_resp = await async_client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "TestPass123!"},
    )
    assert login_resp.status_code == 200

    # Mock IOL authenticate
    with patch("app.services.iol_service.IOLClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.authenticate = AsyncMock(
            return_value={
                "access_token": "iol_access_token",
                "expires_in": 900,
                "refresh_token": "iol_refresh_token",
            }
        )

        with patch("app.models.iol_credentials.settings.ENCRYPTION_KEY", encryption_key):
            # Setup IOL
            setup_resp = await async_client.post(
                "/iol/setup",
                json={"iol_username": "iol_user@example.com", "iol_password": "iol_pass123"},
            )

            assert setup_resp.status_code == 200
            data = setup_resp.json()
            assert data["status"] == "connected"
            assert data["iol_username"] == "iol_user@example.com"


@pytest.mark.asyncio
async def test_post_iol_setup_with_invalid_credentials(async_client: AsyncClient):
    """Test POST /iol/setup with invalid credentials."""
    # Register and login
    await async_client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "TestPass123!"},
    )

    await async_client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "TestPass123!"},
    )

    # Mock IOL authenticate failure
    from app.providers.iol_provider import IOLAuthError

    with patch("app.services.iol_service.IOLClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.authenticate = AsyncMock(side_effect=IOLAuthError("Invalid credentials"))

        # Setup IOL with wrong credentials
        setup_resp = await async_client.post(
            "/iol/setup",
            json={"iol_username": "wrong@example.com", "iol_password": "wrongpass"},
        )

        assert setup_resp.status_code == 401
        data = setup_resp.json()
        assert "detail" in data


@pytest.mark.asyncio
async def test_post_iol_setup_without_auth(async_client: AsyncClient):
    """Test POST /iol/setup without authentication."""
    setup_resp = await async_client.post(
        "/iol/setup",
        json={"iol_username": "user@example.com", "iol_password": "pass"},
    )

    assert setup_resp.status_code == 401


@pytest.mark.asyncio
async def test_get_iol_status_connected(async_client: AsyncClient, encryption_key):
    """Test GET /iol/status when connected."""
    # Register and login
    await async_client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "TestPass123!"},
    )

    await async_client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "TestPass123!"},
    )

    # Setup IOL
    with patch("app.services.iol_service.IOLClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value = mock_client
        mock_client.authenticate = AsyncMock(
            return_value={
                "access_token": "iol_access_token",
                "expires_in": 900,
                "refresh_token": "iol_refresh_token",
            }
        )

        with patch("app.models.iol_credentials.settings.ENCRYPTION_KEY", encryption_key):
            await async_client.post(
                "/iol/setup",
                json={"iol_username": "iol_user@example.com", "iol_password": "iol_pass123"},
            )

    # Get status
    status_resp = await async_client.get("/iol/status")

    assert status_resp.status_code == 200
    data = status_resp.json()
    assert data["connected"] is True


@pytest.mark.asyncio
async def test_get_iol_status_disconnected(async_client: AsyncClient):
    """Test GET /iol/status when not connected."""
    # Register and login
    await async_client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "TestPass123!"},
    )

    await async_client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "TestPass123!"},
    )

    # Get status
    status_resp = await async_client.get("/iol/status")

    assert status_resp.status_code == 200
    data = status_resp.json()
    assert data["connected"] is False


@pytest.mark.asyncio
async def test_get_iol_status_without_auth(async_client: AsyncClient):
    """Test GET /iol/status without authentication."""
    status_resp = await async_client.get("/iol/status")

    assert status_resp.status_code == 401
