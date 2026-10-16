import pytest

from services.price_service.application.dtos import GetLatestPriceInputDTO, PriceDTO
from services.price_service.application.use_cases import GetLatestPriceUseCase
from services.price_service.core import PriceNotFoundError, Ticker
from tests.price_service.application.mocks import (
    InMemoryPriceRepository,
    MockUnitOfWork,
)
from tests.price_service.application.samples import BTC_PRICES


async def test_returns_latest_price(uow: MockUnitOfWork) -> None:
    use_case = GetLatestPriceUseCase(lambda: uow)

    result = await use_case(GetLatestPriceInputDTO(ticker=Ticker.BTC_USD))

    assert result == PriceDTO.from_entity(BTC_PRICES[-1])


async def test_raises_when_ticker_has_no_prices() -> None:
    uow = MockUnitOfWork(InMemoryPriceRepository(BTC_PRICES))
    use_case = GetLatestPriceUseCase(lambda: uow)

    with pytest.raises(PriceNotFoundError) as error:
        await use_case(GetLatestPriceInputDTO(ticker=Ticker.ETH_USD))

    assert error.value.ticker is Ticker.ETH_USD
