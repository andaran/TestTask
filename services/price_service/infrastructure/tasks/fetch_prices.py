import asyncio
from functools import partial
from typing import TYPE_CHECKING

import httpx
from celery import shared_task

from services.price_service.application.dtos import FetchAndSavePricesInputDTO
from services.price_service.application.use_cases import FetchAndSavePricesUseCase
from services.price_service.core import Ticker
from services.price_service.infrastructure.clock import SystemClock
from services.price_service.infrastructure.db import SQLAlchemyUnitOfWork
from services.price_service.infrastructure.deribit import DeribitPriceProvider
from shared.infrastructure.config import Settings, get_settings
from shared.infrastructure.database import create_engine, create_session_factory

if TYPE_CHECKING:
    from celery import Task

    from services.price_service.application.dtos import FetchAndSavePricesOutputDTO

FETCH_PRICES_TASK = "price_service.fetch_prices"
MAX_RETRIES = 3
RETRY_BASE_DELAY = 5


async def run_fetch_and_save(
    settings: Settings, input_dto: FetchAndSavePricesInputDTO
) -> FetchAndSavePricesOutputDTO:
    engine = create_engine(settings.db_url, pooled=False)
    try:
        async with httpx.AsyncClient(
            base_url=settings.deribit_url, timeout=settings.deribit_timeout
        ) as client:
            use_case = FetchAndSavePricesUseCase(
                uow_factory=partial(
                    SQLAlchemyUnitOfWork, create_session_factory(engine)
                ),
                price_provider=DeribitPriceProvider(client),
                clock=SystemClock(),
            )
            return await use_case(input_dto)
    finally:
        await engine.dispose()


@shared_task(bind=True, name=FETCH_PRICES_TASK, max_retries=MAX_RETRIES)
def fetch_prices(self: Task[..., None], tickers: list[str] | None = None) -> None:
    input_dto = (
        FetchAndSavePricesInputDTO(tickers=tuple(map(Ticker, tickers)))
        if tickers
        else FetchAndSavePricesInputDTO()
    )
    result = asyncio.run(run_fetch_and_save(get_settings(), input_dto))

    if result.failed:
        raise self.retry(
            kwargs={"tickers": [ticker.value for ticker in result.failed]},
            countdown=RETRY_BASE_DELAY * 2**self.request.retries,
        )
