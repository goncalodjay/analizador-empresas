from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price_history import PriceHistory
from app.schemas.prices import PricePoint, PriceSeriesResponse


class PriceHistoryService:

    async def get_series(
        self,
        db: AsyncSession,
        ticker: str,
        from_date: date,
        to_date: date,
    ) -> PriceSeriesResponse:
        """Query price_history for ticker between from_date and to_date (inclusive).

        Returns PriceSeriesResponse with empty points when no rows are found.
        """
        stmt = (
            select(PriceHistory)
            .where(
                PriceHistory.ticker == ticker.upper(),
                PriceHistory.date >= from_date,
                PriceHistory.date <= to_date,
            )
            .order_by(PriceHistory.date.asc())
        )

        result = await db.execute(stmt)
        rows = result.scalars().all()

        points = [
            PricePoint(
                date=row.date,
                open=row.open,
                high=row.high,
                low=row.low,
                close=row.close,
                volume=row.volume,
            )
            for row in rows
        ]

        freshness = "fresh" if points else "stale"
        fetched_at = rows[-1].fetched_at if rows else None

        return PriceSeriesResponse(
            ticker=ticker.upper(),
            points=points,
            from_date=from_date,
            to_date=to_date,
            count=len(points),
            source="yfinance",
            freshness=freshness,
            fetched_at=fetched_at,
        )
