"""IOL API endpoints for credential setup, status, and portfolio sync."""
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.portfolio_holdings import PortfolioHolding
from app.models.account_status import AccountStatus
from app.providers.iol_provider import IOLAuthError, IOLError
from app.services.iol_service import IOLTokenManager
from app.services.portfolio_sync_service import PortfolioSyncService

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


class HoldingResponse(BaseModel):
    """Single portfolio holding."""

    ticker: str = Field(..., description="Ticker symbol")
    quantity: float = Field(..., description="Quantity of shares")
    avg_buy_price: float = Field(..., description="Average buy price")
    currency: str = Field(..., description="Currency code")


class HoldingsListResponse(BaseModel):
    """List of portfolio holdings."""

    holdings: list[HoldingResponse] = Field(default_factory=list, description="Holdings list")


class SyncNowResponse(BaseModel):
    """Response from manual sync endpoint."""

    status: str = Field(..., description="Sync status")
    holdings_count: int = Field(..., description="Number of holdings synced")
    synced_at: str = Field(..., description="Sync timestamp in ISO format")


class AccountStatusResponse(BaseModel):
    """Account status snapshot."""

    cash_balance: float = Field(..., description="Available cash")
    buying_power: float = Field(..., description="Buying power")
    total_balance: float = Field(..., description="Total balance")
    currency: str = Field(default="ARS", description="Currency code")


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


@router.post("/sync-now", response_model=SyncNowResponse, status_code=status.HTTP_200_OK)
async def sync_portfolio_now(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger portfolio sync.

    Fetches latest portfolio and account status from IOL and updates the database.

    Args:
        current_user: Currently authenticated user
        db: Database session

    Returns:
        Sync result with status and counts

    Raises:
        HTTPException: If sync fails or IOL API is unreachable
    """
    try:
        logger.info(f"Manual portfolio sync requested for user {current_user.id}")
        sync_service = PortfolioSyncService()

        # Sync portfolio and account status
        report = await sync_service.sync_portfolio(current_user.id, db)
        await sync_service.sync_account_status(current_user.id, db)

        logger.info(f"Manual sync completed for user {current_user.id}: {report.synced_count} holdings")

        return SyncNowResponse(
            status="success",
            holdings_count=report.synced_count,
            synced_at=report.synced_at.isoformat(),
        )

    except IOLAuthError as e:
        logger.warning(f"IOL auth error during sync for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="IOL connection failed: invalid credentials",
        )

    except IOLError as e:
        logger.error(f"IOL API error during sync for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="IOL API is currently unavailable",
        )

    except Exception as e:
        logger.error(f"Portfolio sync failed for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Portfolio sync failed: {str(e)}",
        )


@router.get("/holdings", response_model=HoldingsListResponse, status_code=status.HTTP_200_OK)
async def get_holdings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch user's current portfolio holdings from the database.

    Args:
        current_user: Currently authenticated user
        db: Database session

    Returns:
        List of holdings

    Raises:
        HTTPException: If database query fails
    """
    try:
        logger.info(f"Fetching holdings for user {current_user.id}")

        # Query portfolio holdings
        stmt = select(PortfolioHolding).where(PortfolioHolding.user_id == current_user.id)
        result = await db.execute(stmt)
        holdings = result.scalars().all()

        holdings_response = [
            HoldingResponse(
                ticker=h.ticker,
                quantity=float(h.quantity),
                avg_buy_price=float(h.avg_buy_price),
                currency=h.currency,
            )
            for h in holdings
        ]

        return HoldingsListResponse(holdings=holdings_response)

    except Exception as e:
        logger.error(f"Error fetching holdings for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve holdings",
        )


@router.get("/account-status", response_model=AccountStatusResponse, status_code=status.HTTP_200_OK)
async def get_account_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch user's current account status.

    Args:
        current_user: Currently authenticated user
        db: Database session

    Returns:
        Account status or empty dict if not synced

    Raises:
        HTTPException: If database query fails
    """
    try:
        logger.info(f"Fetching account status for user {current_user.id}")

        # Query account status
        stmt = select(AccountStatus).where(AccountStatus.user_id == current_user.id)
        result = await db.execute(stmt)
        account = result.scalar_one_or_none()

        if not account:
            logger.info(f"No account status found for user {current_user.id}")
            return AccountStatusResponse(
                cash_balance=0.0,
                buying_power=0.0,
                total_balance=0.0,
                currency="ARS",
            )

        return AccountStatusResponse(
            cash_balance=float(account.cash_balance),
            buying_power=float(account.buying_power or 0),
            total_balance=float(account.total_balance or 0),
            currency=account.currency,
        )

    except Exception as e:
        logger.error(f"Error fetching account status for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve account status",
        )
