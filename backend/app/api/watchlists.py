from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.watchlist import (
    WatchlistCreate,
    WatchlistDetail,
    WatchlistOut,
    WatchlistTickerAdd,
    WatchlistUpdate,
)
from app.services import watchlist_service

router = APIRouter(prefix="/watchlists", tags=["watchlists"])


def _watchlist_to_out(watchlist) -> WatchlistOut:
    return WatchlistOut(
        id=watchlist.id,
        name=watchlist.name,
        description=watchlist.description,
        ticker_count=len(watchlist.tickers),
        created_at=watchlist.created_at,
    )


def _watchlist_to_detail(watchlist) -> WatchlistDetail:
    return WatchlistDetail(
        id=watchlist.id,
        name=watchlist.name,
        description=watchlist.description,
        ticker_count=len(watchlist.tickers),
        created_at=watchlist.created_at,
        tickers=watchlist.tickers,
    )


@router.get("", response_model=list[WatchlistOut])
async def list_watchlists(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    watchlists = await watchlist_service.get_watchlists(db, str(current_user.id))
    return [_watchlist_to_out(w) for w in watchlists]


@router.post("", response_model=WatchlistOut, status_code=status.HTTP_201_CREATED)
async def create_watchlist(
    payload: WatchlistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    watchlist = await watchlist_service.create_watchlist(
        db, str(current_user.id), payload
    )
    return _watchlist_to_out(watchlist)


@router.get("/{watchlist_id}", response_model=WatchlistDetail)
async def get_watchlist(
    watchlist_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    watchlist = await watchlist_service.get_watchlist(
        db, watchlist_id, str(current_user.id)
    )
    if watchlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found")
    return _watchlist_to_detail(watchlist)


@router.put("/{watchlist_id}", response_model=WatchlistOut)
async def update_watchlist(
    watchlist_id: str,
    payload: WatchlistUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    watchlist = await watchlist_service.update_watchlist(
        db, watchlist_id, str(current_user.id), payload
    )
    if watchlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found")
    return _watchlist_to_out(watchlist)


@router.delete("/{watchlist_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_watchlist(
    watchlist_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = await watchlist_service.delete_watchlist(
        db, watchlist_id, str(current_user.id)
    )
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found")


@router.post("/{watchlist_id}/tickers", response_model=WatchlistDetail)
async def add_ticker(
    watchlist_id: str,
    payload: WatchlistTickerAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    watchlist = await watchlist_service.add_ticker(
        db, watchlist_id, str(current_user.id), payload.ticker
    )
    if watchlist is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist not found")
    return _watchlist_to_detail(watchlist)


@router.delete(
    "/{watchlist_id}/tickers/{ticker}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_ticker(
    watchlist_id: str,
    ticker: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    removed = await watchlist_service.remove_ticker(
        db, watchlist_id, str(current_user.id), ticker
    )
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist or ticker not found",
        )
