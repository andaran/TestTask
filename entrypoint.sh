#!/bin/sh
set -e

alembic upgrade head
exec uvicorn services.price_service.entrypoints.rest:app --host 0.0.0.0 --port 8000
