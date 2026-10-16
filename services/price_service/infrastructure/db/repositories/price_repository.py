from typing import TYPE_CHECKING

from sqlalchemy import select

from services.price_service.core import Price
from services.price_service.infrastructure.db.models import PriceModel

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.ext.asyncio import AsyncSession

    from services.price_service.core import Ticker


class SQLAlchemyPriceRepository:
    __session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self.__session = session

    async def add(self, price: Price) -> None:
        self.__session.add(
            PriceModel(
                ticker=price.ticker, price=price.price, timestamp=price.timestamp
            )
        )

    async def get_all(self, ticker: Ticker) -> Sequence[Price]:
        return await self.get_by_date_range(ticker)

    async def get_latest(self, ticker: Ticker) -> Price | None:
        query = (
            select(PriceModel)
            .where(PriceModel.ticker == ticker)
            .order_by(PriceModel.timestamp.desc(), PriceModel.id.desc())
            .limit(1)
        )
        model = await self.__session.scalar(query)
        return self.__to_entity(model) if model else None

    async def get_by_date_range(
        self,
        ticker: Ticker,
        date_from: int | None = None,
        date_to: int | None = None,
    ) -> Sequence[Price]:
        query = select(PriceModel).where(PriceModel.ticker == ticker)
        if date_from is not None:
            query = query.where(PriceModel.timestamp >= date_from)
        if date_to is not None:
            query = query.where(PriceModel.timestamp <= date_to)

        models = await self.__session.scalars(
            query.order_by(PriceModel.timestamp, PriceModel.id)
        )
        return tuple(self.__to_entity(model) for model in models)

    @staticmethod
    def __to_entity(model: PriceModel) -> Price:
        return Price(ticker=model.ticker, price=model.price, timestamp=model.timestamp)
