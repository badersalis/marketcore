import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdFilter, CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from prometheus_fastapi_instrumentator import Instrumentator

from core.config import settings
from infrastructure.cache.redis_client import create_redis_client
from infrastructure.messaging.event_publisher import EventPublisher
from infrastructure.messaging.payment_consumer import PaymentEventConsumer
from infrastructure.persistence.database import Base, engine
from presentation.routers.cart_router import router as cart_router
from presentation.routers.order_router import router as order_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s [%(correlation_id)s] %(name)s — %(message)s",
)
for _handler in logging.root.handlers:
    _handler.addFilter(CorrelationIdFilter(default_value="-"))


async def _payment_event_handler(event_type: str, body: dict) -> None:
    """Handle payment events to update order status."""
    from infrastructure.persistence.database import AsyncSessionFactory
    from infrastructure.repositories.order_repository_impl import SQLAlchemyOrderRepository
    from domain.value_objects.order_status import OrderStatus
    from shared.events.order_events import OrderPaymentConfirmed, OrderCancelled

    order_id = body.get("order_id")
    if not order_id:
        return

    async with AsyncSessionFactory() as session:
        order_repo = SQLAlchemyOrderRepository(session)
        publisher = app.state.event_publisher

        order = await order_repo.get_by_id(order_id)
        if not order:
            return

        if event_type == "payment.confirmed":
            try:
                order.transition_to(OrderStatus.CONFIRMED)
                await order_repo.update(order)
                await session.commit()
                await publisher.publish(
                    "order.events",
                    OrderPaymentConfirmed(
                        order_id=order.id,
                        payment_reference=body.get("payment_id", ""),
                    ),
                )
            except Exception as exc:
                logging.getLogger(__name__).error("Failed to confirm order %s: %s", order_id, exc)

        elif event_type == "payment.failed":
            try:
                order.cancel("Payment failed")
                await order_repo.update(order)
                await session.commit()
                await publisher.publish(
                    "order.events",
                    OrderCancelled(
                        order_id=order.id,
                        user_id=order.user_id,
                        reason="Payment failed",
                        refund_amount="0.00",
                    ),
                )
            except Exception as exc:
                logging.getLogger(__name__).error("Failed to cancel order %s: %s", order_id, exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    publisher = EventPublisher(settings.RABBITMQ_URL)
    await publisher.connect()
    app.state.event_publisher = publisher

    redis = create_redis_client()
    app.state.redis = redis

    consumer = PaymentEventConsumer(
        rabbitmq_url=settings.RABBITMQ_URL,
        order_handler=_payment_event_handler,
    )
    await consumer.start()
    app.state.payment_consumer = consumer

    yield

    await consumer.stop()
    await redis.aclose()
    await publisher.disconnect()
    await engine.dispose()


app = FastAPI(
    title="Order Service",
    version="1.0.0",
    description="Cart management, order lifecycle, and payment event integration.",
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

Instrumentator().instrument(app).expose(app, include_in_schema=False)

app.include_router(cart_router, prefix="/cart/items", tags=["Cart"])
app.include_router(order_router, prefix="/orders", tags=["Orders"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "service": "order-service"}


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
