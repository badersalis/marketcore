# Payment Lifecycle Flow

## Overview

An order placement triggers a payment intent. The client (or order-service) then confirms the payment. The outcome propagates via events.

## Full Sequence

```
Client / order-service
  │
  │  POST /payments/intents
  │  { order_id, user_id, amount, currency, idempotency_key }
  ▼
payment-service (port 8004)
  │
  ├─ Check idempotency_key in DB
  │      └─ If exists AND params match → return existing payment (safe retry)
  │      └─ If exists AND params differ → 409 Conflict
  ├─ Validate amount > 0, currency is 3-letter ISO code
  ├─ Create Payment entity: status = PENDING
  ├─ Persist → PostgreSQL (payment_db.payments)
  ├─ Publish PaymentCreated → RabbitMQ "payment.events"
  │
  └─ 201 Created  { id, status: "pending", ... }

                  ┌──────────────────────────────────────────┐
RabbitMQ          │  payment.events  (FANOUT, durable)       │
                  └──────┬──────────────────┬────────────────┘
                         │                  │
                  order-service        notification-service
                  mark: payment_pending   (optional notification)


Client
  │
  │  POST /payments/{id}/confirm?user_id={uid}
  ▼
payment-service
  │
  ├─ Load Payment by ID
  ├─ Verify payment.user_id == requesting user_id → 403 if mismatch
  ├─ Call payment.confirm(provider_reference="mock_ref_...")
  │      └─ Guard: status must be PENDING or PROCESSING → 422 if terminal
  ├─ Update Payment → status = CONFIRMED
  ├─ Publish PaymentConfirmed → "payment.events"
  │
  └─ 200 OK  { id, status: "confirmed", provider_reference, ... }

                  ┌──────────────────────────────────────────┐
RabbitMQ          │  payment.events  (FANOUT)                │
                  └──────┬──────────────────┬────────────────┘
                         │                  │
                  order-service        notification-service
                  mark: paid           send payment receipt email
```

## Failure Path

```
payment-service
  │
  │  payment.fail(reason="...")
  ├─ Update Payment → status = FAILED
  ├─ Publish PaymentFailed → "payment.events"
  │
  └─ order-service: mark order as payment_failed
     notification-service: send failure notification
```

## State Machine

```
                  ┌─────────────┐
             ┌───►│  PROCESSING │──────────────┐
             │    └─────────────┘              │
  ┌─────────┐│                          ┌──────▼──────┐
  │ PENDING ├┤                          │  CONFIRMED  │ (terminal)
  └─────────┘│                          └─────────────┘
             │    ┌──────────┐
             ├───►│  FAILED  │ (terminal)
             │    └──────────┘
             │    ┌───────────┐
             └───►│ CANCELLED │ (terminal — only from PENDING)
                  └───────────┘
```

## Idempotency Matrix

| Same key, same params | Result |
|---|---|
| First call | 201 Created, event published |
| Retry (network timeout) | 201 with existing payment, no duplicate event |
| Same key, different amount | 409 Conflict |

## Production Considerations

**Provider webhook** — when a real provider is integrated, `confirm()` is called from a webhook handler, not a client-facing endpoint. The `POST /payments/{id}/confirm` endpoint becomes internal only or is replaced by the webhook path.

**Outbox pattern** — same concern as the registration flow. For guaranteed event delivery, use a transactional outbox table.

**Refund flow** — a `REFUNDED` terminal state is defined in `PaymentStatus`. The refund use case (calling `payment.refund()` after provider confirms) is not yet implemented.
