# payment-service

Payment processing microservice for the Marketcore platform — **stub phase**.

Provider integration (Stripe, PayPal, etc.) is intentionally absent. The service owns the complete domain model, state machine, idempotency layer, and event contracts. Plugging in a real provider requires only changes to the `confirm_payment` use case and the infrastructure layer — no domain or contract changes.

## Domain Responsibilities

- Accept payment intents (PENDING state) with idempotency guarantees
- Drive the payment state machine: PENDING → PROCESSING → CONFIRMED / FAILED / CANCELLED
- Publish domain events (`PaymentCreated`, `PaymentConfirmed`, `PaymentFailed`) to downstream services
- Authorize access: each payment is owned by a user; cross-user reads/writes are rejected

This service does **not** own order state, product inventory, or user accounts. It holds a reference (`order_id`, `user_id`) to records owned by other bounded contexts.

## Bounded Context

**Payment** context. Interacts with:
- **Order** context — consumes `order.placed`, will eventually auto-initiate a payment intent
- **Order** context — `PaymentConfirmed` causes order-service to mark order as paid
- **Notification** context — `PaymentConfirmed` / `PaymentFailed` triggers email receipts

## Tech Stack

| Concern | Choice |
|---|---|
| Framework | FastAPI 0.115 + uvicorn |
| ORM | SQLAlchemy 2 (async) |
| Database | PostgreSQL 16 (`payment_db`) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Messaging | aio-pika (RabbitMQ FANOUT exchanges) |
| Cache | Redis (DB index 4 — future: idempotency key TTL cache) |
| API docs | Scalar UI (`/docs`) |

## API Overview

| Method | Path | Description |
|---|---|---|
| `POST` | `/payments/intents` | Create payment intent (idempotent) |
| `POST` | `/payments/{id}/confirm` | Confirm payment — mock provider |
| `GET` | `/payments/{id}` | Get payment by ID |
| `GET` | `/payments/` | List payments for a user |
| `GET` | `/health` | Liveness probe |
| `GET` | `/docs` | Scalar API reference |

### Idempotency

`POST /payments/intents` is safe to retry. Supply the same `idempotency_key` with identical parameters and you receive the existing payment. Supplying the same key with **different** parameters returns `409 Conflict`.

## Event Contracts

### Published

All events are published to the `payment.events` exchange (FANOUT, durable).

| Event | Trigger | Key Fields |
|---|---|---|
| `payment.created` | Intent created | `payment_id`, `order_id`, `user_id`, `amount`, `currency`, `idempotency_key` |
| `payment.confirmed` | Payment confirmed | `payment_id`, `order_id`, `user_id`, `amount`, `currency` |
| `payment.failed` | Payment failed | `payment_id`, `order_id`, `user_id`, `reason` |

**Example — payment.created:**
```json
{
  "event_id": "uuid",
  "occurred_at": "2026-06-12T00:00:00",
  "event_type": "payment.created",
  "payment_id": "uuid",
  "order_id": "uuid",
  "user_id": "uuid",
  "amount": 99.99,
  "currency": "USD",
  "idempotency_key": "order-uuid-attempt-1"
}
```

### Consumed

| Event | Exchange | Action |
|---|---|---|
| `order.placed` | `order.events` | *(future)* Auto-create payment intent |

## Domain Model

```
Payment (Aggregate Root)
  id                 UUID
  order_id           string   — reference to order-service (no FK across services)
  user_id            string   — reference to auth-service
  amount             Money (Value Object — Decimal + ISO-4217)
  status             PaymentStatus (Value Object — enum)
  idempotency_key    string   — unique, caller-supplied
  provider_reference string?  — set after provider confirmation
  failure_reason     string?  — set on FAILED state
  created_at         datetime
  updated_at         datetime
```

**State machine:**
```
PENDING ──► PROCESSING ──► CONFIRMED
   │              │
   │              └──────► FAILED
   │
   └──────────────────────► CANCELLED
```

**Value Objects:**
- `Money(amount: Decimal, currency: str)` — enforces non-negative amounts and ISO-4217 codes
- `PaymentStatus(str, Enum)` — `pending | processing | confirmed | failed | refunded | cancelled`
- `IdempotencyKey(value: str)` — 1–255 character uniqueness token

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/payment_db` | Async Postgres DSN |
| `RABBITMQ_URL` | `amqp://rabbitmq:rabbitmq@localhost:5672/` | RabbitMQ connection string |
| `REDIS_URL` | `redis://localhost:6379/4` | Redis DSN (DB index 4) |
| `SECRET_KEY` | `secret-key-change-in-production` | Shared signing key |
| `ALGORITHM` | `HS256` | JWT algorithm |

## Local Development

**Via Docker (recommended):**
```bash
docker-compose up --build payment-service postgres rabbitmq
```

**Bare Python:**
```bash
cd payment-service
pip install -r requirements.txt

export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/payment_db"
export RABBITMQ_URL="amqp://rabbitmq:rabbitmq@localhost:5672/"

alembic upgrade head
uvicorn main:app --port 8004 --reload
```

**API docs:** http://localhost:8004/docs

## Migrations

```bash
alembic revision --autogenerate -m "describe_change"
alembic upgrade head
alembic downgrade -1
```

## Adding a Real Provider

When integrating Stripe (or any provider):

1. Add `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` to `core/config.py`
2. Create `infrastructure/providers/stripe_provider.py` implementing a `PaymentProvider` protocol
3. Inject it into `ConfirmPayment` use case — the domain and event contracts are unchanged
4. Add a `POST /payments/webhooks/stripe` endpoint that verifies the signature and calls `payment.confirm()` or `payment.fail()`
