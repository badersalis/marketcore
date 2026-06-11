# MarketCore

A production-ready, reusable e-commerce backend platform built with **FastAPI**, following **Domain-Driven Design (DDD)** principles, and fully containerised with **Docker**.

Clone it. Adapt it. Ship it.

---

## Architecture

```
                    ┌──────────────────────────────────────────┐
                    │           API Gateway  :8000              │
                    │  JWT validation · Rate limiting · Proxy   │
                    └──┬──────────┬──────────┬──────────┬───────┘
                       │          │          │          │
            ┌──────────▼─┐  ┌─────▼──┐  ┌───▼───┐  ┌──▼────────┐
            │auth-service│  │product │  │ order │  │ payment   │
            │   :8001    │  │ :8002  │  │ :8003 │  │  :8004    │
            └────────────┘  └────────┘  └───────┘  └──────┬────┘
                                                           │
                    ┌──────────────────────────────────────▼────┐
                    │         notification-service  :8005        │
                    └────────────────────────────────────────────┘

        All services  ──async events──►  RabbitMQ  :5672  (management :15672)
        All services  ──SQL──────────►  PostgreSQL :5432  (per-service DB)
        auth + gw     ──cache─────────►  Redis      :6379
```

---

## Services

| Service | Port | Responsibility |
|---|---|---|
| `api-gateway` | 8000 | Single entry point, JWT validation, rate limiting, reverse proxy |
| `auth-service` | 8001 | Registration, login, JWT access + refresh tokens |
| `product-service` | 8002 | Product catalogue, categories, inventory |
| `order-service` | 8003 | Cart management, order lifecycle (pending → delivered) |
| `payment-service` | 8004 | Payment intents, Stripe webhook stub |
| `notification-service` | 8005 | Email + push notifications from domain events |

---

## Quick Start

```bash
# 1. Copy and configure env
cp .env.example .env
# Edit .env — at minimum set a strong SECRET_KEY

# 2. Build and boot everything
docker-compose up --build

# 3. Verify the stack
curl http://localhost:8000/health
```

Swagger UI is available at each service:
- http://localhost:8001/docs  (auth)
- http://localhost:8002/docs  (products)
- http://localhost:8003/docs  (orders)
- http://localhost:8004/docs  (payments)
- RabbitMQ management: http://localhost:15672  (rabbitmq / rabbitmq)

---

## Running Migrations

Each service uses Alembic with async SQLAlchemy. Run inside the container:

```bash
# Run all pending migrations
docker-compose exec auth-service        alembic upgrade head
docker-compose exec product-service     alembic upgrade head
docker-compose exec order-service       alembic upgrade head
docker-compose exec payment-service     alembic upgrade head
docker-compose exec notification-service alembic upgrade head

# Generate a new migration after editing a domain model
docker-compose exec auth-service alembic revision --autogenerate -m "add email_verified_at"
```

---

## Environment Variables

| Variable | Services | Description |
|---|---|---|
| `SECRET_KEY` | all | JWT signing secret (≥ 32 chars) |
| `STRIPE_SECRET_KEY` | payment | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | payment | Stripe webhook signing secret |
| `SMTP_HOST` | notification | SMTP server hostname |
| `SMTP_PORT` | notification | SMTP port (587 for STARTTLS) |
| `SMTP_USERNAME` | notification | SMTP username / API key |
| `SMTP_PASSWORD` | notification | SMTP password |
| `FROM_EMAIL` | notification | Sender address |

Infrastructure variables (DATABASE_URL, RABBITMQ_URL, REDIS_URL) are wired automatically in docker-compose.

---

## Adding a New Microservice

1. **Create the directory** with the DDD structure:
   ```
   my-service/
   ├── domain/{entities,value_objects,repositories,events,exceptions}/
   ├── application/{use_cases,dtos,services}/
   ├── infrastructure/{repositories,messaging,persistence/migrations}/
   └── presentation/routers/
   ```
2. **Copy** `requirements.txt` and `Dockerfile` from an existing service and adjust port.
3. **Add `main.py`** with lifespan handlers (DB init + RabbitMQ connect).
4. **Add `alembic.ini`** pointing to `infrastructure/persistence/migrations`.
5. **Add the database** to `scripts/init-db.sql`.
6. **Add the service** to `docker-compose.yml` with correct port and `depends_on`.
7. **Add a route** in `api-gateway/presentation/routers/proxy_router.py`.

---

## Project Structure

```
marketcore/
├── api-gateway/          # Reverse proxy + JWT validation + rate limiting
├── auth-service/         # Auth domain  (fully functional)
├── product-service/      # Product catalogue (fully functional)
├── order-service/        # Order domain (scaffolded with stubs)
├── payment-service/      # Payment domain (scaffolded, Stripe stub)
├── notification-service/ # Event-driven notifications (scaffolded)
├── shared/               # Base classes + shared domain event schemas
├── scripts/
│   └── init-db.sql       # Creates all per-service PostgreSQL databases
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| HTTP framework | FastAPI |
| ORM | SQLAlchemy 2.x async + asyncpg |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Message broker | RabbitMQ via aio-pika |
| Cache / sessions | Redis |
| Auth | python-jose (JWT) + passlib/bcrypt |
| Containerisation | Docker + docker-compose |

---

## License

MIT
