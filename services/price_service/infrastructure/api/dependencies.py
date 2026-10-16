from collections.abc import Callable
from functools import partial
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Request

from services.price_service.application.use_cases import (
    GetLatestPriceUseCase,
    GetPricesByDateUseCase,
    GetPricesUseCase,
)
from services.price_service.infrastructure.db import SQLAlchemyUnitOfWork

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


def get_uow_factory(request: Request) -> Callable[[], SQLAlchemyUnitOfWork]:
    session_factory: async_sessionmaker[AsyncSession] = (
        request.app.state.session_factory
    )
    return partial(SQLAlchemyUnitOfWork, session_factory)


UoWFactory = Annotated[Callable[[], SQLAlchemyUnitOfWork], Depends(get_uow_factory)]


def get_prices_use_case(uow_factory: UoWFactory) -> GetPricesUseCase:
    return GetPricesUseCase(uow_factory)


def get_latest_price_use_case(uow_factory: UoWFactory) -> GetLatestPriceUseCase:
    return GetLatestPriceUseCase(uow_factory)


def get_prices_by_date_use_case(uow_factory: UoWFactory) -> GetPricesByDateUseCase:
    return GetPricesByDateUseCase(uow_factory)
