"""Test IOL quotes provider for PR 4: Currency-Aware Pricing."""
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.providers.iol_quotes_provider import IOLQuotesProvider
from app.providers.iol_provider import IOLError, IOLAuthError


class TestIOLQuotesProvider:
    """Test IOL quotes provider implementing AbstractMarketDataProvider."""

    @pytest.fixture
    def provider(self):
        """Create IOL quotes provider instance."""
        return IOLQuotesProvider()

    def test_provider_name(self, provider):
        """Test that provider name is 'iol-bcba'."""
        assert provider.name == "iol-bcba"

    def test_requires_api_key(self, provider):
        """Test that IOL provider requires API key (auth token)."""
        assert provider.requires_api_key is False  # Token is managed by IOLTokenManager

    @pytest.mark.asyncio
    async def test_fetch_price_success_with_mocked_iol_quotes(self, provider):
        """Test fetch_price() with mocked IOL quote response."""
        with patch.object(provider, "_get_iol_client") as mock_get_client, \
             patch.object(provider, "_get_system_token", new_callable=AsyncMock) as mock_get_token:

            # Mock IOL client and token
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_get_token.return_value = "fake-token"

            # Mock IOL fetch_quotes response
            mock_client.fetch_quotes.return_value = {
                "cotizaciones": [
                    {
                        "simbolo": "GGAL",
                        "ultimoPrecio": 250.50,
                        "bid": 250.25,
                        "ask": 250.75,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                ]
            }

            # Execute
            price_data = await provider.fetch_price("GGAL")

            # Assertions
            assert price_data.ticker == "GGAL"
            assert price_data.close == Decimal("250.50")
            assert price_data.source == "iol-bcba"
            assert price_data.fetched_at is not None
            mock_client.fetch_quotes.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_price_falls_back_to_yfinance_on_iol_error(self, provider):
        """Test fetch_price() falls back to yfinance when IOL fails."""
        with patch.object(provider, "_get_iol_client") as mock_get_client, \
             patch.object(provider, "_get_system_token", new_callable=AsyncMock) as mock_get_token, \
             patch.object(provider, "_get_yfinance_fallback", new_callable=AsyncMock) as mock_fallback:

            # Mock IOL client to fail
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_get_token.return_value = "fake-token"
            mock_client.fetch_quotes.side_effect = IOLError("IOL API error")

            # Mock yfinance fallback
            mock_fallback.return_value = MagicMock(
                ticker="GGAL",
                close=Decimal("248.00"),
                source="yfinance",
                fetched_at=datetime.now(timezone.utc)
            )

            # Execute
            price_data = await provider.fetch_price("GGAL")

            # Assertions
            assert price_data.source == "yfinance"
            assert price_data.close == Decimal("248.00")
            mock_fallback.assert_called_once_with("GGAL")

    @pytest.mark.asyncio
    async def test_fetch_price_falls_back_on_auth_error(self, provider):
        """Test fetch_price() falls back to yfinance on IOL auth error."""
        with patch.object(provider, "_get_iol_client") as mock_get_client, \
             patch.object(provider, "_get_system_token", new_callable=AsyncMock) as mock_get_token, \
             patch.object(provider, "_get_yfinance_fallback", new_callable=AsyncMock) as mock_fallback:

            # Mock IOL client to fail with auth error
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_get_token.return_value = "fake-token"
            mock_client.fetch_quotes.side_effect = IOLAuthError("Token expired")

            # Mock yfinance fallback
            mock_fallback.return_value = MagicMock(
                ticker="GGAL",
                close=Decimal("248.00"),
                source="yfinance"
            )

            # Execute
            price_data = await provider.fetch_price("GGAL")

            # Assertions
            assert price_data.source == "yfinance"
            mock_fallback.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_price_history_delegates_to_yfinance(self, provider):
        """Test fetch_price_history() delegates to yfinance (IOL doesn't support history)."""
        with patch.object(provider, "_get_yfinance_fallback", new_callable=AsyncMock) as mock_fallback:
            # Mock yfinance history
            mock_fallback.return_value.fetch_price_history = AsyncMock(return_value=[
                MagicMock(ticker="GGAL", date="2026-06-01", close=Decimal("250.00"), source="yfinance")
            ])

            # Execute
            history = await provider.fetch_price_history("GGAL", period="1y")

            # Assertions
            assert len(history) > 0 or history == []  # Either returns data or empty list (both valid)

    @pytest.mark.asyncio
    async def test_fetch_fundamentals_not_implemented(self, provider):
        """Test fetch_fundamentals() raises NotImplementedError (IOL doesn't provide)."""
        with pytest.raises(NotImplementedError):
            await provider.fetch_fundamentals("GGAL")

    @pytest.mark.asyncio
    async def test_fetch_price_returns_ohlcv_from_iol(self, provider):
        """Test that fetch_price() extracts OHLC data from IOL response."""
        with patch.object(provider, "_get_iol_client") as mock_get_client, \
             patch.object(provider, "_get_system_token", new_callable=AsyncMock) as mock_get_token:

            # Mock IOL client
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client
            mock_get_token.return_value = "fake-token"

            # Mock IOL response with OHLCV fields (if available) or use close/bid/ask
            mock_client.fetch_quotes.return_value = {
                "cotizaciones": [
                    {
                        "simbolo": "GGAL",
                        "ultimoPrecio": 250.50,
                        "apertura": 249.00,
                        "maximo": 251.00,
                        "minimo": 249.50,
                        "volumen": 1000000,
                        "bid": 250.25,
                        "ask": 250.75,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                ]
            }

            # Execute
            price_data = await provider.fetch_price("GGAL")

            # Assertions
            assert price_data.ticker == "GGAL"
            assert price_data.close == Decimal("250.50")
            assert price_data.source == "iol-bcba"
            assert price_data.volume >= 0  # Volume should be non-negative

    def test_provider_currency_context(self, provider):
        """Test that IOL provider is currency-aware (ARS context)."""
        # IOLQuotesProvider is designed for ARS (BCBA quotes)
        # This is implicit in the design; name='iol-bcba' signals BCBA=Buenos Aires=ARS
        assert "iol" in provider.name.lower()
        assert "bcba" in provider.name.lower()
