"""
Seed script for Portfolio CRUD demo data.

Creates a demo user with sample positions and watchlists.
Usage: cd backend && python seed.py

Requires DATABASE_URL, REDIS_URL, SECRET_KEY env vars or .env file.
"""
import asyncio
import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.core.database import _get_async_session_local
from app.core.security import get_password_hash
from app.models.user import User as UserModel
from app.models.portfolio import PortfolioPosition, Watchlist
from app.schemas.auth import UserCreate
from app.schemas.portfolio import PortfolioPositionCreate
from app.schemas.watchlist import WatchlistCreate
from app.services.user_service import get_user_by_email
from app.services.portfolio_service import create_position
from app.services.watchlist_service import create_watchlist, add_ticker

DEMO_EMAIL = "demo@analyzer.local"
DEMO_PASSWORD = "demopass123"

POSITIONS = [
    {"ticker": "AAPL", "shares": 50, "avg_buy_price": 175.50, "sector": "Technology", "notes": "Long-term hold"},
    {"ticker": "MSFT", "shares": 20, "avg_buy_price": 420.30, "sector": "Technology", "notes": "Cloud + AI play"},
    {"ticker": "GOOGL", "shares": 10, "avg_buy_price": 141.25, "sector": "Communication Services", "notes": None},
]

WATCHLISTS = [
    {
        "name": "Tech Giants",
        "description": "Mega-cap technology companies",
        "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA"],
    },
    {
        "name": "Dividend Candidates",
        "description": "Stable dividend payers for income portfolio",
        "tickers": ["JNJ", "PG", "KO", "PEP"],
    },
]


async def seed():
    session_local = _get_async_session_local()
    async with session_local() as db:
        user = await get_user_by_email(db, DEMO_EMAIL)
        if not user:
            user = UserModel(
                email=DEMO_EMAIL,
                password_hash=get_password_hash(DEMO_PASSWORD),
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            print(f"Created demo user: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        else:
            print(f"Demo user already exists: {user.email}")

        user_id = str(user.id)

        from sqlalchemy import select

        existing_pos = (await db.execute(
            select(PortfolioPosition).where(PortfolioPosition.user_id == user.id)
        )).scalars().first()

        if existing_pos is None:
            for pos_data in POSITIONS:
                pos = await create_position(
                    db, user_id,
                    PortfolioPositionCreate(
                        ticker=pos_data["ticker"],
                        shares=Decimal(str(pos_data["shares"])),
                        avg_buy_price=Decimal(str(pos_data["avg_buy_price"])),
                        sector=pos_data["sector"],
                        notes=pos_data["notes"],
                    ),
                )
                print(f"  Created position: {pos.ticker}")
        else:
            print("  Positions already exist, skipping.")

        existing_wl = (await db.execute(
            select(Watchlist).where(Watchlist.user_id == user.id)
        )).scalars().first()

        if existing_wl is None:
            for wl_data in WATCHLISTS:
                wl = await create_watchlist(
                    db, user_id,
                    WatchlistCreate(
                        name=wl_data["name"],
                        description=wl_data["description"],
                    ),
                )
                for ticker in wl_data["tickers"]:
                    await add_ticker(db, str(wl.id), user_id, ticker)
                print(f"  Created watchlist: {wl.name} ({len(wl_data['tickers'])} tickers)")
        else:
            print("  Watchlists already exist, skipping.")

    print("\nSeed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
