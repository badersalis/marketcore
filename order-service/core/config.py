from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/market_order_db"
    RABBITMQ_URL: str = "amqp://rabbitmq:rabbitmq@localhost:5672/"
    REDIS_URL: str = "redis://localhost:6379/3"
    SECRET_KEY: str = "secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    PRODUCT_SERVICE_URL: str = "http://localhost:8002"
    OTEL_SERVICE_NAME: str = "order-service"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4318/v1/traces"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

__all__ = ["settings"]
