"""IOL API client for OAuth2 authentication and data fetching."""
import logging
from typing import Any, Dict

import aiohttp

logger = logging.getLogger(__name__)


class IOLError(Exception):
    """Base exception for IOL API errors."""

    pass


class IOLAuthError(IOLError):
    """Exception raised for authentication errors."""

    pass


class IOLRateLimitError(IOLError):
    """Exception raised for rate limiting errors."""

    pass


class IOLUnavailableError(IOLError):
    """Exception raised when IOL API is unavailable."""

    pass


class IOLClient:
    """IOL API client for OAuth2 password flow and API endpoints.

    Should be used as an async context manager (async with) or close() called manually.
    """

    def __init__(self, client_id: str, client_secret: str, base_url: str):
        """Initialize IOL client.

        Args:
            client_id: IOL OAuth2 client ID
            client_secret: IOL OAuth2 client secret
            base_url: Base URL for IOL API (e.g., https://api.invertironline.com)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the aiohttp session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp session."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def authenticate(
        self, iol_username: str, iol_password: str
    ) -> Dict[str, Any]:
        """Authenticate with IOL using password credentials grant.

        Args:
            iol_username: IOL username
            iol_password: IOL password

        Returns:
            Token response with access_token, expires_in, refresh_token

        Raises:
            IOLAuthError: If authentication fails
            IOLError: If network error occurs
        """
        session = await self._get_session()
        payload = {
            "grant_type": "password",
            "username": iol_username,
            "password": iol_password,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        try:
            async with session.post(
                f"{self.base_url}/token", json=payload, timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 401:
                    logger.warning(f"Authentication failed for user {iol_username}")
                    raise IOLAuthError("Invalid IOL credentials")

                if response.status >= 500:
                    logger.error(f"IOL API error: {response.status}")
                    raise IOLUnavailableError(f"IOL API error: {response.status}")

                if response.status >= 400:
                    raise IOLError(f"IOL API error: {response.status}")

                data = await response.json()
                logger.info(f"Successfully authenticated IOL user {iol_username}")
                return data

        except aiohttp.ClientError as e:
            logger.error(f"Network error during IOL authentication: {e}")
            raise IOLError(f"Network error: {e}")

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh the access token.

        Args:
            refresh_token: IOL refresh token

        Returns:
            New token response with access_token and expires_in

        Raises:
            IOLAuthError: If refresh fails
            IOLError: If network error occurs
        """
        session = await self._get_session()
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        try:
            async with session.post(
                f"{self.base_url}/token", json=payload, timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 401:
                    logger.warning("Token refresh failed: invalid refresh token")
                    raise IOLAuthError("Invalid refresh token")

                if response.status >= 500:
                    logger.error(f"IOL API error: {response.status}")
                    raise IOLUnavailableError(f"IOL API error: {response.status}")

                if response.status >= 400:
                    raise IOLError(f"IOL API error: {response.status}")

                data = await response.json()
                logger.info("Successfully refreshed IOL token")
                return data

        except aiohttp.ClientError as e:
            logger.error(f"Network error during token refresh: {e}")
            raise IOLError(f"Network error: {e}")

    async def fetch_portfolio(self, access_token: str) -> Dict[str, Any]:
        """Fetch user's portfolio holdings.

        Args:
            access_token: IOL access token

        Returns:
            Portfolio response with posiciones list

        Raises:
            IOLAuthError: If token is invalid
            IOLError: If request fails
        """
        session = await self._get_session()
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            async with session.get(
                f"{self.base_url}/portafolio",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as response:
                if response.status == 401:
                    logger.warning("Portfolio fetch failed: invalid token")
                    raise IOLAuthError("Invalid access token")

                if response.status >= 500:
                    logger.error(f"IOL API error: {response.status}")
                    raise IOLUnavailableError(f"IOL API error: {response.status}")

                if response.status >= 400:
                    raise IOLError(f"IOL API error: {response.status}")

                data = await response.json()
                logger.debug("Successfully fetched IOL portfolio")
                return data

        except aiohttp.ClientError as e:
            logger.error(f"Network error during portfolio fetch: {e}")
            raise IOLError(f"Network error: {e}")

    async def fetch_account_status(self, access_token: str) -> Dict[str, Any]:
        """Fetch user's account status.

        Args:
            access_token: IOL access token

        Returns:
            Account status response with saldoDisponible, etc.

        Raises:
            IOLAuthError: If token is invalid
            IOLError: If request fails
        """
        session = await self._get_session()
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            async with session.get(
                f"{self.base_url}/estadocuenta",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as response:
                if response.status == 401:
                    logger.warning("Account status fetch failed: invalid token")
                    raise IOLAuthError("Invalid access token")

                if response.status >= 500:
                    logger.error(f"IOL API error: {response.status}")
                    raise IOLUnavailableError(f"IOL API error: {response.status}")

                if response.status >= 400:
                    raise IOLError(f"IOL API error: {response.status}")

                data = await response.json()
                logger.debug("Successfully fetched IOL account status")
                return data

        except aiohttp.ClientError as e:
            logger.error(f"Network error during account status fetch: {e}")
            raise IOLError(f"Network error: {e}")

    async def fetch_quotes(self, access_token: str, tickers: list[str]) -> Dict[str, Any]:
        """Fetch quotes for multiple tickers.

        Args:
            access_token: IOL access token
            tickers: List of ticker symbols

        Returns:
            Quotes response with cotizaciones list

        Raises:
            IOLAuthError: If token is invalid
            IOLError: If request fails
        """
        session = await self._get_session()
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"tickers": ",".join(tickers)}

        try:
            async with session.get(
                f"{self.base_url}/cotizaciones",
                headers=headers,
                params=params,
                timeout=aiohttp.ClientTimeout(total=5),
            ) as response:
                if response.status == 401:
                    logger.warning("Quotes fetch failed: invalid token")
                    raise IOLAuthError("Invalid access token")

                if response.status >= 500:
                    logger.error(f"IOL API error: {response.status}")
                    raise IOLUnavailableError(f"IOL API error: {response.status}")

                if response.status >= 400:
                    raise IOLError(f"IOL API error: {response.status}")

                data = await response.json()
                logger.debug(f"Successfully fetched quotes for {len(tickers)} tickers")
                return data

        except aiohttp.ClientError as e:
            logger.error(f"Network error during quotes fetch: {e}")
            raise IOLError(f"Network error: {e}")
