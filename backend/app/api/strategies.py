from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.strategies import ActivateRequest, StrategyCreate, StrategyOut, StrategyUpdate
from app.services import strategy_service

router = APIRouter(prefix="/strategies", tags=["strategies"])

_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Strategy not found",
)


@router.get("", response_model=list[StrategyOut])
async def list_strategies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await strategy_service.get_strategies(db, str(current_user.id))


@router.post("", response_model=StrategyOut, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    payload: StrategyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await strategy_service.create_strategy(db, payload, str(current_user.id))


@router.get("/{strategy_id}", response_model=StrategyOut)
async def get_strategy(
    strategy_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    strategy = await strategy_service.get_strategy(db, strategy_id, str(current_user.id))
    if strategy is None:
        raise _NOT_FOUND
    return strategy


@router.put("/{strategy_id}", response_model=StrategyOut)
async def update_strategy(
    strategy_id: str,
    payload: StrategyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    strategy = await strategy_service.update_strategy(
        db, strategy_id, payload, str(current_user.id)
    )
    if strategy is None:
        raise _NOT_FOUND
    return strategy


@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(
    strategy_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await strategy_service.delete_strategy(db, strategy_id, str(current_user.id))
    if not deleted:
        raise _NOT_FOUND


@router.patch("/{strategy_id}/activate", response_model=StrategyOut)
async def activate_strategy(
    strategy_id: str,
    payload: ActivateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    strategy = await strategy_service.set_active(
        db, strategy_id, str(current_user.id), payload.is_active
    )
    if strategy is None:
        raise _NOT_FOUND
    return strategy


@router.patch("/{strategy_id}/primary", response_model=StrategyOut)
async def set_primary_strategy(
    strategy_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    strategy = await strategy_service.set_primary(db, strategy_id, str(current_user.id))
    if strategy is None:
        raise _NOT_FOUND
    return strategy
