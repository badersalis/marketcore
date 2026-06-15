# MarketCore

> A production-grade, event-driven e-commerce backend — built to clone, adapt, and ship.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square&logo=postgresql&logoColor=white)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-3.13-FF6600?style=flat-square&logo=rabbitmq&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat-square&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-11-F46800?style=flat-square&logo=grafana&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)

---

## Why MarketCore?

Most e-commerce starters are either too simple (a single Django monolith) or too complex (Kubernetes hell on day one). MarketCore sits in the sweet spot:

- **Production patterns, zero boilerplate** — Domain-Driven Design, CQRS-ready use cases, clean architecture boundaries in every service
- **Real async messaging** — RabbitMQ FANOUT exchanges, ARQ background jobs, Dead Letter Exchanges for reliable delivery
- **Full observability out of the box** — Prometheus metrics, Grafana dashboards, correlation IDs threaded across every HTTP request and RabbitMQ message
- **Clone it and own it** — no magic frameworks, no vendor lock-in; just Python, FastAPI, and patterns you already understand

---

## Architecture

```
                    ┌─────────────────────────────────────────────┐
                    │              API Gateway  :8000              │
                    │     JWT validation · Rate limiting · Proxy   │
                    └──┬──────────┬──────────┬──────────┬─────────┘
                       │          │          │          │
            ┌──────────▼──┐  ┌────▼───┐  ┌──▼────┐  ┌──▼──────────┐
            │ auth-service│  │product │  │ order │  │  payment    │
            │   :8001     │  │ :8002  │  │ :8003 │  │   :8004     │
            └──────┬──────┘  └────────┘  └───────┘  └──────┬──────┘
                   │                                         │
                   └──────────────┬──────────────────────────┘
                                  │  async domain events
                         ┌────────▼────────┐
                         │    RabbitMQ      │  :5672 / :15672
                         │  user.events     │
                         │  order.events    │
                         │  payment.events  │
                         └────────┬─────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │    notification-service     │  :8005  (RabbitMQ consumer)
                    │    notification-worker      │         (ARQ email worker)
                    └───────────────────────────┘

  ┌────────────┐   ┌──────────────┐   ┌─────────────────┐
  │ Prometheus │   │   Grafana    │   │  RedisInsight   │
  │   :9090    │   │   :3000      │   │    :5540        │
  └────────────┘   └──────────────┘   └─────────────────┘
```

**Every HTTP request carries an `X-Correlation-ID` header that is propagated through RabbitMQ messages and all log lines — making cross-service debugging a single `grep`.**

---

## Services

| Service | Port | Status | Responsibility |
|---|---|---|---|
| `api-gateway` | 8000 | planned | Single entry point, JWT validation, rate limiting, reverse proxy |
| `auth-service` | 8001 | **live** | Registration, email verification (OTP), login, JWT access + refresh tokens |
| `product-service` | 8002 | **live** | Product catalogue, SKUs (variants), categories, inventory |
| `order-service` | 8003 | scaffolded | Cart management, order lifecycle (pending → delivered) |
| `payment-service` | 8004 | scaffolded | Payment intents, Stripe webhook stub |
| `notification-service` | 8005 | **live** | Email delivery from domain events via ARQ background jobs |

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| HTTP framework | **FastAPI** | Async-first, auto-generated OpenAPI, dependency injection |
| API docs | **Scalar** | Beautiful modern API reference at `/docs` on every service |
| ORM | **SQLAlchemy 2.x async** + asyncpg | Non-blocking Postgres with full ORM power |
| Migrations | **Alembic** | Schema versioning per service, per database |
| Validation | **Pydantic v2** | Fast, type-safe request/response contracts |
| Message broker | **RabbitMQ** via aio-pika | Durable FANOUT exchanges, DLX, at-least-once delivery |
| Background jobs | **ARQ** (async Redis Queue) | Retry logic, job observability, Redis-backed queue |
| Transactional email | **Resend** | Reliable delivery, HTML templates per event type |
| Cache / sessions | **Redis 7** | Token blacklist, OTP storage, ARQ queue backend |
| Auth | **python-jose** (JWT) + passlib/bcrypt | Stateless auth with refresh token rotation |
| Observability | **Prometheus** + **Grafana** | Auto-scraped `/metrics` on every service, pre-provisioned datasource |
| Correlation IDs | **asgi-correlation-id** | `X-Correlation-ID` propagated across HTTP and AMQP |
| Redis UI | **RedisInsight** | Browse keys, queues, TTLs visually |
| Containerisation | **Docker** + **Compose** | One command to boot the entire platform |

