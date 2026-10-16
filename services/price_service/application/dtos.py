from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Self

from services.price_service.core import Price, Ticker

if TYPE_CHECKING:
    from collections.abc import Sequence
    from decimal import Decimal


@dataclass(frozen=True, slots=True)
class PriceDTO:
    ticker: Ticker
    price: Decimal
    timestamp: int

    @classmethod
    def from_entity(cls, price: Price) -> Self:
        return cls(ticker=price.ticker, price=price.price, timestamp=price.timestamp)


@dataclass(frozen=True, slots=True)
class PricesDTO:
    prices: Sequence[PriceDTO]


@dataclass(frozen=True, slots=True)
class GetPricesInputDTO:
    ticker: Ticker


@dataclass(frozen=True, slots=True)
class GetLatestPriceInputDTO:
    ticker: Ticker


@dataclass(frozen=True, slots=True)
class GetPricesByDateInputDTO:
    ticker: Ticker
    date_from: int | None = None
    date_to: int | None = None


@dataclass(frozen=True, slots=True)
class FetchAndSavePricesInputDTO:
    tickers: Sequence[Ticker] = field(default_factory=lambda: tuple(Ticker))


@dataclass(frozen=True, slots=True)
class FetchAndSavePricesOutputDTO:
    saved: Sequence[PriceDTO]
    failed: Sequence[Ticker]
