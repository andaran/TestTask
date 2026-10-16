from decimal import Decimal

from pydantic import BaseModel


class IndexPriceResult(BaseModel):
    index_price: Decimal


class IndexPriceResponse(BaseModel):
    result: IndexPriceResult
