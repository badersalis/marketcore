import logging

from arq.connections import RedisSettings
from asgi_correlation_id import CorrelationIdFilter

from core.config import ARQ_QUEUE_NAME, settings
from infrastructure.email.resend_sender import ResendEmailSender
from infrastructure.jobs.email_jobs import (
    send_payment_confirmed_email_job,
    send_payment_failed_email_job,
    send_verification_email_job,
    send_welcome_email_job,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s [%(correlation_id)s] %(name)s — %(message)s",
)
for _handler in logging.root.handlers:
    _handler.addFilter(CorrelationIdFilter(default_value="-"))


async def startup(ctx: dict) -> None:
    ctx["email_sender"] = ResendEmailSender()
    logging.getLogger(__name__).info("ARQ email worker started")


async def shutdown(ctx: dict) -> None:
    logging.getLogger(__name__).info("ARQ email worker stopped")


class WorkerSettings:
    functions = [
        send_verification_email_job,
        send_welcome_email_job,
        send_payment_confirmed_email_job,
        send_payment_failed_email_job,
    ]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    queue_name = ARQ_QUEUE_NAME
    max_jobs = settings.ARQ_MAX_JOBS
    job_timeout = settings.ARQ_JOB_TIMEOUT
    keep_result = settings.ARQ_KEEP_RESULT
