"""IOL API endpoints for credential setup and status."""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.providers.iol_provider import IOLAuthError, IOLError
from app.services.iol_service import IOLTokenManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/iol", tags=["iol"])

# Request/Response schemas
class IOLSetupRequest(BaseModel):
    """Request body for IOL setup."""

    iol_username: str = Field(..., description="IOL username")
    iol_password: str = Field(..., description="IOL password")


class IOLSetupResponse(BaseModel):
    """Response for successful IOL setup."""

    status: str = Field(default="connected", description="Connection status")
    iol_username: str = Field(..., description="IOL username")
    account_name: str = Field(default="", description="IOL account name")
    synced_at: str = Field(..., description="Setup timestamp in ISO format")


class IOLStatusResponse(BaseModel):
    """Response for IOL connection status."""

    connected: bool = Field(..., description="Whether IOL is connected")
    iol_username: str = Field(default="", description="IOL username if connected")
    account_name: str = Field(default="", description="Account name if connected")
    cash_balance: float = Field(default=0, description="Available cash")
    currency: str = Field(default="ARS", description="Currency code")
    last_sync: str | None = Field(default=None, description="Last sync timestamp")
    needs_reauth: bool = Field(default=False, description="Whether re-authentication is needed")


@router.post("/setup", response_model=IOLSetupResponse, status_code=status.HTTP_200_OK)
async def setup_iol_connection(
    payload: IOLSetupRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Set up IOL credentials and validate against IOL API.

    Validates credentials by attempting authentication with IOL.
    If successful, stores encrypted credentials and sets iol_connected flag.

    Args:
        payload: IOL username and password
        current_user: Currently authenticated user
        db: Database session

    Returns:
        Connection status and account info

    Raises:
        HTTPException: If authentication fails or IOL API is unreachable
    """
    manager = IOLTokenManager()

    try:
        logger.info(f"Setting up IOL connection for user {current_user.id}")
        creds = await manager.store_credentials(
            db, current_user.id, payload.iol_username, payload.iol_password
        )

        logger.info(f"IOL connection established for user {current_user.id}")

        # Return success response
        from datetime import datetime, timezone

        return IOLSetupResponse(
            status="connected",
            iol_username=creds.iol_username,
            account_name=creds.iol_username,  # TODO: fetch actual account name from IOL
            synced_at=datetime.now(timezone.utc).isoformat(),
        )

    except IOLAuthError:
        logger.warning(f"IOL authentication failed for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid IOL credentials"
        )

    except IOLError:
        logger.error(f"IOL API error for user {current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="IOL API is currently unavailable",
        )


@router.get("/status", response_model=IOLStatusResponse, status_code=status.HTTP_200_OK)
async def get_iol_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get IOL connection status for the current user.

    Returns connection status, account info, and whether re-authentication is needed.

    Args:
        current_user: Currently authenticated user
        db: Database session

    Returns:
        Connection status response

    Raises:
        HTTPException: If database query fails
    """
    manager = IOLTokenManager()

    try:
        status_dict = await manager.get_credentials_status(db, current_user.id)

        if status_dict["connected"]:
            return IOLStatusResponse(
                connected=True,
                iol_username=status_dict.get("iol_username", ""),
                account_name=status_dict.get("account_name", ""),
                last_sync=status_dict.get("last_synced", ""),
                needs_reauth=status_dict.get("needs_reauth", False),
            )
        else:
            return IOLStatusResponse(connected=False)

    except Exception as e:
        logger.error(f"Error getting IOL status for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve IOL status",
        )
