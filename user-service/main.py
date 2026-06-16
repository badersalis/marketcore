import logging
import os
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdFilter, CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from core.config import settings
from infrastructure.clients.persona_client import PersonaClient
from infrastructure.messaging.event_publisher import EventPublisher
from infrastructure.messaging.kyc_consumer import KYCWebhookConsumer
from infrastructure.persistence.database import Base, engine, AsyncSessionFactory
from presentation.routers.kyc_router import router as kyc_router
from presentation.routers.profile_router import router as profile_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s [%(correlation_id)s] %(name)s — %(message)s",
)
for _handler in logging.root.handlers:
    _handler.addFilter(CorrelationIdFilter(default_value="-"))


def setup_telemetry(app: FastAPI, service_name: str) -> None:
    provider = TracerProvider()
    provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(
                endpoint=os.getenv(
                    "OTEL_EXPORTER_OTLP_ENDPOINT",
                    "http://hyperdx:4318/v1/traces",
                )
            )
        )
    )
    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app, server_request_hook=None)
    SQLAlchemyInstrumentor().instrument()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    publisher = EventPublisher(settings.RABBITMQ_URL)
    await publisher.connect()
    app.state.event_publisher = publisher

    persona = PersonaClient()
    app.state.persona_client = persona

    async def _kyc_webhook_handler(payload: dict) -> None:
        from application.use_cases.process_kyc_webhook import ProcessKYCWebhook
        from infrastructure.repositories.kyc_repository_impl import SQLAlchemyKYCRepository

        async with AsyncSessionFactory() as session:
            try:
                use_case = ProcessKYCWebhook(
                    kyc_repo=SQLAlchemyKYCRepository(session),
                    event_publisher=publisher,
                )
                await use_case.execute(payload)
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    consumer = KYCWebhookConsumer(settings.RABBITMQ_URL)
    await consumer.start(_kyc_webhook_handler)
    app.state.kyc_consumer = consumer

    yield

    await consumer.stop()
    await publisher.disconnect()
    await engine.dispose()


app = FastAPI(
    title="User Service",
    version="1.0.0",
    description="User profiles and KYC verification via Persona",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

setup_telemetry(app, os.getenv("OTEL_SERVICE_NAME", "user-service"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(profile_router, prefix="/profile", tags=["Profile"])
app.include_router(kyc_router, prefix="/kyc", tags=["KYC"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "service": "user-service"}


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
