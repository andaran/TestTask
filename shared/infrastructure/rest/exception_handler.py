from typing import TYPE_CHECKING

from fastapi.responses import JSONResponse

if TYPE_CHECKING:
    from collections.abc import Callable

    from fastapi import FastAPI, Request
    from starlette.exceptions import HTTPException


def setup_exception_handler[DomainErrorT: Exception](
    app: FastAPI,
    *,
    domain_error_type: type[DomainErrorT],
    error_mapper: Callable[[DomainErrorT], HTTPException],
) -> None:
    @app.exception_handler(domain_error_type)
    async def domain_error_handler(_: Request, exc: DomainErrorT) -> JSONResponse:
        http_error = error_mapper(exc)
        return JSONResponse(
            status_code=http_error.status_code,
            content={"detail": http_error.detail},
        )
