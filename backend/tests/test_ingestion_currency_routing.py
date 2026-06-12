"""Test ingestion service currency-aware routing for PR 4: Currency-Aware Pricing."""
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.base import Base
from app.models.portfolio_holdings import PortfolioHolding
from app.models.user import User
from app.services.ingestion_service import IngestionService
from app.schemas.ingestion import IngestionResult


class TestIngestionServiceCurrencyRouting:
    """Test IngestionService routes to correct provider based on holding currency."""

    @pytest.fixture
    async def db_session(self):
        """Create in-memory SQLite test database."""
        engine = create_async_engine(
            "sqlite+aiosqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async_session = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session() as session:
            yield session

        await engine.dispose()

    @pytest.mark.asyncio
    async def test_ingest_ticker_with_ars_currency_uses_iol_provider(self, db_session):
        """Test that ingest_ticker with ARS currency uses IOL provider."""
        # Create test user and holding
        user_id = uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            password_hash="hashed-password",
        )
        db_session.add(user)

        holding = PortfolioHolding(
            user_id=user_id,
            ticker="GGAL",
            quantity=Decimal("50"),
            avg_buy_price=Decimal("250.00"),
            currency="ARS",
            synced_at=datetime.now(timezone.utc),
        )
        db_session.add(holding)
        await db_session.commit()

        ingestion_service = IngestionService()

        with patch("app.services.ingestion_service.ProviderFactory.get_price_provider") as mock_factory:
            mock_iol_provider = AsyncMock()
            mock_iol_provider.name = "iol-bcba"
            mock_iol_provider.fetch_price.return_value = AsyncMock(
                ticker="GGAL",
                close=Decimal("250.50"),
                source="iol-bcba"
            )
            mock_factory.return_value = mock_iol_provider

            # Execute: ingest with currency from portfolio
            result = await ingestion_service.ingest_ticker_with_currency(
                ticker="GGAL",
                user_id=user_id,
                currency="ARS"
            )

            # Assertions: IOL provider should be called
            mock_factory.assert_called_with(currency="ARS")
            assert result.source == "iol-bcba" or result.price is True

    @pytest.mark.asyncio
    async def test_ingest_ticker_with_usd_currency_uses_yfinance_provider(self, db_session):
        """Test that ingest_ticker with USD currency uses yfinance provider."""
        user_id = uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            password_hash="hashed-password",
        )
        db_session.add(user)

        holding = PortfolioHolding(
            user_id=user_id,
            ticker="AAPL",
            quantity=Decimal("10"),
            avg_buy_price=Decimal("150.00"),
            currency="USD",
            synced_at=datetime.now(timezone.utc),
        )
        db_session.add(holding)
        await db_session.commit()

        ingestion_service = IngestionService()

        with patch("app.services.ingestion_service.ProviderFactory.get_price_provider") as mock_factory:
            mock_yf_provider = AsyncMock()
            mock_yf_provider.name = "yfinance"
            mock_yf_provider.fetch_price.return_value = AsyncMock(
                ticker="AAPL",
                close=Decimal("150.30"),
                source="yfinance"
            )
            mock_factory.return_value = mock_yf_provider

            # Execute
            result = await ingestion_service.ingest_ticker_with_currency(
                ticker="AAPL",
                user_id=user_id,
                currency="USD"
            )

            # Assertions: yfinance provider should be called
            mock_factory.assert_called_with(currency="USD")

    @pytest.mark.asyncio
    async def test_ingest_ticker_fetches_currency_from_portfolio_if_not_provided(self, db_session):
        """Test that ingest_ticker fetches currency from portfolio if not provided."""
        user_id = uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            password_hash="hashed-password",
        )
        db_session.add(user)

        holding = PortfolioHolding(
            user_id=user_id,
            ticker="GGAL",
            quantity=Decimal("50"),
            avg_buy_price=Decimal("250.00"),
            currency="ARS",
            synced_at=datetime.now(timezone.utc),
        )
        db_session.add(holding)
        await db_session.commit()

        ingestion_service = IngestionService()

        with patch("app.services.ingestion_service.ProviderFactory.get_price_provider") as mock_factory:
            mock_iol_provider = AsyncMock()
            mock_iol_provider.name = "iol-bcba"
            mock_iol_provider.fetch_price.return_value = AsyncMock(
                ticker="GGAL",
                close=Decimal("250.50"),
                source="iol-bcba"
            )
            mock_factory.return_value = mock_iol_provider

            # Execute: ingest WITHOUT providing currency; should fetch from portfolio
            result = await ingestion_service.ingest_ticker_with_currency(
                ticker="GGAL",
                user_id=user_id,
                db=db_session
            )

            # Assertions: factory should be called with ARS (fetched from portfolio)
            mock_factory.assert_called_with(currency="ARS")

    @pytest.mark.asyncio
    async def test_ingest_ticker_defaults_to_usd_if_not_in_portfolio(self, db_session):
        """Test that ingest_ticker defaults to USD if ticker not in portfolio."""
        user_id = uuid4()
        user = User(
            id=user_id,
            email="test@example.com",
            password_hash="hashed-password",
        )
        db_session.add(user)
        await db_session.commit()

        ingestion_service = IngestionService()

        with patch("app.services.ingestion_service.ProviderFactory.get_price_provider") as mock_factory:
            mock_yf_provider = AsyncMock()
            mock_yf_provider.name = "yfinance"
            mock_yf_provider.fetch_price.return_value = AsyncMock(
                ticker="TSLA",
                close=Decimal("250.00"),
                source="yfinance"
            )
            mock_factory.return_value = mock_yf_provider

            # Execute: ingest ticker NOT in portfolio
            result = await ingestion_service.ingest_ticker_with_currency(
                ticker="TSLA",
                user_id=user_id,
                db=db_session
            )

            # Assertions: factory should default to USD
            mock_factory.assert_called_with(currency="USD")

    def test_ingestion_service_has_ingest_ticker_with_currency_method(self):
        """Test that IngestionService has ingest_ticker_with_currency method."""
        service = IngestionService()
        assert hasattr(service, "ingest_ticker_with_currency")
        assert callable(service.ingest_ticker_with_currency)
