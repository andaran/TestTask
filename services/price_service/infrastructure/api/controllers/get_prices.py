from typing import Annotated

from fastapi import APIRouter, Depends, Query

from services.price_service.application.dtos import GetPricesInputDTO
from services.price_service.application.use_cases import GetPricesUseCase

from ..dependencies import get_prices_use_case
from ..schemas import PricesResponse, TickerQuery

router = APIRouter()


@router.get("/prices")
async def get_prices(
    query: Annotated[TickerQuery, Query()],
    use_case: Annotated[GetPricesUseCase, Depends(get_prices_use_case)],
) -> PricesResponse:
    result = await use_case(GetPricesInputDTO(ticker=query.ticker))
    return PricesResponse.model_validate(result)
