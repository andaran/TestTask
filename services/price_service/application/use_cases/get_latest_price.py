from typing import TYPE_CHECKING

from services.price_service.application.dtos import GetLatestPriceInputDTO, PriceDTO
from services.price_service.core import PriceNotFoundError

if TYPE_CHECKING:
    from collections.abc import Callable

    from services.price_service.application.ports import UnitOfWork


class GetLatestPriceUseCase:
    __uow_factory: Callable[[], UnitOfWork]

    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self.__uow_factory = uow_factory

    async def __call__(self, input_dto: GetLatestPriceInputDTO) -> PriceDTO:
        async with self.__uow_factory() as uow:
            price = await uow.prices.get_latest(input_dto.ticker)

        if price is None:
            raise PriceNotFoundError(input_dto.ticker)

        return PriceDTO.from_entity(price)
