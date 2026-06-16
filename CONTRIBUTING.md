# Contributing to MarketCore

## Branching strategy

```
main          ← production releases only
develop       ← integration branch; all feature PRs merge here first
feature/*     ← one branch per service or concern, branched from develop
```

### Creating a feature branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/your-feature-name
```

### Opening a PR

1. Push your branch: `git push -u origin feature/your-feature-name`
2. Open a PR from `feature/your-feature-name` → `develop`
3. Include a summary of what changed and how to test it
4. CI must pass before merging

---

## Commit conventions

MarketCore uses [Commitizen](https://commitizen-tools.github.io/commitizen/) with a pre-commit hook that rejects non-conforming messages.

### Format

```
<type>(<scope>): <short imperative summary>

[optional body — the WHY, not the what]
```

### Types

| Type | When to use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code restructure with no behavior change |
| `perf` | Performance improvement |
| `test` | Adding or fixing tests |
| `docs` | Documentation only |
| `chore` | Deps, tooling, CI config |

### Scopes

| Scope | Directory |
|---|---|
| `auth` | `auth-service/` |
| `product` | `product-service/` |
| `payment` | `payment-service/` |
| `notification` | `notification-service/` |
| `order` | `order-service/` |
| `user` | `user-service/` |
| `gateway` | `api-gateway/` |
| `shared` | `shared/` |
| `infra` | `docker-compose.yml`, `scripts/` |
| `docs` | `README.md`, `docs/` |
| `chore` | Deps, tooling, root config |

### Rules

1. One scope per commit — if you touched `auth-service/` and `user-service/`, split into two commits
2. Use imperative mood: "add", "fix", "remove" — not "added", "fixing"
3. Keep the summary line under 72 characters
4. Never commit `.env` files, secrets, or `venv/` contents

### Using Commitizen (interactive prompt)

```bash
cz commit
```

### Setup

```bash
pip install pre-commit commitizen
pre-commit install --hook-type commit-msg
```

---

## Service ports

| Service | Port |
|---|---|
| api-gateway | 8000 |
| auth-service | 8001 |
| product-service | 8002 |
| order-service | 8003 |
| payment-service | 8004 |
| notification-service | 8005 |
| user-service | 8006 |

---

## Async messaging architecture

### Why we use RabbitMQ queues

Every inter-service communication that does not need an immediate response goes through RabbitMQ instead of a direct HTTP call. This gives us:

- **Resilience** — if the consumer is down, messages wait in the queue rather than causing cascading 503s
- **Decoupling** — producers never import or call consumers; either side can be replaced without touching the other
- **Retry / DLX** — failed messages move to a Dead Letter Exchange (DLX) instead of being silently dropped; you can inspect and replay them

### Exchange topology

```
producer                 exchange (FANOUT)       queue(s)              consumer
───────────────────────────────────────────────────────────────────────────────
auth-service   ──────►  user.events         ──► notification-service.user.events  ──► notification-service
payment-service ─────►  payment.events      ──► order-service.payment.events      ──► order-service
                                            ──► notification-service.payment.events ► notification-service
user-service   ──────►  kyc.webhooks        ──► user-service.kyc.webhooks         ──► user-service (internal)
user-service   ──────►  user.events         ──► (future consumers)
```

All exchanges are **FANOUT** and **durable**. All queues are **durable** with a DLX configured.

### Where queues are used and why

#### `user.events` — auth-service → notification-service

Publishes: `user.registered`, `user.verified`, `user.merchant_upgrade_requested`, `user.merchant_approved`

Why a queue: Registration and approval emails are fire-and-forget from auth-service's perspective. Using a queue means a transient email provider outage doesn't block the registration response or roll back the DB transaction.

#### `payment.events` — payment-service → order-service + notification-service

Publishes: `payment.confirmed`, `payment.failed`

Why a queue: Order status transitions (PAYING → CONFIRMED) must happen eventually even if order-service restarts mid-payment. A durable queue with DLX gives us at-least-once delivery.

#### `kyc.webhooks` — user-service webhook endpoint → user-service KYC consumer

Publishes: raw Persona webhook JSON

Why a queue (within the same service): The Persona webhook endpoint must return `200 OK` quickly — Persona will retry if we time out. Writing to the DB synchronously inside the webhook handler risks exceeding Persona's timeout under load. By publishing the raw payload to RabbitMQ and returning immediately, the webhook handler becomes a thin ingest point. The KYC consumer processes the event asynchronously, updates the inquiry status, and publishes `user.kyc_status_updated` downstream.

The DLX on this queue means a processing failure (e.g. DB down) retains the message for inspection rather than discarding it.

---

## Webhooks

### Persona KYC webhook (`POST /kyc/webhook` on user-service)

**Flow:**
```
Persona (external)
  └─► POST /kyc/webhook (user-service)
        ├─ verify Persona-Signature header (HMAC-SHA256, t=<ts>,v1=<sig>)
        ├─ reject replays > 5 min old
        ├─ publish raw body → kyc.webhooks exchange
        └─ return 200 immediately

kyc.webhooks queue
  └─► KYCWebhookConsumer (user-service)
        ├─ parse Persona event (inquiry.completed / inquiry.failed / inquiry.needs_review)
        ├─ look up KYCInquiry by persona_inquiry_id
        ├─ update status in DB
        └─ publish KYCStatusUpdated → user.events exchange

user.events exchange
  └─► (notification-service can subscribe to send KYC result email)
```

**Signature verification:** Persona signs every webhook with HMAC-SHA256 using the webhook secret configured in the Persona dashboard. We verify by computing `HMAC(secret, "{timestamp}.{raw_body}")` and comparing to the `v1` value in the `Persona-Signature` header.

**Sandbox testing:** Use the Persona dashboard → Webhooks → "Send test event" to fire a simulated `inquiry.completed` event against your local tunnel (e.g. ngrok `http 8006`).

### Configuring Persona

1. Create a Persona account at [withpersona.com](https://withpersona.com)
2. In the sandbox, create an Inquiry Template and copy its `itmpl_xxx` ID → `PERSONA_INQUIRY_TYPE_ID`
3. Generate a sandbox API key → `PERSONA_API_KEY`
4. Add a webhook endpoint pointing at `https://<your-domain>/kyc/webhook` → copy the signing secret → `PERSONA_WEBHOOK_SECRET`
