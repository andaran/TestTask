from typing import TYPE_CHECKING

import httpx
from pydantic import ValidationError

from services.price_service.core import PriceProviderError

from .schemas import IndexPriceResponse

if TYPE_CHECKING:
    from decimal import Decimal

    from services.price_service.core import Ticker


class DeribitPriceProvider:
    INDEX_PRICE_PATH = "/public/get_index_price"

    __client: httpx.AsyncClient

    def __init__(self, client: httpx.AsyncClient) -> None:
        self.__client = client

    async def get_index_price(self, ticker: Ticker) -> Decimal:
        try:
            response = await self.__client.get(
                self.INDEX_PRICE_PATH, params={"index_name": ticker.value}
            )
            response.raise_for_status()
            payload = IndexPriceResponse.model_validate_json(response.content)
        except httpx.HTTPError as error:
            raise PriceProviderError(ticker, str(error)) from error
        except ValidationError as error:
            raise PriceProviderError(ticker, "unexpected response format") from error

        return payload.result.index_price
