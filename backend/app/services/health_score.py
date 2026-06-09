from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from app.schemas.analysis import HealthScoreResult
from app.services.cache_service import CacheService
from app.services.fundamental_service import FundamentalService

VERDICTS = {
    (80, 100): "Strong Buy",
    (65, 79): "Accumulate",
    (45, 64): "Hold",
    (30, 44): "Reduce",
    (0, 29): "Avoid",
}


class HealthScoreEngine:

    def __init__(self):
        self.cache = CacheService()
        self.fundamental = FundamentalService()

    async def compute(self, ticker: str) -> HealthScoreResult | None:
        metrics = await self.fundamental.compute(ticker)
        if metrics is None:
            return None

        fund_quality = self._score_fundamental_quality(metrics)
        earnings_momentum = self._score_earnings_momentum(metrics)
        analyst_sentiment = await self._score_analyst_sentiment(ticker)
        technical_momentum = 15

        composite = fund_quality + earnings_momentum + analyst_sentiment + technical_momentum
        composite = max(0, min(100, composite))

        verdict = self._verdict(composite)
        top_drivers = self._top_drivers(
            fund_quality, earnings_momentum, analyst_sentiment, technical_momentum
        )

        return HealthScoreResult(
            composite=composite,
            verdict=verdict,
            fundamental_quality=fund_quality,
            earnings_momentum=earnings_momentum,
            analyst_sentiment=analyst_sentiment,
            technical_momentum=technical_momentum,
            top_drivers=top_drivers,
            computed_at=datetime.now(timezone.utc),
        )

    def _score_fundamental_quality(self, metrics) -> int:
        score = 15
        pe = self._decimal(metrics.pe_trailing.value) if metrics.pe_trailing else None
        pb = self._decimal(metrics.pb_ratio.value) if metrics.pb_ratio else None
        de = self._decimal(metrics.debt_to_equity.value) if metrics.debt_to_equity else None

        if pe is not None:
            if 12 <= pe <= 18:
                score += 5
            elif pe < 12:
                score += 2
            elif pe > 30 or pe < 0:
                score -= 5

        if pb is not None:
            if 0 < pb <= 3:
                score += 3
            elif pb > 5:
                score -= 3

        if de is not None:
            if de < 0.5:
                score += 2
            elif de > 2.0:
                score -= 5

        return max(0, min(25, score))

    def _score_earnings_momentum(self, metrics) -> int:
        score = 12
        growth = self._decimal(metrics.revenue_growth_yoy.value) if metrics.revenue_growth_yoy else None

        if growth is not None:
            if growth > 15:
                score += 8
            elif growth > 5:
                score += 4
            elif growth < 0:
                score -= 5

        return max(0, min(25, score))

    async def _score_analyst_sentiment(self, ticker: str) -> int:
        score = 12
        key = self.cache.build_key("finnhub", "analysts", ticker.upper())
        raw = await self.cache.get(key)

        if raw is None:
            return score

        ratings = raw.get("ratings", [])
        if not ratings:
            return score

        latest = ratings[0] if isinstance(ratings, list) else None
        if latest and isinstance(latest, dict):
            buy = latest.get("buy", 0) or 0
            hold = latest.get("hold", 0) or 0
            sell = latest.get("sell", 0) or 0
            total = buy + hold + sell
            if total > 0:
                buy_ratio = buy / total
                if buy_ratio > 0.7:
                    score += 8
                elif buy_ratio > 0.5:
                    score += 4
                elif buy_ratio < 0.3:
                    score -= 5

        return max(0, min(25, score))

    @staticmethod
    def _verdict(composite: int) -> str:
        for (low, high), label in VERDICTS.items():
            if low <= composite <= high:
                return label
        return "Hold"

    @staticmethod
    def _top_drivers(fq: int, em: int, as_: int, tm: int) -> list[str]:
        scores = {
            "Fundamental Quality": fq,
            "Earnings Momentum": em,
            "Analyst Sentiment": as_,
            "Technical Momentum": tm,
        }
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [k for k, v in sorted_scores[:3]]

    @staticmethod
    def _decimal(val) -> Decimal | None:
        if val is None:
            return None
        try:
            return Decimal(str(val))
        except InvalidOperation:
            return None
