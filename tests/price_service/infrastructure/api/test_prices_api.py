from decimal import Decimal
from functools import partial
from typing import TYPE_CHECKING

import httpx
import pytest

from services.price_service.core import Price, Ticker
from services.price_service.entrypoints.rest import app
from services.price_service.infrastructure.api.dependencies import get_uow_factory
from tests.price_service.application.mocks import (
    InMemoryPriceRepository,
    MockUnitOfWork,
)
from tests.price_service.application.samples import BTC_PRICES, ETH_PRICES

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


def use_repository(repository: InMemoryPriceRepository) -> None:
    app.dependency_overrides[get_uow_factory] = lambda: partial(
        MockUnitOfWork, repository
    )


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    use_repository(InMemoryPriceRepository((*BTC_PRICES, *ETH_PRICES)))
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()


async def test_get_prices(client: httpx.AsyncClient) -> None:
    response = await client.get("/prices", params={"ticker": "btc_usd"})

    assert response.status_code == 200
    assert response.json() == {
        "prices": [
            {"ticker": "btc_usd", "price": "60000.5", "timestamp": 100},
            {"ticker": "btc_usd", "price": "60100", "timestamp": 160},
            {"ticker": "btc_usd", "price": "60200.25", "timestamp": 220},
        ]
    }


async def test_get_latest_price(client: httpx.AsyncClient) -> None:
    response = await client.get("/prices/latest", params={"ticker": "eth_usd"})

    assert response.status_code == 200
    assert response.json() == {"ticker": "eth_usd", "price": "3000", "timestamp": 130}


@pytest.mark.parametrize(
    ("stored", "expected"),
    [
        (Decimal("82246.58000000"), "82246.58"),
        (Decimal("65000.00000000"), "65000"),
        (Decimal("0.00000001"), "0.00000001"),
        (Decimal("0E-8"), "0"),
    ],
)
async def test_price_is_serialized_without_trailing_zeros(
    client: httpx.AsyncClient, stored: Decimal, expected: str
) -> None:
    use_repository(
        InMemoryPriceRepository(
            [Price(ticker=Ticker.BTC_USD, price=stored, timestamp=1)]
        )
    )

    response = await client.get("/prices/latest", params={"ticker": "btc_usd"})

    assert response.json()["price"] == expected


async def test_get_latest_price_returns_404_without_data(
    client: httpx.AsyncClient,
) -> None:
    use_repository(InMemoryPriceRepository(BTC_PRICES))

    response = await client.get("/prices/latest", params={"ticker": "eth_usd"})

    assert response.status_code == 404
    assert "eth_usd" in response.json()["detail"]


async def test_get_prices_by_date(client: httpx.AsyncClient) -> None:
    response = await client.get(
        "/prices/by-date",
        params={"ticker": "btc_usd", "date_from": 150, "date_to": 220},
    )

    assert response.status_code == 200
    assert [price["timestamp"] for price in response.json()["prices"]] == [160, 220]


async def test_get_prices_by_date_rejects_inverted_range(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get(
        "/prices/by-date",
        params={"ticker": "btc_usd", "date_from": 300, "date_to": 100},
    )

    assert response.status_code == 422


@pytest.mark.parametrize("path", ["/prices", "/prices/latest", "/prices/by-date"])
@pytest.mark.parametrize("params", [{}, {"ticker": "doge_usd"}])
async def test_requires_valid_ticker(
    client: httpx.AsyncClient, path: str, params: dict[str, str]
) -> None:
    response = await client.get(path, params=params)

    assert response.status_code == 422


async def test_rejects_negative_dates(client: httpx.AsyncClient) -> None:
    response = await client.get(
        "/prices/by-date", params={"ticker": "btc_usd", "date_from": -1}
    )

    assert response.status_code == 422
