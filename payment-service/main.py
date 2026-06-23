import logging
import os
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdFilter, CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from core.config import settings
from shared.telemetry import setup_telemetry
from infrastructure.messaging.event_publisher import EventPublisher
from infrastructure.persistence.database import Base, engine
from presentation.routers.payment_router import router as payment_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s [%(correlation_id)s] %(name)s — %(message)s",
    force=True,
)



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    publisher = EventPublisher(settings.RABBITMQ_URL)
    await publisher.connect()
    app.state.event_publisher = publisher

    yield

    await publisher.disconnect()
    await engine.dispose()


app = FastAPI(
    title="Payment Service",
    version="1.0.0",
    description=(
        "Payment processing microservice — stub phase. "
        "Manages payment intents, state transitions, and publishes domain events. "
        "Provider integration (Stripe / PayPal) is wired in a later phase."
    ),
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CorrelationIdMiddleware)

setup_telemetry(
    app,
    settings.OTEL_EXPORTER_OTLP_ENDPOINT,
    settings.OTEL_SERVICE_NAME,
    instrument_sqlalchemy=True,
    instrument_aio_pika=True,
)
for _handler in logging.root.handlers:
    _handler.addFilter(CorrelationIdFilter(default_value="-"))

app.include_router(payment_router, prefix="/payments", tags=["Payments"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "service": "payment-service"}


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
