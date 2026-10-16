from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from decimal import Decimal

    from services.price_service.core import Ticker


class PriceProvider(Protocol):
    async def get_index_price(self, ticker: Ticker) -> Decimal: ...
