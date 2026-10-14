"""IOL BCBA Quotes Provider - implements AbstractMarketDataProvider for ARS holdings."""
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional, TYPE_CHECKING
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.providers.base import AbstractMarketDataProvider
from app.providers.iol_provider import IOLClient, IOLAuthError, IOLError
from app.schemas.ingestion import (
    NormalizedCompanyInfo,
    NormalizedDividend,
    NormalizedFundamentals,
    NormalizedPriceBar,
    NormalizedPriceData,
)

if TYPE_CHECKING:
    from app.services.iol_service import IOLTokenManager

logger = logging.getLogger(__name__)


class IOLQuotesProvider(AbstractMarketDataProvider):
    """IOL BCBA quotes provider for ARS-denominated holdings.

    Provides real-time or near-real-time quotes from IOL's /cotizaciones endpoint.
    Falls back to yfinance if IOL is unavailable.
    """

    name = "iol-bcba"
    requires_api_key = False  # Token is managed by IOLTokenManager

    def __init__(self):
        """Initialize IOL quotes provider."""
        self._iol_client: IOLClient | None = None
        self._yfinance_provider: "YFinanceProvider" | None = None

    def _get_iol_client(self) -> IOLClient:
        """Get or create IOL client instance."""
        if self._iol_client is None:
            self._iol_client = IOLClient(
                client_id=settings.IOL_CLIENT_ID,
                client_secret=settings.IOL_CLIENT_SECRET,
                base_url=settings.IOL_BASE_URL,
            )
        return self._iol_client

    async def _get_system_token(
        self, user_id: Optional[UUID] = None, db: Optional[AsyncSession] = None
    ) -> Optional[str]:
        """Get IOL access token for quotes.

        If user_id and db are provided, fetches the user's IOL token via IOLTokenManager.
        Otherwise returns None (caller should handle fallback).

        Args:
            user_id: User ID for token lookup
            db: Database session for token manager

        Returns:
            Access token string, or None if no token available
        """
        if user_id and db:
            # Use IOLTokenManager to get user's token
            from app.services.iol_service import IOLTokenManager
            token_manager = IOLTokenManager()
            try:
                token = await token_manager.get_valid_token(db, user_id)
                if token:
                    logger.debug(f"Retrieved IOL token for user {user_id}")
                    return token
                else:
                    logger.warning(f"No IOL token found for user {user_id}")
                    return None
            except Exception as e:
                logger.warning(f"Failed to retrieve IOL token for user {user_id}: {e}")
                return None
        else:
            # No user context provided; cannot fetch token
            logger.debug("No user context provided to _get_system_token; returning None")
            return None

    async def _get_yfinance_fallback(self, ticker: str) -> NormalizedPriceData:
        """Fetch price from yfinance as fallback."""
        if self._yfinance_provider is None:
            from app.providers.yfinance_provider import YFinanceProvider
            self._yfinance_provider = YFinanceProvider()

        logger.info(f"Falling back to yfinance for {ticker}")
        return await self._yfinance_provider.fetch_price(ticker)

    async def fetch_price(
        self,
        ticker: str,
        user_id: Optional[UUID] = None,
        db: Optional[AsyncSession] = None,
    ) -> NormalizedPriceData:
        """Fetch price from IOL BCBA quotes endpoint.

        Args:
            ticker: Stock ticker symbol (e.g., 'GGAL')
            user_id: Optional user ID for token lookup
            db: Optional database session for token lookup

        Returns:
            NormalizedPriceData with price from IOL or yfinance fallback

        Raises:
            PriceError: If both IOL and fallback fail
        """
        ticker_upper = ticker.upper()

        try:
            # Get IOL token (from user context if provided, otherwise None)
            access_token = await self._get_system_token(user_id=user_id, db=db)

            # If no token available, fall back to yfinance
            if not access_token:
                logger.info(f"No IOL token available for {ticker_upper}; using yfinance fallback")
                return await self._get_yfinance_fallback(ticker_upper)

            iol_client = self._get_iol_client()
            response = await iol_client.fetch_quotes(access_token, [ticker_upper])

            # Extract price from IOL response
            if response and "cotizaciones" in response:
                for quote in response["cotizaciones"]:
                    if quote.get("simbolo") == ticker_upper:
                        price_value = quote.get("ultimoPrecio") or quote.get("precio")
                        if price_value:
                            now = datetime.now(timezone.utc)
                            # Use price_value as open/high/low if not provided
                            close_price = Decimal(str(price_value))
                            return NormalizedPriceData(
                                ticker=ticker_upper,
                                date=now,
                                open=self._safe_decimal(quote.get("apertura")) or close_price,
                                high=self._safe_decimal(quote.get("maximo")) or close_price,
                                low=self._safe_decimal(quote.get("minimo")) or close_price,
                                close=close_price,
                                volume=int(quote.get("volumen", 0)),
                                source=self.name,
                                fetched_at=now,
                            )

            # No quote found in IOL response; fall back to yfinance
            logger.warning(f"No IOL quote for {ticker_upper}; using yfinance fallback")
            return await self._get_yfinance_fallback(ticker_upper)

        except IOLAuthError as e:
            logger.error(f"IOL auth error for {ticker_upper}: {e}; using yfinance fallback")
            return await self._get_yfinance_fallback(ticker_upper)

        except IOLError as e:
            logger.error(f"IOL error for {ticker_upper}: {e}; using yfinance fallback")
            return await self._get_yfinance_fallback(ticker_upper)

        except Exception as e:
            logger.error(f"Unexpected error fetching {ticker_upper} from IOL: {e}")
            return await self._get_yfinance_fallback(ticker_upper)

    async def fetch_price_history(
        self, ticker: str, period: str = "1y"
    ) -> list[NormalizedPriceBar]:
        """Fetch price history from yfinance (IOL does not provide history).

        Args:
            ticker: Stock ticker symbol
            period: Time period ('1d', '1y', etc.)

        Returns:
            List of NormalizedPriceBar from yfinance
        """
        if self._yfinance_provider is None:
            from app.providers.yfinance_provider import YFinanceProvider
            self._yfinance_provider = YFinanceProvider()

        return await self._yfinance_provider.fetch_price_history(ticker, period)

    async def fetch_fundamentals(
        self, ticker: str
    ) -> NormalizedFundamentals:
        """Fetch fundamentals (not supported by IOL).

        Raises:
            NotImplementedError: IOL does not provide fundamental data
        """
        raise NotImplementedError("IOL BCBA provider does not support fundamental data")

    async def fetch_company_info(self, ticker: str) -> NormalizedCompanyInfo:
        """Fetch company info (not supported by IOL).

        Raises:
            NotImplementedError: IOL does not provide company info
        """
        raise NotImplementedError("IOL BCBA provider does not support company info")

    async def fetch_dividends(
        self, ticker: str
    ) -> list[NormalizedDividend]:
        """Fetch dividend data (not supported by IOL).

        Returns:
            Empty list (not supported)
        """
        return []

    @staticmethod
    def _safe_decimal(value: Any) -> Decimal | None:
        """Safely convert value to Decimal."""
        if value is None:
            return None
        try:
            d = Decimal(str(value))
            return d if d.is_finite() else None
        except (ValueError, TypeError, AttributeError):
            return None
