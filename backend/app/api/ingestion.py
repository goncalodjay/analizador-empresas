from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.ingestion import IngestionResult
from app.services.ingestion_service import IngestionService

router = APIRouter(prefix="/ingestion", tags=["ingestion"])

_ingestion_service = IngestionService()


@router.post("/trigger", response_model=list[IngestionResult])
async def trigger_portfolio_ingestion(
    current_user: User = Depends(get_current_user),
):
    return await _ingestion_service.ingest_portfolio(str(current_user.id))


@router.post("/trigger/{ticker}", response_model=IngestionResult)
async def trigger_ticker_ingestion(
    ticker: str,
    current_user: User = Depends(get_current_user),
):
    return await _ingestion_service.ingest_ticker(
        ticker, str(current_user.id)
    )


@router.get("/status/{ticker}")
async def cache_status(
    ticker: str,
    current_user: User = Depends(get_current_user),
):
    return await _ingestion_service.get_cache_status(ticker)
