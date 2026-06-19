import logging

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_telemetry(
    app: FastAPI,
    trace_endpoint: str,
    service_name: str,
    *,
    instrument_sqlalchemy: bool = False,
    instrument_aio_pika: bool = False,
) -> None:
    """Wire up OTLP trace + log export and auto-instrumentation.

    Derives the log endpoint from trace_endpoint by replacing /v1/traces
    with /v1/logs so both ship to the same collector (HyperDX).
    """
    resource = Resource.create({SERVICE_NAME: service_name})

    # ── Traces ────────────────────────────────────────────────────────────────
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=trace_endpoint))
    )
    trace.set_tracer_provider(tracer_provider)

    # ── Logs ──────────────────────────────────────────────────────────────────
    log_endpoint = trace_endpoint.replace("/v1/traces", "/v1/logs")
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(endpoint=log_endpoint))
    )
    set_logger_provider(logger_provider)
    logging.getLogger().addHandler(
        LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
    )

    # ── Auto-instrumentation ──────────────────────────────────────────────────
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    FastAPIInstrumentor.instrument_app(app, server_request_hook=None)

    if instrument_sqlalchemy:
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        SQLAlchemyInstrumentor().instrument()

    if instrument_aio_pika:
        from opentelemetry.instrumentation.aio_pika import AioPikaInstrumentor
        AioPikaInstrumentor().instrument()
