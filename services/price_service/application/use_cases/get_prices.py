from typing import TYPE_CHECKING

from services.price_service.application.dtos import (
    GetPricesInputDTO,
    PriceDTO,
    PricesDTO,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from services.price_service.application.ports import UnitOfWork


class GetPricesUseCase:
    __uow_factory: Callable[[], UnitOfWork]

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self.__uow_factory = uow_factory

    async def __call__(self, input_dto: GetPricesInputDTO) -> PricesDTO:
        async with self.__uow_factory() as uow:
            prices = await uow.prices.get_all(input_dto.ticker)

        return PricesDTO(prices=tuple(PriceDTO.from_entity(price) for price in prices))
