"""IOL token manager service for credential storage and token refresh."""
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.iol_credentials import IOLCredentials
from app.providers.iol_provider import IOLClient, IOLAuthError, IOLError
from app.core.config import settings

logger = logging.getLogger(__name__)


class IOLTokenManager:
    """Manage IOL credentials and token refresh."""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        base_url: str = "https://api.invertironline.com",
    ):
        """Initialize token manager.

        Args:
            client_id: IOL OAuth2 client ID (uses env var if not provided)
            client_secret: IOL OAuth2 client secret (uses env var if not provided)
            base_url: IOL API base URL
        """
        self.client_id = client_id or getattr(settings, "IOL_CLIENT_ID", "")
        self.client_secret = client_secret or getattr(settings, "IOL_CLIENT_SECRET", "")
        self.base_url = base_url

    async def store_credentials(
        self, db: AsyncSession, user_id: UUID, iol_username: str, iol_password: str
    ) -> IOLCredentials:
        """Store encrypted IOL credentials and validate with IOL.

        Args:
            db: Database session
            user_id: User ID
            iol_username: IOL username
            iol_password: IOL password (plain text, will be encrypted)

        Returns:
            Stored IOLCredentials object

        Raises:
            IOLAuthError: If credentials are invalid
            IOLError: If IOL API is unreachable
        """
        # Validate credentials against IOL
        async with IOLClient(self.client_id, self.client_secret, self.base_url) as client:
            try:
                token_response = await client.authenticate(iol_username, iol_password)
            except IOLError as e:
                logger.error(f"Failed to authenticate IOL user {iol_username}: {e}")
                raise

        # Create or update credentials
        encrypted_password = IOLCredentials.encrypt_password(iol_password)
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=token_response.get("expires_in", 900)
        )

        # Check if credentials already exist
        result = await db.execute(
            select(IOLCredentials).where(IOLCredentials.user_id == user_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            existing.iol_username = iol_username
            existing.encrypted_password = encrypted_password
            existing.access_token = token_response.get("access_token", "")
            existing.token_expires_at = expires_at
            existing.refresh_token = token_response.get("refresh_token", "")
            existing.updated_at = datetime.now(timezone.utc)
            creds = existing
        else:
            creds = IOLCredentials(
                user_id=user_id,
                iol_username=iol_username,
                encrypted_password=encrypted_password,
                access_token=token_response.get("access_token", ""),
                token_expires_at=expires_at,
                refresh_token=token_response.get("refresh_token", ""),
            )
            db.add(creds)

        await db.commit()
        await db.refresh(creds)

        logger.info(f"Stored IOL credentials for user {user_id}")
        return creds

    async def get_valid_token(self, db: AsyncSession, user_id: UUID) -> Optional[str]:
        """Get a valid access token for the user.

        Refreshes the token if it's near expiry (<60s).

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Access token string, or None if no credentials found

        Raises:
            IOLAuthError: If token refresh fails
            IOLError: If IOL API is unreachable
        """
        result = await db.execute(
            select(IOLCredentials).where(IOLCredentials.user_id == user_id)
        )
        creds = result.scalar_one_or_none()

        if not creds:
            logger.warning(f"No IOL credentials found for user {user_id}")
            return None

        # Check if token is expiring soon (< 60 seconds)
        time_until_expiry = creds.time_until_expiry()
        if time_until_expiry < 60:
            logger.info(f"Token expiring soon for user {user_id}, refreshing...")
            refresh_ok = await self.refresh_token_if_near_expiry(db, user_id)
            if not refresh_ok:
                raise IOLAuthError("Failed to refresh token")

        # Re-fetch in case refresh happened
        result = await db.execute(
            select(IOLCredentials).where(IOLCredentials.user_id == user_id)
        )
        creds = result.scalar_one_or_none()

        return creds.access_token if creds else None

    async def refresh_token_if_near_expiry(
        self, db: AsyncSession, user_id: UUID
    ) -> bool:
        """Refresh token if it's near expiry (<2 min).

        Args:
            db: Database session
            user_id: User ID

        Returns:
            True if refresh succeeded, False otherwise
        """
        result = await db.execute(
            select(IOLCredentials).where(IOLCredentials.user_id == user_id)
        )
        creds = result.scalar_one_or_none()

        if not creds:
            logger.warning(f"No IOL credentials found for user {user_id}")
            return False

        # Check if token is within 2 minutes of expiry
        time_until_expiry = creds.time_until_expiry()
        if time_until_expiry > 120:
            logger.debug(f"Token for user {user_id} not expiring soon, skipping refresh")
            return True

        # Refresh the token
        async with IOLClient(self.client_id, self.client_secret, self.base_url) as client:
            try:
                token_response = await client.refresh_token(creds.refresh_token)
                expires_at = datetime.now(timezone.utc) + timedelta(
                    seconds=token_response.get("expires_in", 900)
                )

                creds.access_token = token_response.get("access_token", "")
                creds.token_expires_at = expires_at
                creds.refresh_token = token_response.get("refresh_token", creds.refresh_token)
                creds.sync_error = None  # Clear any previous errors
                creds.updated_at = datetime.now(timezone.utc)

                await db.commit()
                await db.refresh(creds)

                logger.info(f"Successfully refreshed token for user {user_id}")
                return True

            except IOLError as e:
                logger.error(f"Failed to refresh token for user {user_id}: {e}")
                creds.sync_error = f"Token refresh failed: {str(e)}"
                creds.updated_at = datetime.now(timezone.utc)
                await db.commit()
                return False

    async def revoke_credentials(self, db: AsyncSession, user_id: UUID) -> None:
        """Revoke (delete) IOL credentials for a user.

        Args:
            db: Database session
            user_id: User ID
        """
        result = await db.execute(
            select(IOLCredentials).where(IOLCredentials.user_id == user_id)
        )
        creds = result.scalar_one_or_none()

        if creds:
            await db.delete(creds)
            await db.commit()
            logger.info(f"Revoked IOL credentials for user {user_id}")

    async def get_credentials_status(
        self, db: AsyncSession, user_id: UUID
    ) -> Dict[str, Any]:
        """Get IOL connection status for a user.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            Dictionary with connection status
        """
        result = await db.execute(
            select(IOLCredentials).where(IOLCredentials.user_id == user_id)
        )
        creds = result.scalar_one_or_none()

        if not creds:
            return {"connected": False}

        # Check if token is expired
        time_until_expiry = creds.time_until_expiry()
        needs_reauth = time_until_expiry < 0 or creds.sync_error is not None

        return {
            "connected": True,
            "iol_username": creds.iol_username,
            "account_name": creds.iol_username,  # Will be updated from account status
            "last_synced": creds.last_synced_at.isoformat() if creds.last_synced_at else None,
            "needs_reauth": needs_reauth,
            "sync_error": creds.sync_error,
        }
