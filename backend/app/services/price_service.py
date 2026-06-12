"""Price service with caching strategy for PR 4: Currency-Aware Pricing.

Implements separate cache TTLs: IOL 1-min, yfinance 5-min.
"""
import logging
from datetime import datetime, timezone
from decimal import Decimal

from app.providers.factory import ProviderFactory
from app.schemas.ingestion import NormalizedPriceData
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)


class PriceService:
    """Service for fetching and caching prices with currency-aware routing."""

    # Cache TTLs by source
    IOL_CACHE_TTL = 60  # 1 minute for IOL BCBA quotes
    YFINANCE_CACHE_TTL = 300  # 5 minutes for yfinance
    STALE_PRICE_CACHE_TTL = 86400  # 24 hours for last-known fallback
    STALE_THRESHOLD = 3600  # 1 hour for stale marking

    def __init__(self):
        """Initialize price service."""
        self.cache = CacheService()

    def _build_cache_key(
        self, ticker: str, source: str = None, currency: str = None
    ) -> str:
        """Build cache key for price data.

        Args:
            ticker: Stock ticker symbol
            source: Price source (e.g., 'iol-bcba', 'yfinance')
            currency: Currency code (e.g., 'ARS', 'USD')

        Returns:
            Cache key string
        """
        if source and currency:
            return f"price:{source}:{ticker.upper()}:{currency}"
        elif currency:
            return f"price:{ticker.upper()}:{currency}"
        elif source:
            return f"price:{source}:{ticker.upper()}"
        return f"price:{ticker.upper()}"

    def _get_cache_ttl(self, source: str) -> int:
        """Get TTL for cache based on source.

        Args:
            source: Price source (e.g., 'iol-bcba', 'yfinance')

        Returns:
            TTL in seconds
        """
        if source == "iol-bcba":
            return self.IOL_CACHE_TTL
        return self.YFINANCE_CACHE_TTL

    async def get_price_cached(
        self, ticker: str, currency: str = "USD"
    ) -> NormalizedPriceData | None:
        """Get cached price or fetch fresh price.

        Args:
            ticker: Stock ticker symbol
            currency: Currency code ('ARS', 'USD', etc.)

        Returns:
            NormalizedPriceData with price and source, or None if unavailable
        """
        ticker_upper = ticker.upper()

        try:
            # Get provider based on currency
            provider = ProviderFactory.get_price_provider(currency=currency)
            cache_key = self._build_cache_key(ticker_upper, provider.name, currency)

            # Check cache first
            cached = await self.cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for {ticker_upper}/{currency} from {provider.name}")
                return cached

            # Cache miss: fetch from provider
            logger.debug(
                f"Cache miss for {ticker_upper}/{currency}; fetching from {provider.name}"
            )
            price_data = await provider.fetch_price(ticker_upper)

            # Store in cache with source-specific TTL
            ttl = self._get_cache_ttl(price_data.source)
            await self.cache.set(cache_key, price_data, ttl=ttl)

            # Also store last-known price for fallback (24-hr TTL)
            last_known_key = self._build_cache_key(
                ticker_upper, "last-known", currency
            )
            await self.cache.set(last_known_key, price_data, ttl=self.STALE_PRICE_CACHE_TTL)

            return price_data

        except Exception as e:
            logger.error(f"Error fetching price for {ticker_upper}/{currency}: {e}")

            # Try to return last-known price
            try:
                last_known_key = self._build_cache_key(
                    ticker_upper, "last-known", currency
                )
                cached = await self.cache.get(last_known_key)
                if cached:
                    # Mark as stale
                    cached.source = "stale"
                    return cached
            except Exception as e2:
                logger.error(
                    f"Error retrieving last-known price for {ticker_upper}: {e2}"
                )

            return None

    async def invalidate_price_cache(self, ticker: str, currency: str = "USD") -> None:
        """Invalidate cached price for manual refresh.

        Args:
            ticker: Stock ticker symbol
            currency: Currency code
        """
        ticker_upper = ticker.upper()
        provider = ProviderFactory.get_price_provider(currency=currency)
        cache_key = self._build_cache_key(ticker_upper, provider.name, currency)

        try:
            await self.cache.delete(cache_key)
            logger.debug(f"Invalidated cache for {ticker_upper}/{currency}")
        except Exception as e:
            logger.warning(f"Error invalidating cache for {ticker_upper}: {e}")

    async def warm_cache(self, tickers: list[str], currency: str = "USD") -> None:
        """Pre-populate cache with prices for multiple tickers.

        Useful for dashboard page load to reduce first-page latency.

        Args:
            tickers: List of ticker symbols
            currency: Currency code
        """
        if not tickers:
            return

        logger.info(f"Warming cache for {len(tickers)} tickers in {currency}")

        for ticker in tickers:
            try:
                await self.get_price_cached(ticker, currency=currency)
            except Exception as e:
                logger.warning(f"Error warming cache for {ticker}: {e}")
