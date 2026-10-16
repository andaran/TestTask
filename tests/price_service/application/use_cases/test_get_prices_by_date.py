from typing import TYPE_CHECKING

import pytest

from services.price_service.application.dtos import GetPricesByDateInputDTO
from services.price_service.application.use_cases import GetPricesByDateUseCase
from services.price_service.core import InvalidDateRangeError, Ticker

if TYPE_CHECKING:
    from tests.price_service.application.mocks import MockUnitOfWork


@pytest.fixture
def use_case(uow: MockUnitOfWork) -> GetPricesByDateUseCase:
    return GetPricesByDateUseCase(lambda: uow)


@pytest.mark.parametrize(
    ("date_from", "date_to", "expected_timestamps"),
    [
        (100, 220, (100, 160, 220)),
        (101, 219, (160,)),
        (160, 160, (160,)),
        (160, None, (160, 220)),
        (None, 160, (100, 160)),
        (None, None, (100, 160, 220)),
        (300, 400, ()),
    ],
)
async def test_filters_prices_by_inclusive_range(
    use_case: GetPricesByDateUseCase,
    date_from: int | None,
    date_to: int | None,
    expected_timestamps: tuple[int, ...],
) -> None:
    result = await use_case(
        GetPricesByDateInputDTO(
            ticker=Ticker.BTC_USD, date_from=date_from, date_to=date_to
        )
    )

    assert tuple(price.timestamp for price in result.prices) == expected_timestamps
    assert all(price.ticker is Ticker.BTC_USD for price in result.prices)


async def test_raises_when_date_from_is_greater_than_date_to(
    use_case: GetPricesByDateUseCase,
) -> None:
    with pytest.raises(InvalidDateRangeError):
        await use_case(
            GetPricesByDateInputDTO(ticker=Ticker.BTC_USD, date_from=200, date_to=100)
        )
