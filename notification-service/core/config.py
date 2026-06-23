from pydantic_settings import BaseSettings

ARQ_QUEUE_NAME = "marketcore:email"


class Settings(BaseSettings):
    RABBITMQ_URL: str = "amqp://rabbitmq:rabbitmq@localhost:5672/"
    REDIS_URL: str = "redis://localhost:6379/4"
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "Marketcore <onboarding@resend.dev>"

    # ARQ worker
    ARQ_MAX_JOBS: int = 10
    ARQ_JOB_TIMEOUT: int = 30        # seconds before a job is considered hung
    ARQ_KEEP_RESULT: int = 3600      # seconds to keep job results in Redis
    ARQ_MAX_TRIES: int = 5
    OTEL_SERVICE_NAME: str = "notification-service"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4318/v1/traces"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

__all__ = ["ARQ_QUEUE_NAME", "settings"]
