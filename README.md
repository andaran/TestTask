# Price Service

Сервис раз в минуту забирает с [Deribit](https://docs.deribit.com/) index price `btc_usd` и `eth_usd`, сохраняет их в PostgreSQL и отдаёт сохранённые данные через REST API на FastAPI.

**Стек:** Python 3.14, FastAPI, SQLAlchemy 2 (async, asyncpg), Alembic, Celery + Redis, httpx, Pydantic, PostgreSQL 18, Docker Compose, uv, pytest, ruff, mypy (strict).

## Содержание

- [Быстрый старт](#быстрый-старт)
- [API](#api)
- [Переменные окружения](#переменные-окружения)
- [Локальная разработка](#локальная-разработка)
- [Структура проекта](#структура-проекта)
- [Design decisions](#design-decisions)

## Быстрый старт

Нужен только Docker с Compose v2.

```bash
git clone https://github.com/andaran/TestTask price-service
cd price-service
cp .env.example .env
docker compose up -d --build
```

Поднимаются четыре контейнера:

| Сервис | Назначение |
|---|---|
| `db` | PostgreSQL, данные в volume `postgres_data` |
| `redis` | брокер Celery |
| `app` | применяет миграции (`alembic upgrade head`) и запускает API на порту `APP_PORT` (по умолчанию 8000) |
| `worker` | Celery worker со встроенным beat: опрос Deribit каждые `FETCH_INTERVAL` секунд |

`worker` стартует после того, как `app` прошёл healthcheck. К этому моменту таблицы уже созданы.

Проверка:

```bash
docker compose ps
curl "http://localhost:8000/prices/latest?ticker=btc_usd"
```

Первая запись появляется сразу после старта воркера, следующие — раз в минуту. Swagger UI: http://localhost:8000/docs.

Логи и остановка:

```bash
docker compose logs -f worker
docker compose down       # остановить
docker compose down -v    # остановить и удалить данные БД
```

## API

Все методы — `GET`, у каждого обязательный query-параметр `ticker` (`btc_usd` | `eth_usd`).

| Метод | Параметры | Ответ |
|---|---|---|
| `/prices` | `ticker` | все сохранённые цены по тикеру |
| `/prices/latest` | `ticker` | последняя цена; `404`, если данных нет |
| `/prices/by-date` | `ticker`, `date_from`, `date_to` | цены за период |

- `date_from`, `date_to` — UNIX timestamp в секундах, обе границы включительно и необязательны.
- Записи отсортированы по `timestamp` по возрастанию.
- `price` отдаётся строкой без хвостовых нулей, чтобы не терять точность.

Коды ошибок:
- `422` — нет `ticker`, неизвестный тикер, отрицательная дата или `date_from > date_to`;
- `404` — нет данных для `/prices/latest`.

Примеры:

```bash
curl "http://localhost:8000/prices?ticker=btc_usd"
```
```json
{"prices": [
  {"ticker": "btc_usd", "price": "82123.45", "timestamp": 1792141721},
  {"ticker": "btc_usd", "price": "82131.04", "timestamp": 1792141781}
]}
```

```bash
curl "http://localhost:8000/prices/latest?ticker=eth_usd"
```
```json
{"ticker": "eth_usd", "price": "2452.06", "timestamp": 1792141781}
```

```bash
curl "http://localhost:8000/prices/by-date?ticker=btc_usd&date_from=1792141700&date_to=1792141750"
```
```json
{"prices": [{"ticker": "btc_usd", "price": "82123.45", "timestamp": 1792141721}]}
```

```bash
curl "http://localhost:8000/prices/latest?ticker=xrp_usd"   # 422
```

## Переменные окружения

Читаются из `.env` (шаблон — `.env.example`).

| Переменная | По умолчанию | Описание |
|---|---|---|
| `DB_USER` | `postgres` | пользователь PostgreSQL |
| `DB_PASSWORD` | `postgres` | пароль PostgreSQL |
| `DB_NAME` | `prices` | имя базы |
| `DB_HOST` | `localhost` | хост БД; в Compose переопределяется на `db` |
| `DB_PORT` | `5432` | порт БД; в Compose переопределяется на `5432` |
| `REDIS_URL` | `redis://localhost:6379/0` | брокер Celery; в Compose переопределяется на `redis://redis:6379/0` |
| `DERIBIT_URL` | `https://www.deribit.com/api/v2` | базовый URL Deribit API |
| `DERIBIT_TIMEOUT` | `10` | таймаут запроса к Deribit, секунды |
| `FETCH_INTERVAL` | `60` | интервал опроса биржи, секунды |
| `APP_PORT` | `8000` | порт API на хосте (только для Compose) |

Хосты и порты для Docker заданы прямо в `docker-compose.yml`, поэтому один и тот же `.env` подходит и для Compose, и для локального запуска.

## Локальная разработка

Нужен [uv](https://docs.astral.sh/uv/). Python 3.14 uv поставит сам.

```bash
uv sync
cp .env.example .env
```

Тесты и линтеры (БД и сеть не нужны):

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy .
```

Запуск без Docker для приложения (Postgres и Redis можно взять из Compose):

```bash
docker compose up -d db redis   # в .env: DB_PORT/REDIS_URL на проброшенные порты, если нужно
uv run alembic upgrade head
uv run uvicorn services.price_service.entrypoints.rest:app --reload
uv run celery -A services.price_service.entrypoints.worker worker --beat --loglevel=INFO
```

> По умолчанию `db` и `redis` не пробрасывают порты на хост. Для локального запуска добавьте `ports` в `docker-compose.override.yml` или используйте свои экземпляры.

Новая миграция после изменения ORM-моделей:

```bash
uv run alembic revision --autogenerate -m "describe change"
```

## Структура проекта

```
.
├── shared/infrastructure/             # инфраструктура, общая для будущих сервисов
│   ├── config/settings.py             # Settings (pydantic-settings), единый конфиг
│   ├── database/                      # Base, create_engine, create_session_factory
│   └── rest/exception_handler.py      # DomainError -> HTTP-ответ через переданный маппер
├── services/price_service/
│   ├── core/                          # домен: ни от чего не зависит
│   │   ├── entities.py                # Ticker и Price
│   │   └── exceptions.py              # DomainError и наследники
│   ├── application/                   # сценарии: зависят только от core
│   │   ├── ports/                     # Protocol: PriceRepository, PriceProvider, Clock, UnitOfWork
│   │   ├── use_cases/                 # FetchAndSavePrices, GetPrices, GetLatestPrice, GetPricesByDate
│   │   └── dtos.py
│   ├── infrastructure/                # реализации портов и адаптеры
│   │   ├── db/                        # ORM-модель, SQLAlchemy-репозиторий, Unit of Work
│   │   ├── deribit/                   # HTTP-клиент Deribit
│   │   ├── api/                       # FastAPI: контроллеры, схемы, DI, маппер ошибок
│   │   ├── tasks/fetch_prices.py      # Celery-задача
│   │   └── clock.py
│   └── entrypoints/                   # сборка и запуск
│       ├── rest.py                    # FastAPI-приложение
│       └── worker.py                  # Celery-приложение и расписание beat
├── migrations/                        # Alembic
├── tests/price_service/
│   ├── core/                          # инварианты сущностей
│   ├── application/                   # use case'ы на in-memory моках портов
│   └── infrastructure/                # Deribit-клиент, API, Celery-задача
├── Dockerfile
├── docker-compose.yml
└── entrypoint.sh                      # миграции + uvicorn
```

Направление зависимостей: `entrypoints → infrastructure → application → core`. `shared` не импортирует ничего из `services`.

## Design decisions

**Чистая архитектура**
- Домен и сценарии не знают про FastAPI, SQLAlchemy, Celery и httpx.
- Use case'ы тестируются без БД и сети.
- Источник цен, хранилище или транспорт меняются заменой адаптера в `infrastructure`.
- `shared/` — задел под следующие сервисы: в нём только то, что не зависит от предметной области.

**Unit of Work**
- Use case получает `Callable[[], UnitOfWork]`, а не готовую сессию, поэтому каждый вызов работает в своей транзакции.
- Коммит всегда явный. Выход из контекста с исключением откатывает транзакцию.

**Денежные суммы хранятся в `Decimal`**
- Ответ Deribit разбирается из JSON сразу в `Decimal`, без промежуточного `float`.
- В БД цена хранится как `Numeric(18, 8)`.
- В API цена отдаётся строкой без хвостовых нулей: `"82123.45"`, а не `82123.45000000` и не `float`.

**Сбой одного тикера не блокирует остальные**
- Тикеры опрашиваются параллельно через `asyncio.TaskGroup`.
- Ожидаемые ошибки (сеть, HTTP, невалидный ответ, отрицательная цена) обрабатываются внутри задачи по тикеру.
- Неожиданные ошибки отменяют группу и всплывают наружу.
- Celery-задача повторяет только упавшие тикеры, с backoff 5 → 10 → 20 секунд, не больше 3 раз. Повтор укладывается в минутный интервал, а успешные цены не записываются дважды.

**`expires` у периодической задачи равен интервалу.** Если воркер лежал, после подъёма он не выполнит пачку устаревших задач.

**`asyncio.run` в Celery и `NullPool`**
- Стек асинхронный, а Celery-задача синхронная: каждый запуск выполняет use case через `asyncio.run`, то есть в новом event loop.
- Соединения asyncpg привязаны к циклу, в котором открыты, поэтому воркер работает без пула соединений (`NullPool`): engine создаётся и закрывается на каждый запуск.
- API держит обычный пул, созданный в lifespan.

**Четыре контейнера вместо двух.**
- Для Celery используется Redis в качестве брокера.
- API и воркер вынесены в отдельные контейнеры из одного образа. Их можно независимо перезапускать и масштабировать, а падение воркера не роняет API.

**Миграции применяет только `app` при старте** `worker` ждёт, пока `app` станет healthy, поэтому к первому опросу таблица уже существует. `alembic upgrade head` идемпотентен, и перезапуск контейнера безопасен.

**Семантика API**
- Пустой результат `/prices` и `/prices/by-date` — это `200` с пустым списком.
- `/prices/latest` без данных — `404`.
- Проверка `date_from > date_to` живёт в use case, а не в схеме запроса. Это правило сценария, и оно покрыто юнит-тестом.

**Тесты**
- Use case'ы — на in-memory реализациях портов.
- API — через `httpx.ASGITransport` на настоящем FastAPI-приложении с подменённым `UnitOfWork`.
- Deribit-клиент — через `httpx.MockTransport`.
- Celery-задача — в eager-режиме с подменённым запуском use case'а.
- Внешние сервисы для тестов не нужны.
