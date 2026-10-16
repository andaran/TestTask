from typing import TYPE_CHECKING, Self

from .repositories import SQLAlchemyPriceRepository

if TYPE_CHECKING:
    from types import TracebackType

    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class SQLAlchemyUnitOfWork:
    __session_factory: async_sessionmaker[AsyncSession]
    __session: AsyncSession | None
    __prices: SQLAlchemyPriceRepository | None

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.__session_factory = session_factory
        self.__session = None
        self.__prices = None

    @property
    def prices(self) -> SQLAlchemyPriceRepository:
        if self.__prices is None:
            raise RuntimeError("Unit of work is not started")
        return self.__prices

    async def __aenter__(self) -> Self:
        self.__session = self.__session_factory()
        self.__prices = SQLAlchemyPriceRepository(self.__session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        try:
            if exc_type is not None:
                await self.rollback()
        finally:
            await self.__active_session().close()
            self.__session = None
            self.__prices = None

    async def commit(self) -> None:
        await self.__active_session().commit()

    async def rollback(self) -> None:
        await self.__active_session().rollback()

    def __active_session(self) -> AsyncSession:
        if self.__session is None:
            raise RuntimeError("Unit of work is not started")
        return self.__session
