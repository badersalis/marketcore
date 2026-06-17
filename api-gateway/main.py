import asyncio
import logging
from contextlib import asynccontextmanager

import httpx
import redis.asyncio as aioredis
from asgi_correlation_id import CorrelationIdFilter, CorrelationIdMiddleware
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from prometheus_fastapi_instrumentator import Instrumentator

from core.config import settings
from middleware.jwt_validator import JWTValidationMiddleware
from middleware.rate_limiter import RateLimitMiddleware
from proxy import reverse_proxy

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s [%(correlation_id)s] %(name)s — %(message)s",
)
for _handler in logging.root.handlers:
    _handler.addFilter(CorrelationIdFilter(default_value="-"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    app.state.redis = redis
    yield
    await redis.aclose()


app = FastAPI(
    title="MarketCore API Gateway",
    version="1.0.0",
    description="Single entry point — JWT validation, rate limiting, reverse proxy.",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

# Middleware order: add_middleware is LIFO.
# Execution order: CorrelationId → JWT → route handler
# Rate limiting uses @app.middleware so it runs after JWT (has user_id context).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(JWTValidationMiddleware)
app.add_middleware(CorrelationIdMiddleware)

Instrumentator().instrument(app).expose(app, include_in_schema=False)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    mw = RateLimitMiddleware(app=None, redis=request.app.state.redis)
    return await mw.dispatch(request, call_next)


async def _service_health(client: httpx.AsyncClient, name: str, url: str) -> tuple[str, str]:
    try:
        resp = await asyncio.wait_for(client.get(f"{url}/health"), timeout=3.0)
        return name, "healthy" if resp.status_code == 200 else "degraded"
    except Exception:
        return name, "unhealthy"


@app.get("/health", tags=["Health"])
async def health():
    service_urls = {
        "auth": settings.AUTH_SERVICE_URL,
        "products": settings.PRODUCT_SERVICE_URL,
        "orders": settings.ORDER_SERVICE_URL,
        "payments": settings.PAYMENT_SERVICE_URL,
        "notifications": settings.NOTIFICATION_SERVICE_URL,
    }
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *[_service_health(client, name, url) for name, url in service_urls.items()]
        )

    services = dict(results)
    statuses = set(services.values())
    if statuses == {"healthy"}:
        overall = "healthy"
    elif "unhealthy" in statuses:
        overall = "unhealthy"
    else:
        overall = "degraded"

    return {"status": overall, "services": services}


@app.get("/docs", include_in_schema=False, response_class=HTMLResponse)
async def scalar_docs():
    return HTMLResponse(
        content=f"""<!doctype html>
<html>
  <head>
    <title>{app.title} — API Reference</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
  </head>
  <body>
    <script
      id="api-reference"
      data-url="/openapi.json"
      data-configuration='{{"theme":"purple","layout":"modern","defaultHttpClient":{{"targetKey":"python","clientKey":"requests"}}}}'
    ></script>
    <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
  </body>
</html>"""
    )


@app.api_route(
    "/{full_path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
    include_in_schema=False,
)
async def catch_all(request: Request):
    return await reverse_proxy(request)
