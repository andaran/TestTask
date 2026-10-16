from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from services.price_service.core import Price, Ticker


class InMemoryPriceRepository:
    __prices: list[Price]

    def __init__(self, prices: Iterable[Price] = ()) -> None:
        self.__prices = list(prices)

    @property
    def stored(self) -> Sequence[Price]:
        return tuple(self.__prices)

    async def add(self, price: Price) -> None:
        self.__prices.append(price)

    async def get_all(self, ticker: Ticker) -> Sequence[Price]:
        return await self.get_by_date_range(ticker)

    async def get_latest(self, ticker: Ticker) -> Price | None:
        prices = await self.get_all(ticker)
        return prices[-1] if prices else None

    async def get_by_date_range(
        self,
        ticker: Ticker,
        date_from: int | None = None,
        date_to: int | None = None,
    ) -> Sequence[Price]:
        return sorted(
            (
                price
                for price in self.__prices
                if price.ticker == ticker
                and (date_from is None or price.timestamp >= date_from)
                and (date_to is None or price.timestamp <= date_to)
            ),
            key=lambda price: price.timestamp,
        )
