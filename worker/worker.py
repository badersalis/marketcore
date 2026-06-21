import logging

from arq.connections import RedisSettings
from asgi_correlation_id import CorrelationIdFilter

from core.config import ARQ_QUEUE_NAME, settings
from infrastructure.email.resend_sender import ResendEmailSender
from infrastructure.image.processor import ImageProcessor
from infrastructure.image.storage import LocalStorageClient
from infrastructure.jobs.email_jobs import (
    send_payment_confirmed_email_job,
    send_payment_failed_email_job,
    send_verification_email_job,
    send_welcome_email_job,
)
from infrastructure.jobs.image_jobs import process_product_images_job
from infrastructure.messaging.consumer import ProductEventConsumer
from infrastructure.messaging.publisher import EventPublisher
from shared.telemetry import setup_worker_telemetry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s [%(correlation_id)s] %(name)s — %(message)s",
    force=True,
)
for _handler in logging.root.handlers:
    _handler.addFilter(CorrelationIdFilter(default_value="-"))

setup_worker_telemetry(settings.OTEL_EXPORTER_OTLP_ENDPOINT, settings.OTEL_SERVICE_NAME)

logger = logging.getLogger(__name__)


async def startup(ctx: dict) -> None:
    ctx["email_sender"] = ResendEmailSender()
    ctx["image_processor"] = ImageProcessor()
    ctx["storage_client"] = LocalStorageClient(settings.IMAGE_STORAGE_DIR)
    ctx["_max_tries"] = settings.ARQ_MAX_TRIES

    publisher = EventPublisher(settings.RABBITMQ_URL)
    await publisher.connect()
    ctx["event_publisher"] = publisher

    consumer = ProductEventConsumer(settings.RABBITMQ_URL, arq_pool=ctx["redis"])
    await consumer.start()
    ctx["product_consumer"] = consumer

    logger.info("Worker started")


async def shutdown(ctx: dict) -> None:
    if consumer := ctx.get("product_consumer"):
        await consumer.stop()
    if publisher := ctx.get("event_publisher"):
        await publisher.disconnect()
    logger.info("Worker stopped")


class WorkerSettings:
    functions = [
        send_verification_email_job,
        send_welcome_email_job,
        send_payment_confirmed_email_job,
        send_payment_failed_email_job,
        process_product_images_job,
    ]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    queue_name = ARQ_QUEUE_NAME
    max_jobs = settings.ARQ_MAX_JOBS
    job_timeout = settings.ARQ_JOB_TIMEOUT
    keep_result = settings.ARQ_KEEP_RESULT
    max_tries = settings.ARQ_MAX_TRIES
