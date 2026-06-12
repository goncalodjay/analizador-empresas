"""Tests for IOL API Client provider."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.providers.iol_provider import IOLClient, IOLAuthError, IOLError, IOLUnavailableError


@pytest.fixture
def iol_client():
    """Create an IOL client for testing."""
    return IOLClient(
        client_id="test_client_id",
        client_secret="test_client_secret",
        base_url="https://api.invertironline.com",
    )


@pytest.mark.asyncio
async def test_authenticate_success(iol_client):
    """Test successful authentication with valid credentials."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={
            "access_token": "test_access_token",
            "token_type": "Bearer",
            "expires_in": 900,
            "refresh_token": "test_refresh_token",
        }
    )

    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value = mock_response

        response = await iol_client.authenticate("user@example.com", "password123")

        assert response["access_token"] == "test_access_token"
        assert response["refresh_token"] == "test_refresh_token"
        assert response["expires_in"] == 900


@pytest.mark.asyncio
async def test_authenticate_invalid_credentials(iol_client):
    """Test authentication with invalid credentials."""
    mock_response = AsyncMock()
    mock_response.status = 401

    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value = mock_response

        with pytest.raises(IOLAuthError):
            await iol_client.authenticate("user@example.com", "wrongpassword")


@pytest.mark.asyncio
async def test_refresh_token_success(iol_client):
    """Test successful token refresh."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={
            "access_token": "new_access_token",
            "token_type": "Bearer",
            "expires_in": 900,
            "refresh_token": "new_refresh_token",
        }
    )

    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value = mock_response

        response = await iol_client.refresh_token("old_refresh_token")

        assert response["access_token"] == "new_access_token"
        assert response["refresh_token"] == "new_refresh_token"


@pytest.mark.asyncio
async def test_fetch_portfolio_success(iol_client):
    """Test fetching portfolio holdings."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={
            "posiciones": [
                {
                    "ticker": "GGAL",
                    "cantidad": 50,
                    "precioPromedio": 250.0,
                    "moneda": "ARS",
                },
                {
                    "ticker": "AAPL",
                    "cantidad": 10,
                    "precioPromedio": 150.0,
                    "moneda": "USD",
                },
            ]
        }
    )

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value = mock_response

        response = await iol_client.fetch_portfolio("test_access_token")

        assert "posiciones" in response
        assert len(response["posiciones"]) == 2


@pytest.mark.asyncio
async def test_fetch_account_status_success(iol_client):
    """Test fetching account status."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={
            "nombre": "Juan Pérez",
            "saldoDisponible": 125000.50,
            "moneda": "ARS",
            "podeCompra": 250000.00,
            "saldoTotal": 375000.50,
        }
    )

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value = mock_response

        response = await iol_client.fetch_account_status("test_access_token")

        assert response["nombre"] == "Juan Pérez"
        assert response["saldoDisponible"] == 125000.50


@pytest.mark.asyncio
async def test_fetch_quotes_success(iol_client):
    """Test fetching quotes for multiple tickers."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={
            "cotizaciones": [
                {"ticker": "GGAL", "precioUltimo": 255.0, "moneda": "ARS"},
                {"ticker": "AAPL", "precioUltimo": 152.0, "moneda": "USD"},
            ]
        }
    )

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value = mock_response

        response = await iol_client.fetch_quotes("test_access_token", ["GGAL", "AAPL"])

        assert "cotizaciones" in response
        assert len(response["cotizaciones"]) == 2


@pytest.mark.asyncio
async def test_authenticate_with_401_response(iol_client):
    """Test that 401 responses raise IOLAuthError."""
    mock_response = AsyncMock()
    mock_response.status = 401

    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value = mock_response

        with pytest.raises(IOLAuthError):
            await iol_client.authenticate("user@example.com", "password")


@pytest.mark.asyncio
async def test_fetch_portfolio_with_401_response(iol_client):
    """Test that 401 on portfolio fetch raises IOLAuthError."""
    mock_response = AsyncMock()
    mock_response.status = 401

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value = mock_response

        with pytest.raises(IOLAuthError):
            await iol_client.fetch_portfolio("expired_token")
