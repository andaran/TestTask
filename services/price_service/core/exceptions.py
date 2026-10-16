from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from decimal import Decimal

    from .entities import Ticker


class DomainError(Exception):
    pass


class NegativePriceError(DomainError):
    ticker: Ticker
    price: Decimal

    def __init__(self, ticker: Ticker, price: Decimal) -> None:
        self.ticker = ticker
        self.price = price
        super().__init__(f"Price of '{ticker}' must not be negative, got {price}")


class PriceNotFoundError(DomainError):
    ticker: Ticker

    def __init__(self, ticker: Ticker) -> None:
        self.ticker = ticker
        super().__init__(f"No prices found for ticker '{ticker}'")


class InvalidDateRangeError(DomainError):
    date_from: int
    date_to: int

    def __init__(self, date_from: int, date_to: int) -> None:
        self.date_from = date_from
        self.date_to = date_to
        super().__init__(
            f"date_from ({date_from}) must not be greater than date_to ({date_to})"
        )


class PriceProviderError(DomainError):
    ticker: Ticker
    reason: str

    def __init__(self, ticker: Ticker, reason: str) -> None:
        self.ticker = ticker
        self.reason = reason
        super().__init__(f"Failed to get index price for '{ticker}': {reason}")
