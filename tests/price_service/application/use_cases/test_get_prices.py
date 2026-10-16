from services.price_service.application.dtos import GetPricesInputDTO, PriceDTO
from services.price_service.application.use_cases import GetPricesUseCase
from services.price_service.core import Ticker
from tests.price_service.application.mocks import MockUnitOfWork
from tests.price_service.application.samples import BTC_PRICES


async def test_returns_ticker_prices_ordered_by_timestamp(uow: MockUnitOfWork) -> None:
    use_case = GetPricesUseCase(lambda: uow)

    result = await use_case(GetPricesInputDTO(ticker=Ticker.BTC_USD))

    assert result.prices == tuple(PriceDTO.from_entity(price) for price in BTC_PRICES)


async def test_returns_empty_result_when_no_prices() -> None:
    use_case = GetPricesUseCase(MockUnitOfWork)

    result = await use_case(GetPricesInputDTO(ticker=Ticker.BTC_USD))

    assert result.prices == ()
