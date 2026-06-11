from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.prices import PriceSeriesResponse
from app.services.price_history_service import PriceHistoryService

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("/{ticker}", response_model=PriceSeriesResponse)
async def get_price_history(
    ticker: str,
    from_: date | None = Query(None, alias="from"),
    to: date | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()

    resolved_to = to if to is not None else today
    resolved_from = from_ if from_ is not None else resolved_to - timedelta(days=365)

    if resolved_from > resolved_to:
        raise HTTPException(
            status_code=400,
            detail="'from' must be on or before 'to'",
        )

    service = PriceHistoryService()
    return await service.get_series(db, ticker, resolved_from, resolved_to)
