from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.ingestion import (
    NormalizedCompanyInfo,
    NormalizedDividend,
    NormalizedFundamentals,
    NormalizedPriceBar,
    NormalizedPriceData,
)


@dataclass
class ProviderMeta:
    name: str
    rate_limit_per_minute: int | None = None
    requires_api_key: bool = False


class AbstractMarketDataProvider(ABC):

    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    def rate_limit_per_minute(self) -> int | None:
        return None

    @property
    def requires_api_key(self) -> bool:
        return False

    @abstractmethod
    async def fetch_price(self, ticker: str) -> NormalizedPriceData: ...

    @abstractmethod
    async def fetch_fundamentals(
        self, ticker: str
    ) -> NormalizedFundamentals: ...

    async def fetch_price_history(
        self, ticker: str, period: str = "1y"
    ) -> list[NormalizedPriceBar]:
        return []

    async def fetch_dividends(
        self, ticker: str
    ) -> list[NormalizedDividend]:
        return []

    async def fetch_company_info(
        self, ticker: str
    ) -> NormalizedCompanyInfo:
        raise NotImplementedError