---

## Quick Start

```bash
# 1. Clone and configure
git clone https://github.com/your-org/marketcore.git
cd marketcore
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY and RESEND_API_KEY

# 2. Boot everything
docker compose up --build

# 3. Run migrations
docker compose exec auth-service     alembic upgrade head
docker compose exec product-service  alembic upgrade head
docker compose exec payment-service  alembic upgrade head

# 4. Verify
curl http://localhost:8001/health
curl http://localhost:8002/health
```

That's it. You now have a fully operational microservices platform with auth, products, payments, async email notifications, and a live observability stack.

---

## Developer Portals

Once running, every entry point is a click away:

| Portal | URL | Credentials |
|---|---|---|
| Auth API docs | http://localhost:8001/docs | — |
| Product API docs | http://localhost:8002/docs | — |
| Payment API docs | http://localhost:8004/docs | — |
| Notification API docs | http://localhost:8005/docs | — |
| RabbitMQ Management | http://localhost:15672 | `rabbitmq` / `rabbitmq` |
| Grafana | http://localhost:3000 | `admin` / `admin` |
| Prometheus | http://localhost:9090 | — |
| RedisInsight | http://localhost:5540 | — |

---

## Event System

Services communicate through **RabbitMQ FANOUT exchanges** — producers publish to an exchange without knowing who is listening. Add a new consumer without touching a single line of producer code.

```
user.events    (FANOUT, durable)
  ├── notification.user.events   → verification email, welcome email
  └── [your queue]               → drop any consumer in here

payment.events (FANOUT, durable)
  ├── notification.payment.events → payment confirmed / failed emails
  └── [your queue]

order.events   (FANOUT, durable)
product.events (FANOUT, durable)  ← planned
```

Every queue has a **Dead Letter Exchange (DLX)** and a 24-hour message TTL. Poison messages land in the DLX where you can inspect and replay them from the RabbitMQ Management UI at http://localhost:15672.

Correlation IDs are stamped on every AMQP message via the `correlation_id` property, so you can trace a user action from the HTTP request all the way through RabbitMQ into the background email job.

See [docs/events/event-catalog.md](docs/events/event-catalog.md) for the full event schema reference.

---

## Email Pipeline

Transactional emails follow a two-stage pipeline designed for reliability:

```
auth-service (HTTP request)
     │  publishes UserRegistered / UserVerified
     ▼
RabbitMQ  (durable queue, DLX, 24h TTL)
     │  notification-service consumes → enqueue_job()
     ▼
Redis  (ARQ queue: marketcore:email)
     │  notification-worker dequeues → Resend API
     ▼
User's inbox
```

The HTTP request returns immediately. Email is decoupled across two async layers: RabbitMQ for reliable event delivery and ARQ for job execution with automatic retries (configurable via `ARQ_MAX_TRIES`).

---

## SKUs — Product Variants

Products support **SKUs (Stock Keeping Units)** — variants with their own unique code, attributes, optional price override, and independent stock count:

```
Product: "Classic T-Shirt"
  ├── SKU: TSHIRT-BLK-S  { color: black, size: S, stock: 50 }
  ├── SKU: TSHIRT-BLK-L  { color: black, size: L, stock: 30 }
  └── SKU: TSHIRT-WHT-M  { color: white, size: M, stock: 0, price_override: $19.99 }
```

SKU codes are globally unique across the platform.

---

## Observability

**Prometheus** scrapes `/metrics` from every service every 15 seconds. **Grafana** starts with Prometheus pre-provisioned as a datasource — open http://localhost:3000 and start building dashboards immediately.

