# User Registration Flow

## Overview

A client submits credentials → auth-service validates, persists, and publishes an event → downstream services react asynchronously.

## Sequence

```
Client
  │
  │  POST /auth/register  { email, password }
  ▼
auth-service (port 8001)
  │
  ├─ Validate email format (Email value object — regex)
  ├─ Validate password (≥ 8 chars, ≤ 72 bytes after encode)
  ├─ Check uniqueness: SELECT FROM users WHERE email = ?
  │      └─ 409 Conflict if exists
  ├─ Hash password (bcrypt, cost factor 12)
  ├─ Persist User entity → PostgreSQL (auth_db.users)
  ├─ Publish UserRegistered → RabbitMQ exchange "user.events"
  │
  └─ 201 Created  { id, email, is_active, is_verified, created_at }

                      ┌──────────────────────────────────────┐
RabbitMQ              │  user.events  (FANOUT, durable)      │
                      └──────┬─────────────────┬─────────────┘
                             │                 │
                    notification-service   order-service (future)
                             │
                    Send welcome email
                    (async — does not block registration response)
```

## Error Cases

| Scenario | HTTP | Event Published? |
|---|---|---|
| Email already exists | 409 | No |
| Invalid email format | 422 | No |
| DB unavailable | 503 | No |
| RabbitMQ unavailable | 201 | No — logged, not retried (fire-and-forget) |

## Production Considerations

**Transactional outbox** — the current implementation publishes directly after the DB commit. If RabbitMQ is unavailable, the event is silently dropped. For guaranteed delivery, replace with an outbox pattern: write the event to an `outbox` table in the same DB transaction, then a relay process forwards it to RabbitMQ.

**Email verification** — the `is_verified` flag exists on the User entity. A `/auth/verify-email` endpoint (sending a signed token) is a natural next step.
