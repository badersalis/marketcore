from pydantic_settings import BaseSettings

ARQ_QUEUE_NAME = "marketcore:email"


class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/4"
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "Marketcore <onboarding@resend.dev>"

    ARQ_MAX_JOBS: int = 10
    ARQ_JOB_TIMEOUT: int = 30
    ARQ_KEEP_RESULT: int = 3600
    ARQ_MAX_TRIES: int = 5

    OTEL_SERVICE_NAME: str = "worker"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4318/v1/traces"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

__all__ = ["ARQ_QUEUE_NAME", "settings"]