Every log line includes the correlation ID:

```
2026-06-14 10:23:41 INFO     [a3f8c2d1] auth_service.use_cases.login_user — Login successful for user@example.com
2026-06-14 10:23:41 INFO     [a3f8c2d1] notification_service.consumer — Enqueueing job for event: user.verified
2026-06-14 10:23:41 INFO     [a3f8c2d1] infrastructure.jobs.email_jobs — Welcome email sent to user@example.com
```

The same `a3f8c2d1` ID connects the HTTP request, the RabbitMQ message, and the background ARQ job — one grep covers the entire flow.

---

## Project Structure

```
marketcore/
├── auth-service/                # Authentication domain (live)
│   ├── domain/                  # Entities, value objects, repository interfaces
│   ├── application/             # Use cases: Register, Login, VerifyEmail, SendOTP
│   ├── infrastructure/          # SQLAlchemy models, Redis cache, RabbitMQ publisher
│   └── presentation/            # FastAPI routers
│
├── product-service/             # Product catalogue (live)
│   ├── domain/                  # Product + SKU entities
│   ├── application/             # Use cases: CRUD products + SKUs
│   ├── infrastructure/          # Models, Alembic migrations
│   └── presentation/            # FastAPI routers
│
├── payment-service/             # Payment domain (scaffolded, Stripe stub)
├── order-service/               # Order domain (scaffolded)
│
├── notification-service/        # Event-driven email (live)
│   ├── infrastructure/
│   │   ├── messaging/           # RabbitMQ consumer — enqueues ARQ jobs
│   │   ├── jobs/                # ARQ job functions with retry logic
│   │   └── email/               # Resend sender + HTML templates
│   └── worker.py                # ARQ WorkerSettings entrypoint
│
├── shared/                      # Shared domain event schemas
│   └── events/
│       ├── user_events.py       # UserRegistered, UserVerified, ...
│       └── payment_events.py    # PaymentCreated, PaymentConfirmed, PaymentFailed
│
├── monitoring/
│   ├── prometheus.yml           # Scrape config for all services
│   └── grafana/
│       └── provisioning/        # Auto-provisions Prometheus datasource on boot
│
├── scripts/
│   └── init-db.sql              # Creates all per-service PostgreSQL databases
│
├── docs/
│   ├── architecture/            # System overview, bounded contexts, security model
│   ├── events/                  # Full event catalog with JSON schemas
│   └── flows/                   # Sequence diagrams: registration, payment lifecycle
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your secrets. All infrastructure wiring (database URLs, broker URLs, Redis DSNs) is handled automatically inside `docker-compose.yml`.

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | *(required)* | JWT signing secret — use at least 32 random characters |
| `POSTGRES_USER` | `postgres` | PostgreSQL superuser |
| `POSTGRES_PASSWORD` | *(required)* | PostgreSQL password |
| `RABBITMQ_USER` | `rabbitmq` | RabbitMQ username |
| `RABBITMQ_PASS` | `rabbitmq` | RabbitMQ password |
| `REDIS_PASSWORD` | *(empty)* | Redis password (blank = no auth) |
| `RESEND_API_KEY` | *(required for email)* | API key from [resend.com](https://resend.com) |
| `EMAIL_FROM` | `Marketcore <onboarding@resend.dev>` | Sender address |
| `GRAFANA_PASSWORD` | `admin` | Grafana admin password |
| `STRIPE_SECRET_KEY` | `sk_test_placeholder` | Stripe secret key (payment-service) |
| `STRIPE_WEBHOOK_SECRET` | `whsec_placeholder` | Stripe webhook signing secret |
| `ARQ_MAX_TRIES` | `5` | Email job retry attempts before giving up |
| `ARQ_JOB_TIMEOUT` | `30` | Seconds before an ARQ job is considered timed out |

---

## Running Migrations

Each service manages its own schema with Alembic against its own isolated database:

```bash
# Apply all pending migrations
docker compose exec auth-service     alembic upgrade head
docker compose exec product-service  alembic upgrade head
docker compose exec payment-service  alembic upgrade head

