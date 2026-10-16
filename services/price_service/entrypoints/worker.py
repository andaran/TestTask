from celery import Celery

from services.price_service.infrastructure.tasks.fetch_prices import FETCH_PRICES_TASK
from shared.infrastructure.config import get_settings

settings = get_settings()

app = Celery(
    "price_service",
    broker=settings.redis_url,
    include=["services.price_service.infrastructure.tasks.fetch_prices"],
)
app.conf.update(
    task_ignore_result=True,
    timezone="UTC",
    broker_connection_retry_on_startup=True,
    beat_schedule={
        "fetch-prices": {
            "task": FETCH_PRICES_TASK,
            "schedule": settings.fetch_interval,
            "options": {"expires": settings.fetch_interval},
        },
    },
)
