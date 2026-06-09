from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.analysis import AnalysisResponse
from app.services.fundamental_service import FundamentalService
from app.services.health_score import HealthScoreEngine
from app.services.peer_comparison import PeerComparisonService

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/{ticker}", response_model=AnalysisResponse)
async def analyze_ticker(
    ticker: str,
    current_user: User = Depends(get_current_user),
):
    ticker_upper = ticker.upper()
    fundamental = FundamentalService()
    metrics = await fundamental.compute(ticker_upper)

    if metrics is None:
        raise HTTPException(
            status_code=503,
            detail=f"No cached data for {ticker_upper}. Run ingestion first.",
        )

    health_engine = HealthScoreEngine()
    health = await health_engine.compute(ticker_upper)

    peers_service = PeerComparisonService()
    sector = metrics.pe_trailing.source if metrics.pe_trailing else None
    peers = await peers_service.compare(ticker_upper, sector)

    price = await fundamental.get_price(ticker_upper)
    price_date = await fundamental.get_price_date(ticker_upper)
    dividends = await fundamental.get_dividends(ticker_upper)
    earnings = await fundamental.get_earnings(ticker_upper)
    analysts = await fundamental.get_analysts(ticker_upper)

    return AnalysisResponse(
        ticker=ticker_upper,
        company_name=ticker_upper,
        sector=sector,
        price=price,
        price_date=price_date,
        fundamentals=metrics,
        earnings=earnings,
        dividends=dividends,
        analysts=analysts,
        peers=peers,
        health_score=health,
        cached_at=datetime.now(timezone.utc),
    )
