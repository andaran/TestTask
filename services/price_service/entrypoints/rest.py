from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import FastAPI

from services.price_service.core import DomainError
from services.price_service.infrastructure.api.controllers import (
    health_router,
    price_routers,
)
from services.price_service.infrastructure.api.error_mapper import map_error
from shared.infrastructure.config import get_settings
from shared.infrastructure.database import create_engine, create_session_factory
from shared.infrastructure.rest import setup_exception_handler

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    engine = create_engine(get_settings().db_url)
    app.state.session_factory = create_session_factory(engine)
    yield
    await engine.dispose()


app = FastAPI(title="Price Service", lifespan=lifespan)

for router in price_routers:
    app.include_router(router, tags=["Prices"])
app.include_router(health_router)

setup_exception_handler(app, domain_error_type=DomainError, error_mapper=map_error)
