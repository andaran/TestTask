from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from services.price_service.application.dtos import GetLatestPriceInputDTO
from services.price_service.application.use_cases import GetLatestPriceUseCase

from ..dependencies import get_latest_price_use_case
from ..schemas import ErrorResponse, PriceResponse, TickerQuery

router = APIRouter()


@router.get(
    "/prices/latest",
    responses={status.HTTP_404_NOT_FOUND: {"model": ErrorResponse}},
)
async def get_latest_price(
    query: Annotated[TickerQuery, Query()],
    use_case: Annotated[GetLatestPriceUseCase, Depends(get_latest_price_use_case)],
) -> PriceResponse:
    result = await use_case(GetLatestPriceInputDTO(ticker=query.ticker))
    return PriceResponse.model_validate(result)
