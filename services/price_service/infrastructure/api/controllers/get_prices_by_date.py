from typing import Annotated

from fastapi import APIRouter, Depends, Query

from services.price_service.application.dtos import GetPricesByDateInputDTO
from services.price_service.application.use_cases import GetPricesByDateUseCase

from ..dependencies import get_prices_by_date_use_case
from ..schemas import DateRangeQuery, PricesResponse

router = APIRouter()


@router.get("/prices/by-date")
async def get_prices_by_date(
    query: Annotated[DateRangeQuery, Query()],
    use_case: Annotated[GetPricesByDateUseCase, Depends(get_prices_by_date_use_case)],
) -> PricesResponse:
    result = await use_case(
        GetPricesByDateInputDTO(
            ticker=query.ticker,
            date_from=query.date_from,
            date_to=query.date_to,
        )
    )
    return PricesResponse.model_validate(result)
