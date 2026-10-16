from decimal import Decimal

import httpx
import pytest

from services.price_service.core import PriceProviderError, Ticker
from services.price_service.infrastructure.deribit import DeribitPriceProvider

BASE_URL = "https://deribit.test/api/v2"


def make_provider(transport: httpx.MockTransport) -> DeribitPriceProvider:
    return DeribitPriceProvider(
        httpx.AsyncClient(base_url=BASE_URL, transport=transport)
    )


async def test_returns_index_price_without_precision_loss() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(
            200,
            content=b'{"jsonrpc":"2.0","result":{"index_price":65432.12345678,'
            b'"estimated_delivery_price":65432.12}}',
        )

    price = await make_provider(httpx.MockTransport(handler)).get_index_price(
        Ticker.ETH_USD
    )

    assert price == Decimal("65432.12345678")
    assert requests[0].url.path == "/api/v2/public/get_index_price"
    assert requests[0].url.params["index_name"] == "eth_usd"


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(400, json={"error": {"code": -32602, "message": "Invalid"}}),
        httpx.Response(503),
        httpx.Response(200, json={"result": {}}),
        httpx.Response(200, json={"result": {"index_price": "abc"}}),
        httpx.Response(200, content=b"not json"),
    ],
)
async def test_raises_provider_error_on_bad_response(response: httpx.Response) -> None:
    provider = make_provider(httpx.MockTransport(lambda _: response))

    with pytest.raises(PriceProviderError) as error:
        await provider.get_index_price(Ticker.BTC_USD)

    assert error.value.ticker is Ticker.BTC_USD


async def test_raises_provider_error_on_network_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("timed out", request=request)

    with pytest.raises(PriceProviderError, match="timed out"):
        await make_provider(httpx.MockTransport(handler)).get_index_price(
            Ticker.BTC_USD
        )
