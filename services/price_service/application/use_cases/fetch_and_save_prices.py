import asyncio
import logging
from typing import TYPE_CHECKING

from services.price_service.application.dtos import (
    FetchAndSavePricesInputDTO,
    FetchAndSavePricesOutputDTO,
    PriceDTO,
)
from services.price_service.core import NegativePriceError, Price, PriceProviderError

if TYPE_CHECKING:
    from collections.abc import Callable

    from services.price_service.application.ports import (
        Clock,
        PriceProvider,
        UnitOfWork,
    )
    from services.price_service.core import Ticker

logger = logging.getLogger(__name__)


class FetchAndSavePricesUseCase:
    __uow_factory: Callable[[], UnitOfWork]
    __price_provider: PriceProvider
    __clock: Clock

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        price_provider: PriceProvider,
        clock: Clock,
    ) -> None:
        self.__uow_factory = uow_factory
        self.__price_provider = price_provider
        self.__clock = clock

    async def __call__(
        self, input_dto: FetchAndSavePricesInputDTO
    ) -> FetchAndSavePricesOutputDTO:
        timestamp = self.__clock.now()

        async with asyncio.TaskGroup() as task_group:
            tasks = {
                ticker: task_group.create_task(self.__fetch_price(ticker, timestamp))
                for ticker in input_dto.tickers
            }

        prices = [price for task in tasks.values() if (price := task.result())]
        failed = [ticker for ticker, task in tasks.items() if task.result() is None]

        if prices:
            async with self.__uow_factory() as uow:
                for price in prices:
                    await uow.prices.add(price)
                await uow.commit()

        return FetchAndSavePricesOutputDTO(
            saved=tuple(PriceDTO.from_entity(price) for price in prices),
            failed=tuple(failed),
        )

    async def __fetch_price(self, ticker: Ticker, timestamp: int) -> Price | None:
        try:
            value = await self.__price_provider.get_index_price(ticker)
            return Price(ticker=ticker, price=value, timestamp=timestamp)
        except (PriceProviderError, NegativePriceError) as error:
            logger.warning("Skipping %s: %s", ticker, error)
            return None
