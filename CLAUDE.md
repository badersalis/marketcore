# MarketCore — Claude Code Guidelines

## Commit Rules

Every commit must be **scoped to a single service or concern**. These rules are enforced automatically by `commitizen` via the `pre-commit` `commit-msg` hook.

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
| `infra` | Docker, monitoring, scripts |

### Scopes (one service per commit)

| Scope | Directory |
|---|---|
| `auth` | `auth-service/` |
| `product` | `product-service/` |
| `payment` | `payment-service/` |
| `notification` | `notification-service/` |
| `shared` | `shared/` |
| `infra` | `docker-compose.yml`, `monitoring/`, `scripts/` |
| `docs` | `README.md`, `docs/` |
| `chore` | Deps, tooling, root config |

### Examples

```
feat(auth): add JWT refresh token rotation
fix(product): resolve N+1 query in product listing
feat(payment): integrate Stripe webhook signature verification
infra(infra): add Prometheus scrape config for payment-service
docs(docs): expand event catalog with payment.events schema
```

### Rules

1. One scope per commit — if you touched `auth-service/` and `product-service/`, split into two commits.
2. Use the imperative mood: "add", "fix", "remove" — not "added", "fixing".
3. Keep the summary line under 72 characters.
4. Never commit `.env` files, secrets, or `venv/` contents.

## Setup (first time)

```bash
pip install pre-commit commitizen
pre-commit install --hook-type commit-msg
```

Use `cz commit` instead of `git commit` to get an interactive prompt that builds a valid message for you.
