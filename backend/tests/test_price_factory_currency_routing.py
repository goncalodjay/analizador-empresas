"""Test price factory currency routing for PR 4: Currency-Aware Pricing."""
import pytest

from app.providers.factory import ProviderFactory
from app.providers.iol_quotes_provider import IOLQuotesProvider
from app.providers.yfinance_provider import YFinanceProvider


class TestPriceFactoryRoutingByCurrency:
    """Test price factory routes by currency: ARS → IOL, USD → yfinance."""

    def test_factory_returns_iol_quotes_provider_for_ars(self):
        """Test that factory returns IOL quotes provider for ARS currency."""
        provider = ProviderFactory.get_price_provider(currency="ARS")
        assert isinstance(provider, IOLQuotesProvider)
        assert provider.name == "iol-bcba"

    def test_factory_returns_yfinance_provider_for_usd(self):
        """Test that factory returns yfinance provider for USD currency."""
        provider = ProviderFactory.get_price_provider(currency="USD")
        assert isinstance(provider, YFinanceProvider)
        assert provider.name == "yfinance"

    def test_factory_returns_yfinance_for_unknown_currency(self):
        """Test that factory returns yfinance as fallback for unknown currency."""
        provider = ProviderFactory.get_price_provider(currency="EUR")
        assert isinstance(provider, YFinanceProvider)
        assert provider.name == "yfinance"

    def test_factory_returns_yfinance_when_currency_not_provided(self):
        """Test that factory returns yfinance as default when currency not provided."""
        provider = ProviderFactory.get_price_provider()
        assert isinstance(provider, YFinanceProvider)
        assert provider.name == "yfinance"

    def test_factory_has_get_iol_quotes_provider_method(self):
        """Test that factory has get_iol_quotes_provider() convenience method."""
        assert hasattr(ProviderFactory, "get_iol_quotes_provider")
        provider = ProviderFactory.get_iol_quotes_provider()
        assert isinstance(provider, IOLQuotesProvider)
