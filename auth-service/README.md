# auth-service

Authentication and session management microservice for the Marketcore platform.

## Domain Responsibilities

- User registration and account lifecycle
- Password hashing and credential verification (bcrypt)
- JWT access token issuance (short-lived, 30 min)
- Refresh token management with revocation (stored in DB)
- Publishing `UserRegistered` domain events to downstream consumers

This service is the single source of truth for user identity. It does **not** own profile data, roles, or permissions beyond `is_active` / `is_verified` flags — those belong to a future identity/profile service.

## Bounded Context

**Authentication** context. Interacts with:
- **Notification** context (consumes `user.registered` → sends welcome email)
- **API Gateway** (validates JWT tokens on every inbound request via `/auth/me` or shared secret verification)

## Tech Stack

| Concern | Choice |
|---|---|
| Framework | FastAPI 0.115 + uvicorn |
| ORM | SQLAlchemy 2 (async) |
| Database | PostgreSQL 16 (asyncpg driver) |
| Migrations | Alembic |
| Password hashing | bcrypt 4.2 |
| Token signing | python-jose (HS256) |
| Messaging | aio-pika (RabbitMQ FANOUT exchange) |
| Cache / sessions | Redis (future — token blocklist) |
| API docs | Scalar UI (`/docs`) |

## API Overview

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/register` | Create account, publish `UserRegistered` |
| `POST` | `/auth/login` | Issue access + refresh tokens |
| `POST` | `/auth/refresh` | Rotate refresh token, issue new access token |
| `POST` | `/auth/logout` | Revoke refresh token |
| `GET` | `/auth/me` | Return authenticated user profile |
| `GET` | `/health` | Liveness probe |
| `GET` | `/docs` | Scalar API reference |

## Event Contracts

### Published

| Event | Exchange | Trigger |
|---|---|---|
| `user.registered` | `user.events` (FANOUT) | Successful registration |

**Payload:**
```json
{
  "event_id": "uuid",
  "occurred_at": "2026-06-12T00:00:00",
  "event_type": "user.registered",
  "user_id": "uuid",
  "email": "user@example.com"
}
```

### Consumed

None. Auth-service is a pure producer for user lifecycle events.

## Domain Model

```
User (Entity / Aggregate Root)
  id              UUID
  email           Email (Value Object — regex-validated)
  hashed_password HashedPassword (Value Object — bcrypt)
  is_active       bool
  is_verified     bool
  created_at      datetime

RefreshToken (Entity)
  id         UUID
  user_id    FK → User
  token      string (opaque, indexed)
  expires_at datetime
  is_revoked bool
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/auth_db` | Async Postgres DSN |
| `RABBITMQ_URL` | `amqp://rabbitmq:rabbitmq@localhost:5672/` | RabbitMQ connection string |
| `REDIS_URL` | `redis://localhost:6379/1` | Redis DSN (DB index 1) |
| `SECRET_KEY` | `secret-key-change-in-production` | JWT signing key — **rotate in prod** |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token TTL |

## Local Development

**Via Docker (recommended):**
```bash
# Start infrastructure + this service
docker-compose up --build auth-service postgres rabbitmq redis
```

**Bare Python (Python 3.12):**
```bash
cd auth-service
pip install -r requirements.txt

export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/auth_db"
export SECRET_KEY="dev-secret"

# Run migrations
alembic upgrade head

# Start the service
uvicorn main:app --port 8001 --reload
```

**API docs:** http://localhost:8001/docs

## Migrations

```bash
# Generate a new migration after model changes
alembic revision --autogenerate -m "describe_change"

# Apply
alembic upgrade head

# Roll back one step
alembic downgrade -1
```
