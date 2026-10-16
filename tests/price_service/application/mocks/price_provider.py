from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
    from decimal import Decimal

    from services.price_service.core import Ticker


class MockPriceProvider:
    __responses: Mapping[Ticker, Decimal | Exception]

    def __init__(self, responses: Mapping[Ticker, Decimal | Exception]) -> None:
        self.__responses = responses

    async def get_index_price(self, ticker: Ticker) -> Decimal:
        response = self.__responses[ticker]
        if isinstance(response, Exception):
            raise response
        return response
