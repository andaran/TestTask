from fastapi import HTTPException, status

from services.price_service.core import (
    DomainError,
    InvalidDateRangeError,
    PriceNotFoundError,
)


def map_error(error: DomainError) -> HTTPException:
    match error:
        case PriceNotFoundError():
            return HTTPException(status.HTTP_404_NOT_FOUND, str(error))
        case InvalidDateRangeError():
            return HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(error))
        case _:
            return HTTPException(status.HTTP_400_BAD_REQUEST, str(error))
