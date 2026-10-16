from typing import TYPE_CHECKING

import pytest
from celery.exceptions import MaxRetriesExceededError

from services.price_service.application.dtos import FetchAndSavePricesOutputDTO
from services.price_service.core import Ticker
from services.price_service.entrypoints.worker import app
from services.price_service.infrastructure.tasks import (
    fetch_prices as fetch_prices_module,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine, Sequence
    from typing import Any

    from services.price_service.application.dtos import FetchAndSavePricesInputDTO

    RunFetchAndSave = Callable[..., Coroutine[Any, Any, FetchAndSavePricesOutputDTO]]


@pytest.fixture(autouse=True)
def celery_app() -> None:
    app.set_current()


def fake_runner(
    failures: Sequence[Sequence[Ticker]], calls: list[tuple[Ticker, ...]]
) -> RunFetchAndSave:
    async def run(
        _: object, input_dto: FetchAndSavePricesInputDTO
    ) -> FetchAndSavePricesOutputDTO:
        attempt = len(calls)
        calls.append(tuple(input_dto.tickers))
        return FetchAndSavePricesOutputDTO(saved=(), failed=tuple(failures[attempt]))

    return run


def test_fetches_all_tickers_once_when_successful(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[Ticker, ...]] = []
    monkeypatch.setattr(
        fetch_prices_module, "run_fetch_and_save", fake_runner([[]], calls)
    )

    fetch_prices_module.fetch_prices.apply().get()

    assert calls == [(Ticker.BTC_USD, Ticker.ETH_USD)]


def test_retries_only_failed_tickers(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[Ticker, ...]] = []
    monkeypatch.setattr(
        fetch_prices_module,
        "run_fetch_and_save",
        fake_runner([[Ticker.ETH_USD], []], calls),
    )

    fetch_prices_module.fetch_prices.apply().get()

    assert calls == [(Ticker.BTC_USD, Ticker.ETH_USD), (Ticker.ETH_USD,)]


def test_gives_up_after_max_retries(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[Ticker, ...]] = []
    failures = [[Ticker.ETH_USD]] * (fetch_prices_module.MAX_RETRIES + 1)
    monkeypatch.setattr(
        fetch_prices_module, "run_fetch_and_save", fake_runner(failures, calls)
    )

    with pytest.raises(MaxRetriesExceededError):
        fetch_prices_module.fetch_prices.apply().get()

    assert len(calls) == fetch_prices_module.MAX_RETRIES + 1
