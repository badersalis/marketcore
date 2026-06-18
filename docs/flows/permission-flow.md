# Permission Flow

## Roles

MarketCore uses three roles, ordered by privilege:

| Role | Who | Default |
|---|---|---|
| `member` | Any registered user | Yes |
| `merchant` | Approved seller | No — requires operator approval |
| `operator` | Platform admin/staff | No — assigned by another operator |

Roles are embedded in the JWT access token as the `role` claim and forwarded by the API gateway as the `X-User-Role` header to every upstream service.

---

## How roles are assigned

### Member (default)
Every user starts as `member` on registration. No action required.

### Merchant
Modeled after real-world marketplaces (Amazon Seller, Etsy shop): a member must **apply**, and a human operator must **approve** before the role is granted.

```
Member ──POST /auth/merchant-requests──► pending request created
                                              │
                              operator reviews request
                                              │
         POST /auth/admin/merchant-requests/{id}/approve
                                              │
                             user.role = merchant
                             user.is_merchant_approved = true
                             MerchantApproved event published
```

Once approved the user's existing tokens become stale — they must re-login to receive a new access token reflecting the `merchant` role.

### Operator
Assigned by another operator only:

```
POST /auth/admin/assign-role   (requires operator token)
body: { "user_id": "...", "role": "operator" }
```

There is no self-service path to become an operator.

---

## Who can publish a product

**Only `merchant` and `operator`** should be able to create, update, or deactivate products. This matches real-world e-commerce rules where anonymous visitors and plain buyers can browse but cannot list items for sale.

The permission hierarchy as expressed in code (`permissions.py`):

| Guard | Allowed roles |
|---|---|
| `require_member` | member, merchant, operator |
| `require_merchant` | merchant, operator |
| `require_operator` | operator only |

Product write operations (`POST /products`, `PUT /products/{id}`, `DELETE /products/{id}`) must use `require_merchant`.

> **Current gap:** the product-service routers do not yet inject auth dependencies — those endpoints are open. The gateway's JWT middleware validates tokens and forwards `X-User-Role`, but the product service must also enforce `require_merchant` on write routes before this is production-safe.

---

## Gateway enforcement

The API gateway enforces authentication before proxying any request:

1. Strips the raw `Authorization` header.
2. Decodes and validates the JWT (signature + `type == "access"`).
3. Injects `X-User-Id`, `X-User-Role`, `X-User-Email` into the forwarded request.
4. Upstream services trust those headers — they do **not** re-verify the JWT.

Public routes (no token required): `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `GET /products/*`, `GET /categories/*`, `GET /health`.

---

## Real-world rationale

| Platform | Equivalent of `merchant` |
|---|---|
| Amazon | Seller account (approved after identity + bank verification) |
| Etsy | Shop owner (shop creation = implicit approval) |
| eBay | Verified seller (feedback threshold + ID check) |
| Shopify | Store owner (paid plan = implicit approval) |

MarketCore's explicit operator-approval step mirrors the Amazon/eBay model where the platform vets sellers before they can list. This prevents spam listings and gives operators control over who sells on the platform.
