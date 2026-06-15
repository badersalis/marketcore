# System Architecture Overview

## Platform: Marketcore

A microservices-based e-commerce platform. Each service owns its data, communicates asynchronously via events, and exposes a synchronous HTTP API for client-facing operations.

## Service Map

```
                         ┌─────────────────┐
                         │   API Gateway   │  :8000
                         │  (FastAPI proxy)│
                         └────────┬────────┘
                    ┌─────────────┼──────────────────┐
                    │             │                  │
           ┌────────▼────┐  ┌─────▼──────┐  ┌───────▼──────┐
           │ auth-service│  │product-svc │  │payment-svc   │
           │   :8001     │  │   :8002    │  │   :8004      │
           │  auth_db    │  │ product_db │  │  payment_db  │
           └─────────────┘  └────────────┘  └──────────────┘
                    │                               │
           ┌────────▼───────────────────────────────▼────┐
           │               RabbitMQ :5672                │
           │  user.events │ product.events │ payment.events │
           └─────────────────────────────────────────────┘
                    │
           ┌────────▼────────────────────┐
           │  notification-service :8005 │ (stub)
           │  order-service        :8003 │ (stub)
           └─────────────────────────────┘

                 Redis :6379  (shared, separate DB indexes per service)
```

## Bounded Contexts

| Context | Service | DB | Owns |
|---|---|---|---|
| Authentication | auth-service | auth_db | Users, sessions, JWT tokens |
| Catalogue | product-service | product_db | Products, categories, pricing |
| Payment | payment-service | payment_db | Payment intents, state machine |
| Order | order-service | order_db | Orders, line items (stub) |
| Notification | notification-service | notification_db | Email/SMS delivery (stub) |

## Data Isolation

Each service has its own PostgreSQL database (`auth_db`, `product_db`, `payment_db`, `order_db`, `notification_db`). There are **no cross-service foreign keys**. References across services (e.g., `payment.user_id`, `payment.order_id`) are plain strings — consistency is eventual, enforced by event handlers.

## Communication Patterns

| Pattern | Used For |
|---|---|
| Synchronous HTTP (REST) | Client-facing CRUD, inter-service reads (e.g., order-service reading product prices) |
| Async events (RabbitMQ FANOUT) | State change notifications, side-effects that must not block the producer |

## Infrastructure Components

| Component | Purpose | Port |
|---|---|---|
| PostgreSQL 16 | Persistent storage per service | 5432 |
| RabbitMQ 3.13 | Async event bus (management UI on 15672) | 5672 |
| Redis 7 | Caching, token blacklist, idempotency TTL | 6379 |

## Security Boundaries

- The API Gateway validates JWT tokens (shared `SECRET_KEY`) before proxying to downstream services
- Services trust `user_id` extracted from the gateway-validated token — they do **not** re-validate JWTs internally (trust boundary at the gateway edge)
- The `payment-service` enforces ownership checks: `payment.user_id` must match the requesting `user_id`
- No service exposes its database port outside the Docker network

## Scalability Notes

- All services are stateless — horizontal scaling via multiple replicas behind the API Gateway is safe
- SQLAlchemy async engine with connection pooling (`pool_pre_ping=True`) handles Postgres connection management
- RabbitMQ FANOUT exchanges decouple producers from consumer count — adding a new consumer requires no producer changes
- Redis is a shared dependency; isolate services using separate DB indexes (auth→1, product→2, order→3, payment→4) to prevent key collisions and allow independent eviction policies
