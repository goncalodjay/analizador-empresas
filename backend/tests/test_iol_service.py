"""Tests for IOL token manager service."""
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.base import Base
from app.models import User, IOLCredentials
from app.services.iol_service import IOLTokenManager
from app.providers.iol_provider import IOLAuthError


@pytest.fixture
async def db_session():
    """Create an async database session for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password",
        timezone="America/Argentina/Buenos_Aires",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_store_credentials(db_session, test_user, encryption_key):
    """Test storing IOL credentials."""
    from app.models.iol_credentials import IOLCredentials

    manager = IOLTokenManager()

    with patch("app.models.iol_credentials.settings.ENCRYPTION_KEY", encryption_key):
        with patch("app.services.iol_service.IOLClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.authenticate = AsyncMock(
                return_value={
                    "access_token": "test_token",
                    "expires_in": 900,
                    "refresh_token": "test_refresh",
                }
            )

            creds = await manager.store_credentials(
                db_session, test_user.id, "user@iol.com", "password123"
            )

            assert creds.user_id == test_user.id
            assert creds.iol_username == "user@iol.com"
            assert creds.encrypted_password != "password123"

            # Verify it's in the database
            from sqlalchemy import select

            result = await db_session.execute(
                select(IOLCredentials).where(IOLCredentials.user_id == test_user.id)
            )
            db_creds = result.scalar_one()
            assert db_creds.iol_username == "user@iol.com"


@pytest.mark.asyncio
async def test_get_valid_token_returns_token(db_session, test_user, encryption_key):
    """Test getting a valid token."""
    from app.models.iol_credentials import IOLCredentials

    manager = IOLTokenManager()
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(minutes=10)

    with patch("app.models.iol_credentials.settings.ENCRYPTION_KEY", encryption_key):
        # Create credentials
        creds = IOLCredentials(
            user_id=test_user.id,
            iol_username="user@iol.com",
            encrypted_password=IOLCredentials.encrypt_password("password123"),
            access_token="valid_token",
            token_expires_at=expiry,
            refresh_token="refresh_token",
        )
        db_session.add(creds)
        await db_session.commit()

        # Get token
        token = await manager.get_valid_token(db_session, test_user.id)

        assert token == "valid_token"


@pytest.mark.asyncio
async def test_get_valid_token_refreshes_if_near_expiry(db_session, test_user, encryption_key):
    """Test that get_valid_token refreshes if token is near expiry."""
    from app.models.iol_credentials import IOLCredentials

    manager = IOLTokenManager()
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(seconds=30)  # Expires soon

    with patch("app.models.iol_credentials.settings.ENCRYPTION_KEY", encryption_key):
        # Create credentials
        creds = IOLCredentials(
            user_id=test_user.id,
            iol_username="user@iol.com",
            encrypted_password=IOLCredentials.encrypt_password("password123"),
            access_token="old_token",
            token_expires_at=expiry,
            refresh_token="refresh_token",
        )
        db_session.add(creds)
        await db_session.commit()

        # Mock the IOL client refresh
        with patch("app.services.iol_service.IOLClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            mock_client.refresh_token = AsyncMock(
                return_value={
                    "access_token": "new_token",
                    "expires_in": 900,
                    "refresh_token": "new_refresh",
                }
            )

            token = await manager.get_valid_token(db_session, test_user.id)

            # Should have called refresh and returned new token
            mock_client.refresh_token.assert_called_once()
            assert token == "new_token"


@pytest.mark.asyncio
async def test_revoke_credentials(db_session, test_user, encryption_key):
    """Test revoking IOL credentials."""
    from app.models.iol_credentials import IOLCredentials

    manager = IOLTokenManager()
    now = datetime.now(timezone.utc)

    with patch("app.models.iol_credentials.settings.ENCRYPTION_KEY", encryption_key):
        # Create credentials
        creds = IOLCredentials(
            user_id=test_user.id,
            iol_username="user@iol.com",
            encrypted_password=IOLCredentials.encrypt_password("password123"),
            access_token="token",
            token_expires_at=now + timedelta(minutes=15),
            refresh_token="refresh",
        )
        db_session.add(creds)
        await db_session.commit()

        # Revoke
        await manager.revoke_credentials(db_session, test_user.id)

        # Verify deleted
        from sqlalchemy import select

        result = await db_session.execute(
            select(IOLCredentials).where(IOLCredentials.user_id == test_user.id)
        )
        assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_get_credentials_status_connected(db_session, test_user, encryption_key):
    """Test getting connection status for connected user."""
    from app.models.iol_credentials import IOLCredentials

    manager = IOLTokenManager()
    now = datetime.now(timezone.utc)

    with patch("app.models.iol_credentials.settings.ENCRYPTION_KEY", encryption_key):
        # Create credentials
        creds = IOLCredentials(
            user_id=test_user.id,
            iol_username="user@iol.com",
            encrypted_password=IOLCredentials.encrypt_password("password123"),
            access_token="token",
            token_expires_at=now + timedelta(minutes=15),
            refresh_token="refresh",
        )
        db_session.add(creds)
        await db_session.commit()

        # Get status
        status = await manager.get_credentials_status(db_session, test_user.id)

        assert status["connected"] is True
        assert status["iol_username"] == "user@iol.com"


@pytest.mark.asyncio
async def test_get_credentials_status_disconnected(db_session, test_user):
    """Test getting connection status for disconnected user."""
    manager = IOLTokenManager()

    # Get status for user with no credentials
    status = await manager.get_credentials_status(db_session, test_user.id)

    assert status["connected"] is False


@pytest.fixture
def encryption_key():
    """Encryption key for testing."""
    from cryptography.fernet import Fernet

    return Fernet.generate_key().decode()
