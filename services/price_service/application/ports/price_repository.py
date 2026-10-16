from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence

    from services.price_service.core import Price, Ticker


class PriceRepository(Protocol):
    async def add(self, price: Price) -> None: ...

    async def get_all(self, ticker: Ticker) -> Sequence[Price]: ...

    async def get_latest(self, ticker: Ticker) -> Price | None: ...

    async def get_by_date_range(
        self,
        ticker: Ticker,
        date_from: int | None = None,
        date_to: int | None = None,
    ) -> Sequence[Price]: ...
