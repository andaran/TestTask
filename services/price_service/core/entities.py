from dataclasses import dataclass
from enum import StrEnum, auto
from typing import TYPE_CHECKING

from .exceptions import NegativePriceError

if TYPE_CHECKING:
    from decimal import Decimal


class Ticker(StrEnum):
    BTC_USD = auto()
    ETH_USD = auto()


@dataclass(frozen=True, slots=True)
class Price:
    ticker: Ticker
    price: Decimal
    timestamp: int

    def __post_init__(self) -> None:
        if self.price < 0:
            raise NegativePriceError(self.ticker, self.price)
