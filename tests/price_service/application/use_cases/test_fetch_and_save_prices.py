from decimal import Decimal

import pytest

from services.price_service.application.dtos import FetchAndSavePricesInputDTO
from services.price_service.application.use_cases import FetchAndSavePricesUseCase
from services.price_service.core import Price, PriceProviderError, Ticker
from tests.price_service.application.mocks import (
    FixedClock,
    MockPriceProvider,
    MockUnitOfWork,
)

TIMESTAMP = 1_700_000_000


def make_use_case(
    uow: MockUnitOfWork, responses: dict[Ticker, Decimal | Exception]
) -> FetchAndSavePricesUseCase:
    return FetchAndSavePricesUseCase(
        uow_factory=lambda: uow,
        price_provider=MockPriceProvider(responses),
        clock=FixedClock(TIMESTAMP),
    )


async def test_saves_prices_of_all_tickers() -> None:
    uow = MockUnitOfWork()
    use_case = make_use_case(
        uow, {Ticker.BTC_USD: Decimal("65000.1"), Ticker.ETH_USD: Decimal("3100")}
    )

    result = await use_case(FetchAndSavePricesInputDTO())

    assert uow.committed
    assert set(uow.prices.stored) == {
        Price(ticker=Ticker.BTC_USD, price=Decimal("65000.1"), timestamp=TIMESTAMP),
        Price(ticker=Ticker.ETH_USD, price=Decimal("3100"), timestamp=TIMESTAMP),
    }
    assert len(result.saved) == 2
    assert result.failed == ()


@pytest.mark.parametrize(
    "failure",
    [
        PriceProviderError(Ticker.ETH_USD, "timeout"),
        Decimal("-1"),
    ],
)
async def test_failed_ticker_does_not_block_others(
    failure: Decimal | Exception,
) -> None:
    uow = MockUnitOfWork()
    use_case = make_use_case(
        uow, {Ticker.BTC_USD: Decimal("65000"), Ticker.ETH_USD: failure}
    )

    result = await use_case(FetchAndSavePricesInputDTO())

    assert uow.committed
    assert [price.ticker for price in uow.prices.stored] == [Ticker.BTC_USD]
    assert [price.ticker for price in result.saved] == [Ticker.BTC_USD]
    assert result.failed == (Ticker.ETH_USD,)


async def test_does_not_open_transaction_when_all_tickers_failed() -> None:
    uow = MockUnitOfWork()
    use_case = make_use_case(
        uow,
        {
            Ticker.BTC_USD: PriceProviderError(Ticker.BTC_USD, "timeout"),
            Ticker.ETH_USD: PriceProviderError(Ticker.ETH_USD, "timeout"),
        },
    )

    result = await use_case(FetchAndSavePricesInputDTO())

    assert not uow.committed
    assert uow.prices.stored == ()
    assert result.saved == ()
    assert set(result.failed) == {Ticker.BTC_USD, Ticker.ETH_USD}


async def test_propagates_unexpected_errors() -> None:
    uow = MockUnitOfWork()
    use_case = make_use_case(
        uow, {Ticker.BTC_USD: Decimal("65000"), Ticker.ETH_USD: RuntimeError("boom")}
    )

    with pytest.RaisesGroup(RuntimeError):
        await use_case(FetchAndSavePricesInputDTO())

    assert uow.prices.stored == ()


async def test_fetches_only_requested_tickers() -> None:
    uow = MockUnitOfWork()
    use_case = make_use_case(uow, {Ticker.BTC_USD: Decimal("65000")})

    result = await use_case(FetchAndSavePricesInputDTO(tickers=(Ticker.BTC_USD,)))

    assert [price.ticker for price in result.saved] == [Ticker.BTC_USD]
