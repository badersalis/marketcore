# Event Catalog

All inter-service communication uses RabbitMQ FANOUT exchanges. Each exchange is durable; messages are persisted (`delivery_mode=PERSISTENT`). Consumers bind their own durable queues to the exchange — the producer is unaware of how many consumers exist.

## Exchange Topology

```
user.events    (FANOUT, durable)
product.events (FANOUT, durable)  ← planned
order.events   (FANOUT, durable)
payment.events (FANOUT, durable)
```

---

## user.events

### UserRegistered

| Field | Type | Description |
|---|---|---|
| `event_id` | UUID string | Unique event ID (for deduplication) |
| `occurred_at` | ISO-8601 datetime | When the event occurred |
| `event_type` | `"user.registered"` | Discriminator |
| `user_id` | UUID string | Newly created user |
| `email` | string | User's email address |

**Producer:** `auth-service`  
**Consumers:** `notification-service` (welcome email), `order-service` (future: initialize user cart)

```json
{
  "event_id": "3f4a1b2c-...",
  "occurred_at": "2026-06-12T10:00:00",
  "event_type": "user.registered",
  "user_id": "a1b2c3d4-...",
  "email": "user@example.com"
}
```

---

## product.events *(planned)*

### ProductCreated *(planned)*

**Producer:** `product-service`  
**Consumers:** search indexer, recommendation engine

### ProductDeactivated *(planned)*

**Producer:** `product-service`  
**Consumers:** order-service (invalidate open cart items), search indexer

---

## order.events

### OrderPlaced

| Field | Type | Description |
|---|---|---|
| `event_id` | UUID string | Unique event ID |
| `occurred_at` | ISO-8601 datetime | — |
| `event_type` | `"order.placed"` | — |
| `order_id` | UUID string | — |
| `user_id` | UUID string | — |
| `total_amount` | float | Order total |
| `currency` | string (ISO-4217) | — |

**Producer:** `order-service`  
**Consumers:** `payment-service` (future: auto-create payment intent), `notification-service`

### OrderCancelled

| Field | Type | Description |
|---|---|---|
| `order_id` | UUID string | — |
| `user_id` | UUID string | — |
| `reason` | string | Cancellation reason |

**Producer:** `order-service`  
**Consumers:** `payment-service` (cancel pending payment), `notification-service`

---

## payment.events

### PaymentCreated

| Field | Type | Description |
|---|---|---|
| `event_id` | UUID string | — |
| `occurred_at` | ISO-8601 datetime | — |
| `event_type` | `"payment.created"` | — |
| `payment_id` | UUID string | — |
| `order_id` | UUID string | — |
| `user_id` | UUID string | — |
| `amount` | float | — |
| `currency` | string (ISO-4217) | — |
| `idempotency_key` | string | Caller-supplied retry key |

**Producer:** `payment-service`  
**Consumers:** `order-service` (mark order as payment_pending), `notification-service`

### PaymentConfirmed

| Field | Type | Description |
|---|---|---|
| `payment_id` | UUID string | — |
| `order_id` | UUID string | — |
| `user_id` | UUID string | — |
| `amount` | float | — |
| `currency` | string | — |

**Producer:** `payment-service`  
**Consumers:** `order-service` (mark order as paid), `notification-service` (send receipt)

### PaymentFailed

| Field | Type | Description |
|---|---|---|
| `payment_id` | UUID string | — |
| `order_id` | UUID string | — |
| `user_id` | UUID string | — |
| `reason` | string | Failure description |

**Producer:** `payment-service`  
**Consumers:** `order-service` (mark order as payment_failed), `notification-service`

---

## Idempotency & At-Least-Once Delivery

Every consumer **must** be idempotent. RabbitMQ guarantees at-least-once delivery; the same event can arrive more than once after a consumer crash/restart. Use `event_id` as the deduplication key — store processed IDs in Redis with a TTL of 24 h.

## Dead Letter Strategy

For each consumer queue, configure a dead-letter exchange (DLX):

```python
await channel.declare_queue(
    "payment.events.order-service",
    durable=True,
    arguments={
        "x-dead-letter-exchange": "payment.events.dlx",
        "x-message-ttl": 86_400_000,  # 24h
    },
)
```

Dead-lettered messages should be monitored via the RabbitMQ Management UI (port 15672) and replayed once the root cause is resolved.
