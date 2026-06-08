import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.portfolio import Watchlist, WatchlistTicker
from app.schemas.watchlist import WatchlistCreate, WatchlistUpdate


def _to_uuid(value: str) -> uuid.UUID:
    return uuid.UUID(value)


async def get_watchlists(db: AsyncSession, user_id: str) -> list[Watchlist]:
    result = await db.execute(
        select(Watchlist)
        .where(Watchlist.user_id == _to_uuid(user_id))
        .options(selectinload(Watchlist.tickers))
        .order_by(Watchlist.created_at.desc())
    )
    return list(result.scalars().all())


async def get_watchlist(
    db: AsyncSession, watchlist_id: str, user_id: str
) -> Watchlist | None:
    result = await db.execute(
        select(Watchlist)
        .where(
            Watchlist.id == _to_uuid(watchlist_id),
            Watchlist.user_id == _to_uuid(user_id),
        )
        .options(selectinload(Watchlist.tickers))
    )
    return result.scalar_one_or_none()


async def create_watchlist(
    db: AsyncSession, user_id: str, payload: WatchlistCreate
) -> Watchlist:
    watchlist = Watchlist(
        user_id=_to_uuid(user_id),
        name=payload.name,
        description=payload.description,
    )
    db.add(watchlist)
    await db.commit()
    await db.refresh(watchlist)

    result = await db.execute(
        select(Watchlist)
        .options(selectinload(Watchlist.tickers))
        .where(Watchlist.id == watchlist.id)
    )
    return result.scalar_one()


async def update_watchlist(
    db: AsyncSession, watchlist_id: str, user_id: str, payload: WatchlistUpdate
) -> Watchlist | None:
    watchlist = await get_watchlist(db, watchlist_id, user_id)
    if watchlist is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(watchlist, field, value)

    await db.commit()

    result = await db.execute(
        select(Watchlist)
        .options(selectinload(Watchlist.tickers))
        .where(Watchlist.id == _to_uuid(watchlist_id))
    )
    return result.scalar_one()


async def delete_watchlist(
    db: AsyncSession, watchlist_id: str, user_id: str
) -> bool:
    watchlist = await get_watchlist(db, watchlist_id, user_id)
    if watchlist is None:
        return False

    await db.delete(watchlist)
    await db.commit()
    return True


async def add_ticker(
    db: AsyncSession, watchlist_id: str, user_id: str, ticker: str
) -> Watchlist | None:
    watchlist = await get_watchlist(db, watchlist_id, user_id)
    if watchlist is None:
        return None

    ticker_upper = ticker.upper()
    existing = next(
        (t for t in watchlist.tickers if t.ticker == ticker_upper), None
    )
    if existing:
        return watchlist

    watchlist_ticker = WatchlistTicker(
        watchlist_id=_to_uuid(watchlist_id),
        ticker=ticker_upper,
    )
    db.add(watchlist_ticker)
    await db.commit()
    await db.refresh(watchlist)
    return watchlist


async def remove_ticker(
    db: AsyncSession, watchlist_id: str, user_id: str, ticker: str
) -> bool:
    watchlist = await get_watchlist(db, watchlist_id, user_id)
    if watchlist is None:
        return False

    ticker_upper = ticker.upper()
    target = next(
        (t for t in watchlist.tickers if t.ticker == ticker_upper), None
    )
    if target is None:
        return False

    await db.delete(target)
    await db.commit()
    return True
