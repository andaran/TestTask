from typing import TYPE_CHECKING, Self

from .price_repository import InMemoryPriceRepository

if TYPE_CHECKING:
    from types import TracebackType


class MockUnitOfWork:
    committed: bool
    rolled_back: bool
    __prices: InMemoryPriceRepository

    def __init__(self, prices: InMemoryPriceRepository | None = None) -> None:
        self.committed = False
        self.rolled_back = False
        self.__prices = prices or InMemoryPriceRepository()

    @property
    def prices(self) -> InMemoryPriceRepository:
        return self.__prices

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True
