from decimal import Decimal

from sqlalchemy import BigInteger, CheckConstraint, Enum, Index, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from services.price_service.core import Ticker
from shared.infrastructure.database.base import Base


class PriceModel(Base):
    __tablename__ = "prices"
    __table_args__ = (
        CheckConstraint("price >= 0", name="price_non_negative"),
        Index(None, "ticker", "timestamp"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    ticker: Mapped[Ticker] = mapped_column(
        Enum(
            Ticker,
            name="ticker",
            values_callable=lambda enum: [member.value for member in enum],
        ),
    )
    price: Mapped[Decimal] = mapped_column(Numeric(18, 8))
    timestamp: Mapped[int] = mapped_column(BigInteger)
