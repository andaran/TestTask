from decimal import Decimal

from services.price_service.core import Price, Ticker

BTC_PRICES = (
    Price(ticker=Ticker.BTC_USD, price=Decimal("60000.5"), timestamp=100),
    Price(ticker=Ticker.BTC_USD, price=Decimal("60100"), timestamp=160),
    Price(ticker=Ticker.BTC_USD, price=Decimal("60200.25"), timestamp=220),
)
ETH_PRICES = (Price(ticker=Ticker.ETH_USD, price=Decimal("3000"), timestamp=130),)
