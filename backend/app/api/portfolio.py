from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.portfolio import (
    PortfolioPositionCreate,
    PortfolioPositionOut,
    PortfolioPositionUpdate,
)
from app.services import portfolio_service

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/positions", response_model=list[PortfolioPositionOut])
async def list_positions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    positions = await portfolio_service.get_positions(db, str(current_user.id))
    return positions


@router.post(
    "/positions",
    response_model=PortfolioPositionOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_position(
    payload: PortfolioPositionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        position = await portfolio_service.create_position(
            db, str(current_user.id), payload
        )
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Position for ticker {payload.ticker.upper()} already exists",
        )
    return position


@router.get("/positions/{position_id}", response_model=PortfolioPositionOut)
async def get_position(
    position_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    position = await portfolio_service.get_position(
        db, position_id, str(current_user.id)
    )
    if position is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Position not found")
    return position


@router.put("/positions/{position_id}", response_model=PortfolioPositionOut)
async def update_position(
    position_id: str,
    payload: PortfolioPositionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        position = await portfolio_service.update_position(
            db, position_id, str(current_user.id), payload
        )
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Position with this ticker already exists",
        )
    if position is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Position not found")
    return position


@router.delete("/positions/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_position(
    position_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await portfolio_service.delete_position(
        db, position_id, str(current_user.id)
    )
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Position not found")
