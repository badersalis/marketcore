import logging
import os
from contextlib import asynccontextmanager

from arq import create_pool
from arq.connections import RedisSettings
from asgi_correlation_id import CorrelationIdFilter, CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from core.config import ARQ_QUEUE_NAME, settings
from shared.telemetry import setup_telemetry
from infrastructure.messaging.consumer import NotificationConsumer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s [%(correlation_id)s] %(name)s — %(message)s",
    force=True,
)



@asynccontextmanager
async def lifespan(app: FastAPI):
    arq_pool = await create_pool(
        RedisSettings.from_dsn(settings.REDIS_URL),
        default_queue_name=ARQ_QUEUE_NAME,
    )
    app.state.arq_pool = arq_pool

    consumer = NotificationConsumer(
        rabbitmq_url=settings.RABBITMQ_URL,
        arq_pool=arq_pool,
    )
    await consumer.start()
    app.state.consumer = consumer

    yield

    await consumer.stop()
    await arq_pool.close()


app = FastAPI(
    title="Notification Service",
    version="1.0.0",
    description="Consumes domain events and enqueues transactional email jobs via ARQ.",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(CorrelationIdMiddleware)

setup_telemetry(
    app,
    settings.OTEL_EXPORTER_OTLP_ENDPOINT,
    settings.OTEL_SERVICE_NAME,
    instrument_aio_pika=True,
)
for _handler in logging.root.handlers:
    _handler.addFilter(CorrelationIdFilter(default_value="-"))


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "service": "notification-service"}


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
      data-configuration='{{"theme":"purple","layout":"modern"}}'
    ></script>
    <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference"></script>
  </body>
</html>"""
    )
