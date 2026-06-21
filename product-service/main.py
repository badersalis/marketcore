import logging
import os
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdFilter, CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from core.config import settings
from shared.telemetry import setup_telemetry
from infrastructure.cache.product_cache import ProductCache
from infrastructure.messaging.event_publisher import EventPublisher
from infrastructure.messaging.product_event_consumer import ProductEventConsumer
from infrastructure.persistence.database import AsyncSessionFactory, Base, engine
from infrastructure.repositories.product_repository_impl import SQLAlchemyProductRepository
from presentation.routers.category_router import router as category_router
from presentation.routers.product_router import router as product_router
from presentation.routers.sku_router import router as sku_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s [%(correlation_id)s] %(name)s — %(message)s",
    force=True,
)



async def _product_event_handler(event_type: str, body: dict) -> None:
    from application.use_cases.publish_product import PublishProduct
    from application.use_cases.reject_product import RejectProduct

    async with AsyncSessionFactory() as session:
        repo = SQLAlchemyProductRepository(session)
        publisher = app.state.event_publisher
        cache = app.state.product_cache

        if event_type == "product.images_ready":
            await PublishProduct(repo, publisher, cache).execute(
                product_id=body.get("product_id", ""),
                cdn_urls=body.get("cdn_urls", []),
            )
            await session.commit()

        elif event_type == "product.images_failed":
            await RejectProduct(repo).execute(
                product_id=body.get("product_id", ""),
                reason=body.get("reason", ""),
            )
            await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    publisher = EventPublisher(settings.RABBITMQ_URL)
    await publisher.connect()
    app.state.event_publisher = publisher

    cache = ProductCache(settings.REDIS_URL)
    await cache.connect()
    app.state.product_cache = cache

    consumer = ProductEventConsumer(settings.RABBITMQ_URL, handler=_product_event_handler)
    await consumer.start()
    app.state.product_consumer = consumer

    yield

    await consumer.stop()
    await cache.close()
    await publisher.disconnect()
    await engine.dispose()


app = FastAPI(
    title="Product Service",
    version="1.0.0",
    description="Product catalogue microservice",
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

app.include_router(category_router, prefix="/categories", tags=["Categories"])
app.include_router(product_router, prefix="/products", tags=["Products"])
app.include_router(sku_router, prefix="/products/{product_id}/skus", tags=["SKUs"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "service": "product-service"}


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
