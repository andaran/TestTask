from typing import TYPE_CHECKING

from services.price_service.application.dtos import (
    GetPricesByDateInputDTO,
    PriceDTO,
    PricesDTO,
)
from services.price_service.core import InvalidDateRangeError

if TYPE_CHECKING:
    from collections.abc import Callable

    from services.price_service.application.ports import UnitOfWork


class GetPricesByDateUseCase:
    __uow_factory: Callable[[], UnitOfWork]

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self.__uow_factory = uow_factory

    async def __call__(self, input_dto: GetPricesByDateInputDTO) -> PricesDTO:
        date_from, date_to = input_dto.date_from, input_dto.date_to
        if date_from is not None and date_to is not None and date_from > date_to:
            raise InvalidDateRangeError(date_from, date_to)

        async with self.__uow_factory() as uow:
            prices = await uow.prices.get_by_date_range(
                ticker=input_dto.ticker,
                date_from=date_from,
                date_to=date_to,
            )

        return PricesDTO(prices=tuple(PriceDTO.from_entity(price) for price in prices))
