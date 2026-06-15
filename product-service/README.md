# product-service

Product catalogue microservice for the Marketcore platform.

## Domain Responsibilities

- Category management (create, list)
- Product lifecycle: create, update, soft-delete (deactivate), paginated listing
- Slug uniqueness enforcement (URL-safe identifiers)
- Price management via `Money` value object (Decimal, ISO-4217 currency)
- Stock tracking (integer units, no reservation logic — that belongs to order-service)

This service owns the canonical product catalogue. It does **not** process orders, manage inventory reservations, or handle pricing rules — those are separate bounded contexts.

## Bounded Context

**Catalogue** context. Interacts with:
- **Order** context (order-service calls product-service to validate product availability and fetch current prices)
- **Search** context (future — product data fed to Elasticsearch/Algolia)

## Tech Stack

| Concern | Choice |
|---|---|
| Framework | FastAPI 0.115 + uvicorn |
| ORM | SQLAlchemy 2 (async) |
| Database | PostgreSQL 16 (asyncpg driver) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Messaging | aio-pika (wired in docker-compose, not yet publishing events) |
| Cache | Redis (DB index 2 — future: product cache invalidation) |
| API docs | Scalar UI (`/docs`) |

## API Overview

### Categories

| Method | Path | Description |
|---|---|---|
| `POST` | `/categories/` | Create a category |
| `GET` | `/categories/` | List all categories |

### Products

| Method | Path | Description |
|---|---|---|
| `POST` | `/products/` | Create a product |
| `GET` | `/products/` | List active products (paginated, filterable by category) |
| `GET` | `/products/{id}` | Get product by ID |
| `PUT` | `/products/{id}` | Update product fields |
| `DELETE` | `/products/{id}` | Deactivate (soft-delete) product |
| `GET` | `/health` | Liveness probe |
| `GET` | `/docs` | Scalar API reference |

## Event Contracts

### Published

None currently. Planned:

| Event | Exchange | Trigger |
|---|---|---|
| `product.created` | `product.events` (FANOUT) | Product creation |
| `product.deactivated` | `product.events` (FANOUT) | Product deactivation |
| `product.stock_depleted` | `product.events` (FANOUT) | Stock reaches 0 |

### Consumed

None currently.

## Domain Model

```
Category (Entity / Aggregate Root)
  id    UUID
  name  string
  slug  Slug (Value Object — auto-generated, unique)

Product (Entity / Aggregate Root)
  id          UUID
  name        string
  description string
  price       Money (Value Object — Decimal + ISO-4217 currency)
  stock       int  (≥ 0)
  category_id FK → Category (nullable)
  is_active   bool
  created_at  datetime
```

**Value Objects:**

- `Money(amount: Decimal, currency: str)` — arithmetic-safe, prevents negative amounts
- `Slug(value: str)` — auto-generated from name, enforces URL-safe characters and uniqueness

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/product_db` | Async Postgres DSN |
| `RABBITMQ_URL` | `amqp://rabbitmq:rabbitmq@localhost:5672/` | RabbitMQ (reserved for future event publishing) |
| `REDIS_URL` | `redis://localhost:6379/2` | Redis DSN (DB index 2) |
| `SECRET_KEY` | `secret-key-change-in-production` | Shared signing key (token validation) |
| `ALGORITHM` | `HS256` | JWT algorithm |

## Local Development

**Via Docker (recommended):**
```bash
docker-compose up --build product-service postgres
```

**Bare Python:**
```bash
cd product-service
pip install -r requirements.txt

export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/product_db"

alembic upgrade head
uvicorn main:app --port 8002 --reload
```

**API docs:** http://localhost:8002/docs

## Migrations

```bash
alembic revision --autogenerate -m "describe_change"
alembic upgrade head
alembic downgrade -1
```
