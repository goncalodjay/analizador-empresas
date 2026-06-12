from app.core.config import settings
from app.providers.alphavantage_provider import AlphaVantageProvider
from app.providers.base import AbstractMarketDataProvider
from app.providers.finnhub_provider import FinnhubProvider
from app.providers.newsapi_provider import NewsAPIProvider
from app.providers.yfinance_provider import YFinanceProvider


class ProviderFactory:
    @staticmethod
    def get_price_provider(currency: str = "USD") -> AbstractMarketDataProvider:
        """Get price provider based on currency.

        Args:
            currency: Currency code ("ARS" for IOL BCBA, "USD" or default for yfinance)

        Returns:
            AbstractMarketDataProvider: IOLQuotesProvider for ARS, YFinanceProvider otherwise
        """
        if currency == "ARS":
            # Import here to avoid circular imports
            from app.providers.iol_quotes_provider import IOLQuotesProvider
            return IOLQuotesProvider()
        return YFinanceProvider()

    @staticmethod
    def get_iol_quotes_provider() -> "IOLQuotesProvider":
        """Get IOL quotes provider for ARS currency."""
        from app.providers.iol_quotes_provider import IOLQuotesProvider
        return IOLQuotesProvider()

    @staticmethod
    def get_fundamentals_provider() -> AbstractMarketDataProvider:
        return YFinanceProvider()

    @staticmethod
    def get_dividends_provider() -> AbstractMarketDataProvider:
        return YFinanceProvider()

    @staticmethod
    def get_company_info_provider() -> AbstractMarketDataProvider:
        return YFinanceProvider()

    @staticmethod
    def get_analyst_provider() -> FinnhubProvider | None:
        if settings.FINNHUB_API_KEY:
            return FinnhubProvider()
        return None

    @staticmethod
    def get_technical_provider() -> AlphaVantageProvider | None:
        if settings.ALPHA_VANTAGE_API_KEY:
            return AlphaVantageProvider()
        return None

    @staticmethod
    def get_news_provider() -> NewsAPIProvider | None:
        if settings.NEWSAPI_API_KEY:
            return NewsAPIProvider()
        return None
