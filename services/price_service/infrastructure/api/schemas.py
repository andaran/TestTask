from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer

from services.price_service.core import Ticker

NormalizedDecimal = Annotated[
    Decimal,
    PlainSerializer(
        lambda value: format(value.normalize(), "f"),
        return_type=str,
        when_used="json",
    ),
]


class TickerQuery(BaseModel):
    ticker: Ticker


class DateRangeQuery(TickerQuery):
    date_from: int | None = Field(default=None, ge=0)
    date_to: int | None = Field(default=None, ge=0)


class PriceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticker: Ticker
    price: NormalizedDecimal
    timestamp: int


class PricesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prices: list[PriceResponse]


class ErrorResponse(BaseModel):
    detail: str
