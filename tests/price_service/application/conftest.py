import pytest

from tests.price_service.application.mocks import (
    InMemoryPriceRepository,
    MockUnitOfWork,
)
from tests.price_service.application.samples import BTC_PRICES, ETH_PRICES


@pytest.fixture
def repository() -> InMemoryPriceRepository:
    return InMemoryPriceRepository(reversed((*BTC_PRICES, *ETH_PRICES)))


@pytest.fixture
def uow(repository: InMemoryPriceRepository) -> MockUnitOfWork:
    return MockUnitOfWork(repository)
