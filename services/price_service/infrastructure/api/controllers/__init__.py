from . import get_latest_price, get_prices, get_prices_by_date, health

price_routers = (get_prices.router, get_latest_price.router, get_prices_by_date.router)
health_router = health.router

__all__ = ["health_router", "price_routers"]
