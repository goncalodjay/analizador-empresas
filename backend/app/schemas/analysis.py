from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class RsiData(BaseModel):
    value: Decimal
    zone: str  # "oversold" | "neutral" | "overbought"
    trend: str  # "rising" | "falling" | "steady"


class MacdData(BaseModel):
    macd_line: Decimal
    signal_line: Decimal
    histogram: Decimal
    crossover: str  # "bullish" | "bearish" | "neutral"


class EmaData(BaseModel):
    ema_9: Decimal
    ema_21: Decimal
    ema_50: Decimal
    ema_200: Decimal
    price_vs_ema_9: str  # "above" | "below"
    price_vs_ema_200: str  # "above" | "below"
    golden_cross: bool
    death_cross: bool


class BollingerData(BaseModel):
    upper_band: Decimal
    middle_band: Decimal
    lower_band: Decimal
    bandwidth: Decimal
    squeeze: bool


class FiftyTwoWeekData(BaseModel):
    high: Decimal
    low: Decimal
    current: Decimal
    position_pct: Decimal


class RelativeVolumeData(BaseModel):
    ratio: Decimal
    label: str  # "low" | "average" | "high"


class TechnicalIndicators(BaseModel):
    rsi: RsiData | None = None
    macd: MacdData | None = None
    ema: EmaData | None = None
    bollinger: BollingerData | None = None
    fifty_two_week: FiftyTwoWeekData | None = None
    relative_volume: RelativeVolumeData | None = None
    source: str = "yfinance"
    computed_at: datetime


class MetricCard(BaseModel):
    label: str
    value: str | None = None
    category: str
    nature: str = "data_driven"
    source: str | None = None
    fetched_at: datetime | None = None


class EarningsSurprise(BaseModel):
    quarter: str
    estimated: Decimal | None
    actual: Decimal | None
    surprise_pct: Decimal | None


class DividendPayment(BaseModel):
    ex_date: date
    amount: Decimal


class FundamentalMetrics(BaseModel):
    pe_trailing: MetricCard | None = None
    pe_forward: MetricCard | None = None
    pb_ratio: MetricCard | None = None
    eps: MetricCard | None = None
    revenue_growth_yoy: MetricCard | None = None
    debt_to_equity: MetricCard | None = None
    current_ratio: MetricCard | None = None
    free_cash_flow: MetricCard | None = None
    market_cap: MetricCard | None = None
    beta: MetricCard | None = None


class EarningsData(BaseModel):
    upcoming_date: date | None = None
    surprises: list[EarningsSurprise] = []


class DividendData(BaseModel):
    current_yield: str | None = None
    payout_ratio: str | None = None
    growth_years: int = 0
    next_ex_date: date | None = None
    history: list[DividendPayment] = []


class AnalystData(BaseModel):
    buy_count: int = 0
    hold_count: int = 0
    sell_count: int = 0
    median_target: Decimal | None = None
    target_high: Decimal | None = None
    target_low: Decimal | None = None


class PeerRank(BaseModel):
    ticker: str
    name: str | None = None
    pe_trailing: Decimal | None
    revenue_growth: Decimal | None
    roe: Decimal | None
    debt_to_equity: Decimal | None


class PeerComparison(BaseModel):
    ticker: str
    sector: str | None = None
    peers: list[PeerRank] = []
    rankings: dict[str, int] = {}


class HealthScoreResult(BaseModel):
    composite: int
    verdict: str
    fundamental_quality: int
    earnings_momentum: int
    analyst_sentiment: int
    technical_momentum: int
    top_drivers: list[str] = []
    computed_at: datetime


class AnalysisResponse(BaseModel):
    ticker: str
    company_name: str | None = None
    sector: str | None = None
    price: Decimal | None = None
    price_date: datetime | None = None
    fundamentals: FundamentalMetrics | None = None
    earnings: EarningsData | None = None
    dividends: DividendData | None = None
    analysts: AnalystData | None = None
    peers: PeerComparison | None = None
    health_score: HealthScoreResult | None = None
    technical: TechnicalIndicators | None = None
    cached_at: datetime | None = None