# Generate a migration after editing a domain model
docker compose exec auth-service alembic revision --autogenerate -m "add phone_number"

# Roll back one migration
docker compose exec auth-service alembic downgrade -1
```

---

## Adding a New Microservice

The architecture is designed to grow. Here's the full checklist:

**1. Create the directory** with the clean architecture layer structure:
```
my-service/
├── domain/
│   ├── entities/
│   ├── value_objects/
│   ├── repositories/       # Abstract interfaces only
│   ├── events/
│   └── exceptions/
├── application/
│   ├── use_cases/          # One class per use case
│   ├── dtos/               # Pydantic request/response models
│   └── services/
├── infrastructure/
│   ├── persistence/
│   │   ├── models.py
│   │   └── migrations/     # Alembic setup
│   ├── repositories/       # Concrete implementations of domain interfaces
│   └── messaging/          # Publisher / consumer
├── presentation/
│   └── routers/
├── core/
│   └── config.py           # Pydantic Settings
├── main.py
├── Dockerfile
└── requirements.txt
```

**2. Add the database** to [scripts/init-db.sql](scripts/init-db.sql):
```sql
CREATE DATABASE market_myservice_db;
GRANT ALL PRIVILEGES ON DATABASE market_myservice_db TO postgres;
```

**3. Register in [docker-compose.yml](docker-compose.yml)** with `depends_on` pointing at `postgres`, `rabbitmq`, and `redis`.

**4. Publish events** by subclassing `DomainEvent` from `shared/events/` — the exchange topology picks them up automatically.

**5. Add observability** — wire `CorrelationIdMiddleware` and `Instrumentator().instrument(app).expose(app)` in `main.py`, then add the service to [monitoring/prometheus.yml](monitoring/prometheus.yml).

See [docs/architecture/system-overview.md](docs/architecture/system-overview.md) for the full bounded context map and security model.

---

## Documentation

| Document | What it covers |
|---|---|
| [System Overview](docs/architecture/system-overview.md) | Bounded contexts, data isolation, security model, scalability notes |
| [Event Catalog](docs/events/event-catalog.md) | Every event schema with field descriptions and JSON examples |
| [User Registration Flow](docs/flows/user-registration-flow.md) | End-to-end sequence from `POST /register` to welcome email |
| [Payment Lifecycle](docs/flows/payment-lifecycle-flow.md) | Payment intent creation through Stripe confirmation and notification |

---

## Contributing

Pull requests are welcome. Here's where the interesting work is:

**Open for contribution:**
- `api-gateway` — JWT validation middleware, route proxying, per-route rate limiting
- `order-service` — cart management, order state machine (pending → confirmed → shipped → delivered)
- Product search and filtering in `product-service`
- Event deduplication using `event_id` in Redis (see the [event catalog](docs/events/event-catalog.md) — every event carries a UUID for exactly this)
- Grafana dashboard presets for request rates, queue depths, error rates

**Develop a service locally without Docker:**
```bash
# Run auth-service locally against dockerised infrastructure
cd auth-service
pip install -r requirements.txt
PYTHONPATH=.. uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Run the ARQ worker alongside notification-service (two terminals)
cd notification-service
PYTHONPATH=.. uvicorn main:app --host 0.0.0.0 --port 8005 --reload
PYTHONPATH=.. arq worker.WorkerSettings

# Tail logs from multiple services at once
docker compose logs -f auth-service product-service notification-service
```

**Architecture rules to preserve:**

1. **No cross-service foreign keys** — services reference each other by plain string IDs; consistency is eventual and enforced by event handlers
2. **Use cases are thin and testable** — no framework code inside `application/`; all dependencies are injected
3. **Events are additive** — adding a new consumer never requires touching the producer
4. **One database per service** — `market_auth_db`, `market_product_db`, etc.; never share a DB across services
5. **Correlation IDs everywhere** — bind `X-Correlation-ID` on every HTTP entry point and stamp it on every AMQP message

---

## License

MIT — clone it, adapt it, ship it.
