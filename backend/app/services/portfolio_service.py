from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.portfolio import PortfolioPosition
from app.schemas.portfolio import PortfolioPositionCreate, PortfolioPositionUpdate


async def get_positions(db: AsyncSession, user_id: str) -> list[PortfolioPosition]:
    result = await db.execute(
        select(PortfolioPosition)
        .where(PortfolioPosition.user_id == user_id)
        .order_by(PortfolioPosition.created_at.desc())
    )
    return list(result.scalars().all())


async def get_position(
    db: AsyncSession, position_id: str, user_id: str
) -> PortfolioPosition | None:
    result = await db.execute(
        select(PortfolioPosition).where(
            PortfolioPosition.id == position_id,
            PortfolioPosition.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()


async def create_position(
    db: AsyncSession, user_id: str, payload: PortfolioPositionCreate
) -> PortfolioPosition:
    position = PortfolioPosition(
        user_id=user_id,
        ticker=payload.ticker.upper(),
        shares=payload.shares,
        avg_buy_price=payload.avg_buy_price,
        sector=payload.sector,
        notes=payload.notes,
    )
    db.add(position)
    await db.commit()
    await db.refresh(position)
    return position


async def update_position(
    db: AsyncSession, position_id: str, user_id: str, payload: PortfolioPositionUpdate
) -> PortfolioPosition | None:
    position = await get_position(db, position_id, user_id)
    if position is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "ticker" and value is not None:
            value = value.upper()
        setattr(position, field, value)

    await db.commit()
    await db.refresh(position)
    return position


async def delete_position(
    db: AsyncSession, position_id: str, user_id: str
) -> bool:
    position = await get_position(db, position_id, user_id)
    if position is None:
        return False

    await db.delete(position)
    await db.commit()
    return True
