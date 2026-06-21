import logging

from asgi_correlation_id import correlation_id as _correlation_id_ctx

from core.config import settings
from infrastructure.email.resend_sender import ResendEmailSender
from infrastructure.email.templates import (
    payment_confirmed_email,
    payment_failed_email,
    product_published_email,
    verification_email,
    welcome_email,
)

logger = logging.getLogger(__name__)


def _bind_correlation_id(corr_id: str) -> None:
    _correlation_id_ctx.set(corr_id)


async def send_verification_email_job(
    ctx: dict, *, to: str, otp: str, correlation_id: str = "-"
) -> None:
    _bind_correlation_id(correlation_id)
    sender: ResendEmailSender = ctx["email_sender"]
    try:
        await sender.send(
            to=to,
            subject=f"{otp} is your Marketcore verification code",
            html=verification_email(otp),
        )
    except Exception as exc:
        if ctx["job_try"] < settings.ARQ_MAX_TRIES:
            raise
        logger.error("Giving up on verification email to %s after %d tries: %s", to, settings.ARQ_MAX_TRIES, exc)


async def send_welcome_email_job(
    ctx: dict, *, to: str, correlation_id: str = "-"
) -> None:
    _bind_correlation_id(correlation_id)
    sender: ResendEmailSender = ctx["email_sender"]
    try:
        await sender.send(
            to=to,
            subject="Welcome to Marketcore!",
            html=welcome_email(to),
        )
    except Exception as exc:
        if ctx["job_try"] < settings.ARQ_MAX_TRIES:
            raise
        logger.error("Giving up on welcome email to %s after %d tries: %s", to, settings.ARQ_MAX_TRIES, exc)


async def send_payment_confirmed_email_job(
    ctx: dict, *, to: str, order_id: str, amount: float, currency: str, correlation_id: str = "-"
) -> None:
    _bind_correlation_id(correlation_id)
    sender: ResendEmailSender = ctx["email_sender"]
    try:
        await sender.send(
            to=to,
            subject=f"Payment confirmed — Order {order_id}",
            html=payment_confirmed_email(order_id, amount, currency),
        )
    except Exception as exc:
        if ctx["job_try"] < settings.ARQ_MAX_TRIES:
            raise
        logger.error("Giving up on payment confirmed email to %s after %d tries: %s", to, settings.ARQ_MAX_TRIES, exc)


async def send_payment_failed_email_job(
    ctx: dict, *, to: str, order_id: str, reason: str, correlation_id: str = "-"
) -> None:
    _bind_correlation_id(correlation_id)
    sender: ResendEmailSender = ctx["email_sender"]
    try:
        await sender.send(
            to=to,
            subject=f"Payment failed — Order {order_id}",
            html=payment_failed_email(order_id, reason),
        )
    except Exception as exc:
        if ctx["job_try"] < settings.ARQ_MAX_TRIES:
            raise
        logger.error("Giving up on payment failed email to %s after %d tries: %s", to, settings.ARQ_MAX_TRIES, exc)


async def send_product_published_email_job(
    ctx: dict, *, to: str, product_id: str, product_name: str, correlation_id: str = "-"
) -> None:
    _bind_correlation_id(correlation_id)
    sender: ResendEmailSender = ctx["email_sender"]
    try:
        await sender.send(
            to=to,
            subject=f"Your product \"{product_name}\" is now live on Marketcore",
            html=product_published_email(product_name, product_id),
        )
    except Exception as exc:
        if ctx["job_try"] < settings.ARQ_MAX_TRIES:
            raise
        logger.error("Giving up on product-published email to %s after %d tries: %s", to, settings.ARQ_MAX_TRIES, exc)


__all__ = [
    "send_verification_email_job",
    "send_welcome_email_job",
    "send_payment_confirmed_email_job",
    "send_payment_failed_email_job",
    "send_product_published_email_job",
]
