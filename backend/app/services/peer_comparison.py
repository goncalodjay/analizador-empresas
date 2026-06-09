from decimal import Decimal

from app.providers.factory import ProviderFactory
from app.schemas.analysis import PeerComparison, PeerRank
from app.services.cache_service import CacheService

SECTOR_PEERS: dict[str, list[str]] = {
    "Technology": ["MSFT", "GOOGL", "META", "AMZN", "NVDA"],
    "Communication Services": ["META", "GOOGL", "NFLX", "DIS", "VZ"],
    "Financial Services": ["JPM", "BAC", "WFC", "GS", "MS"],
    "Healthcare": ["JNJ", "PFE", "UNH", "ABBV", "MRK"],
    "Consumer Cyclical": ["AMZN", "TSLA", "HD", "MCD", "NKE"],
    "Consumer Defensive": ["PG", "KO", "PEP", "WMT", "COST"],
    "Energy": ["XOM", "CVX", "COP", "SLB", "EOG"],
    "Industrials": ["CAT", "BA", "GE", "UPS", "HON"],
    "Real Estate": ["PLD", "AMT", "EQIX", "CCI", "SPG"],
    "Utilities": ["NEE", "DUK", "SO", "D", "AEP"],
}


class PeerComparisonService:

    def __init__(self):
        self.cache = CacheService()
        self.provider = ProviderFactory.get_price_provider()

    async def compare(self, ticker: str, sector: str | None) -> PeerComparison | None:
        ticker_upper = ticker.upper()
        if not sector or sector not in SECTOR_PEERS:
            return PeerComparison(ticker=ticker_upper, sector=sector)

        peer_tickers = SECTOR_PEERS[sector]
        all_tickers = [t for t in peer_tickers if t.upper() != ticker_upper]
        if all_tickers:
            all_tickers = [ticker_upper] + all_tickers[:5]
        else:
            all_tickers = [ticker_upper] + peer_tickers[:5]

        peers: list[PeerRank] = []
        for t in all_tickers:
            key = self.cache.build_key(self.provider.name, "fundamentals", t.upper())
            raw = await self.cache.get(key)
            if raw is None:
                continue
            peers.append(
                PeerRank(
                    ticker=t.upper(),
                    name=raw.get("name"),
                    pe_trailing=self._dec(raw.get("pe_ratio")),
                    revenue_growth=self._dec(raw.get("revenue_growth_yoy")),
                    roe=self._dec(raw.get("roe")),
                    debt_to_equity=self._dec(raw.get("debt_to_equity")),
                )
            )

        rankings = {}
        if peers:
            for metric in ["pe_trailing", "revenue_growth", "roe", "debt_to_equity"]:
                sorted_peers = sorted(
                    [p for p in peers if getattr(p, metric) is not None],
                    key=lambda p: getattr(p, metric) or Decimal(0),
                )
                target = next(
                    (i for i, p in enumerate(sorted_peers) if p.ticker == ticker_upper),
                    None,
                )
                if target is not None:
                    rankings[metric] = len(sorted_peers) - target

        return PeerComparison(
            ticker=ticker_upper,
            sector=sector,
            peers=peers,
            rankings=rankings,
        )

    @staticmethod
    def _dec(val) -> Decimal | None:
        if val is None:
            return None
        try:
            return Decimal(str(val))
        except Exception:
            return None
