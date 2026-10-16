from decimal import Decimal

import pytest

from services.price_service.core import NegativePriceError, Price, Ticker


@pytest.mark.parametrize(
    "value", [Decimal("0"), Decimal("0.00000001"), Decimal("65000")]
)
def test_accepts_non_negative_price(value: Decimal) -> None:
    price = Price(ticker=Ticker.BTC_USD, price=value, timestamp=1)

    assert price.price == value


def test_rejects_negative_price() -> None:
    with pytest.raises(NegativePriceError) as error:
        Price(ticker=Ticker.BTC_USD, price=Decimal("-0.01"), timestamp=1)

    assert error.value.ticker is Ticker.BTC_USD
    assert error.value.price == Decimal("-0.01")
