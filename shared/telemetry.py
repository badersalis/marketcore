import logging
from typing import Optional

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def _init_providers(trace_endpoint: str, service_name: str) -> None:
    resource = Resource.create({SERVICE_NAME: service_name})

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=trace_endpoint))
    )
    trace.set_tracer_provider(tracer_provider)

    log_endpoint = trace_endpoint.replace("/v1/traces", "/v1/logs")
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(endpoint=log_endpoint))
    )
    set_logger_provider(logger_provider)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider))

    # Uvicorn overrides propagation on its own loggers in some configurations;
    # force them back so all access/error logs reach the OTEL handler on root.
    for _name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        logging.getLogger(_name).propagate = True


def setup_telemetry(
    app,
    trace_endpoint: str,
    service_name: str,
    *,
    instrument_sqlalchemy: bool = False,
    instrument_aio_pika: bool = False,
) -> None:
    """Wire OTLP trace + log export for FastAPI services.

    Derives the log endpoint from trace_endpoint by replacing /v1/traces
    with /v1/logs so both ship to the same collector (HyperDX).
    """
    _init_providers(trace_endpoint, service_name)

    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    FastAPIInstrumentor.instrument_app(app, server_request_hook=None)

    if instrument_sqlalchemy:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        SQLAlchemyInstrumentor().instrument()

    if instrument_aio_pika:
        from opentelemetry.instrumentation.aio_pika import AioPikaInstrumentor
        AioPikaInstrumentor().instrument()


def setup_worker_telemetry(trace_endpoint: str, service_name: str) -> None:
    """Wire OTLP trace + log export for non-FastAPI workers (ARQ, etc.)."""
    _init_providers(trace_endpoint, service_name)
