from datetime import datetime, timezone
from decimal import Decimal

from app.schemas.analysis import (
    FundamentalMetrics,
    MetricCard,
)
from app.services.health_score import HealthScoreEngine, VERDICTS


def _card(label: str, value: str, category: str = "valuation") -> MetricCard:
    return MetricCard(
        label=label,
        value=value,
        category=category,
        source="test",
        fetched_at=datetime.now(timezone.utc),
    )


def test_verdict_mapping():
    assert HealthScoreEngine._verdict(85) == "Strong Buy"
    assert HealthScoreEngine._verdict(70) == "Accumulate"
    assert HealthScoreEngine._verdict(50) == "Hold"
    assert HealthScoreEngine._verdict(35) == "Reduce"
    assert HealthScoreEngine._verdict(15) == "Avoid"


def test_verdict_boundaries():
    assert HealthScoreEngine._verdict(80) == "Strong Buy"
    assert HealthScoreEngine._verdict(65) == "Accumulate"
    assert HealthScoreEngine._verdict(45) == "Hold"
    assert HealthScoreEngine._verdict(30) == "Reduce"
    assert HealthScoreEngine._verdict(0) == "Avoid"
    assert HealthScoreEngine._verdict(100) == "Strong Buy"


def test_fundamental_quality_ideal():
    metrics = FundamentalMetrics(
        pe_trailing=_card("P/E", "15.0"),
        pb_ratio=_card("P/B", "2.0"),
        debt_to_equity=_card("D/E", "0.3"),
    )
    engine = HealthScoreEngine()
    score = engine._score_fundamental_quality(metrics)
    assert score == 25


def test_fundamental_quality_poor():
    metrics = FundamentalMetrics(
        pe_trailing=_card("P/E", "35.0"),
        pb_ratio=_card("P/B", "6.0"),
        debt_to_equity=_card("D/E", "3.0"),
    )
    engine = HealthScoreEngine()
    score = engine._score_fundamental_quality(metrics)
    assert score <= 5


def test_earnings_momentum_strong():
    metrics = FundamentalMetrics(
        revenue_growth_yoy=_card("Rev Growth", "20.0", "growth"),
    )
    engine = HealthScoreEngine()
    score = engine._score_earnings_momentum(metrics)
    assert score == 20


def test_earnings_momentum_declining():
    metrics = FundamentalMetrics(
        revenue_growth_yoy=_card("Rev Growth", "-5.0", "growth"),
    )
    engine = HealthScoreEngine()
    score = engine._score_earnings_momentum(metrics)
    assert score <= 10


def test_top_drivers():
    drivers = HealthScoreEngine._top_drivers(20, 15, 10, 15)
    assert drivers[0] == "Fundamental Quality"
    assert len(drivers) == 3


def test_health_score_result_structure():
    from app.schemas.analysis import HealthScoreResult
    result = HealthScoreResult(
        composite=72,
        verdict="Accumulate",
        fundamental_quality=20,
        earnings_momentum=18,
        analyst_sentiment=19,
        technical_momentum=15,
        top_drivers=["Analyst Sentiment", "Fundamental Quality", "Earnings Momentum"],
        computed_at=datetime.now(timezone.utc),
    )
    assert result.composite == 72
    assert result.verdict == "Accumulate"
