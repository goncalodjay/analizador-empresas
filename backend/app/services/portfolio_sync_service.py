"""Portfolio sync service for fetching IOL holdings and account status."""
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
import uuid

from pydantic import BaseModel
from sqlalchemy import select, insert, update, delete
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.iol_credentials import IOLCredentials
from app.models.portfolio_holdings import PortfolioHolding
from app.models.account_status import AccountStatus
from app.providers.iol_provider import IOLClient, IOLAuthError, IOLError
from app.services.iol_service import IOLTokenManager
from app.core.config import settings

logger = logging.getLogger(__name__)


class PortfolioSyncReport(BaseModel):
    """Report of a portfolio sync operation."""

    synced_count: int
    tickers: list[str]
    synced_at: datetime


class PortfolioSyncService:
    """Service for syncing portfolio holdings and account status from IOL."""

    def __init__(self):
        """Initialize the sync service."""
        # Configure IOL client from settings, same pattern as IOLTokenManager
        client_id = getattr(settings, "IOL_CLIENT_ID", "")
        client_secret = getattr(settings, "IOL_CLIENT_SECRET", "")
        base_url = getattr(settings, "IOL_BASE_URL", "https://api.invertironline.com")

        self.iol_client = IOLClient(
            client_id=client_id,
            client_secret=client_secret,
            base_url=base_url,
        )
        self.iol_token_manager = IOLTokenManager()

    async def sync_portfolio(
        self, user_id: uuid.UUID, db: AsyncSession
    ) -> PortfolioSyncReport:
        """Fetch IOL portfolio and sync to database.

        Args:
            user_id: User ID to sync for
            db: Database session

        Returns:
            PortfolioSyncReport with sync results

        Raises:
            IOLAuthError: If token is invalid or refresh fails
            IOLError: If IOL API call fails
        """
        try:
            # Get IOL credentials
            creds_stmt = select(IOLCredentials).where(
                IOLCredentials.user_id == user_id
            )
            creds_result = await db.execute(creds_stmt)
            iol_creds = creds_result.scalar_one_or_none()

            if not iol_creds:
                raise IOLAuthError(f"No IOL credentials found for user {user_id}")

            # Get valid token, with re-auth retry on failure
            try:
                token = await self.iol_token_manager.get_valid_token(db, user_id)
            except IOLAuthError as e:
                # Attempt ONE re-authentication from stored encrypted credentials
                logger.info(f"Token refresh failed, attempting re-authentication for user {user_id}")
                try:
                    decrypted_password = iol_creds.decrypt_password()
                    # Re-authenticate and store new credentials
                    await self.iol_token_manager.store_credentials(
                        db, user_id, iol_creds.iol_username, decrypted_password
                    )
                    # Retry getting the token
                    token = await self.iol_token_manager.get_valid_token(db, user_id)
                except IOLAuthError as reauth_error:
                    # Re-auth also failed
                    logger.error(f"Re-authentication failed for user {user_id}: {reauth_error}")
                    iol_creds.sync_error = "Reconnect required: re-authentication failed"
                    await db.commit()
                    raise

            # Fetch IOL portfolio
            try:
                iol_portfolio = await self.iol_client.fetch_portfolio(token)
            except IOLAuthError as e:
                iol_creds.sync_error = f"IOL auth error: {str(e)}"
                await db.commit()
                raise

            # Transform and upsert holdings
            synced_tickers = []
            for iol_holding in iol_portfolio.get("posiciones", []):
                ticker = iol_holding.get("ticker", "").upper()
                quantity = Decimal(str(iol_holding.get("cantidad", 0)))
                avg_buy_price = Decimal(str(iol_holding.get("precio_promedio", 0)))
                currency = iol_holding.get("moneda", "ARS")
                iol_position_id = iol_holding.get("id")

                # Upsert: insert or update
                stmt = (
                    pg_insert(PortfolioHolding)
                    .values(
                        user_id=user_id,
                        ticker=ticker,
                        quantity=quantity,
                        avg_buy_price=avg_buy_price,
                        currency=currency,
                        synced_at=datetime.now(timezone.utc),
                    )
                    .on_conflict_do_update(
                        index_elements=["user_id", "ticker"],
                        set_={
                            "quantity": quantity,
                            "avg_buy_price": avg_buy_price,
                            "currency": currency,
                            "synced_at": datetime.now(timezone.utc),
                        },
                    )
                )
                await db.execute(stmt)
                synced_tickers.append(ticker)

            # Remove sold holdings: delete positions not present in IOL response
            # (per spec: IOL is source of truth)
            if synced_tickers:
                delete_stmt = delete(PortfolioHolding).where(
                    (PortfolioHolding.user_id == user_id) &
                    (~PortfolioHolding.ticker.in_(synced_tickers))
                )
                await db.execute(delete_stmt)

            # Commit transaction
            await db.commit()

            # Update credentials with sync info
            iol_creds.last_synced_at = datetime.now(timezone.utc)
            iol_creds.sync_error = None
            await db.commit()

            logger.info(
                f"Portfolio synced for user {user_id}: {len(synced_tickers)} holdings"
            )

            return PortfolioSyncReport(
                synced_count=len(synced_tickers),
                tickers=synced_tickers,
                synced_at=datetime.now(timezone.utc),
            )

        except (IOLAuthError, IOLError):
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Portfolio sync failed for user {user_id}: {str(e)}")
            raise

    async def sync_account_status(
        self, user_id: uuid.UUID, db: AsyncSession
    ) -> AccountStatus:
        """Fetch IOL account status and sync to database.

        Args:
            user_id: User ID to sync for
            db: Database session

        Returns:
            AccountStatus object

        Raises:
            IOLAuthError: If token is invalid or refresh fails
            IOLError: If IOL API call fails
        """
        try:
            # Get valid token
            token = await self.iol_token_manager.get_valid_token(db, user_id)

            # Fetch IOL account status
            iol_account = await self.iol_client.fetch_account_status(token)

            # Create/update account status
            cash_balance = Decimal(str(iol_account.get("saldo_disponible", 0)))
            buying_power = Decimal(str(iol_account.get("poder_compra", 0)))
            total_balance = Decimal(str(iol_account.get("patrimonio", 0)))

            now = datetime.now(timezone.utc)

            # Upsert account status
            stmt = (
                pg_insert(AccountStatus)
                .values(
                    user_id=user_id,
                    cash_balance=cash_balance,
                    buying_power=buying_power,
                    total_balance=total_balance,
                    currency="ARS",
                    synced_at=now,
                )
                .on_conflict_do_update(
                    index_elements=["user_id"],
                    set_={
                        "cash_balance": cash_balance,
                        "buying_power": buying_power,
                        "total_balance": total_balance,
                        "synced_at": now,
                    },
                )
            )
            await db.execute(stmt)
            await db.commit()

            logger.info(f"Account status synced for user {user_id}")

            return AccountStatus(
                user_id=user_id,
                cash_balance=cash_balance,
                buying_power=buying_power,
                total_balance=total_balance,
                currency="ARS",
                synced_at=now,
            )

        except (IOLAuthError, IOLError):
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Account status sync failed for user {user_id}: {str(e)}")
            raise
