from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/product_db"
    RABBITMQ_URL: str = "amqp://rabbitmq:rabbitmq@localhost:5672/"
    REDIS_URL: str = "redis://localhost:6379/2"
    SECRET_KEY: str = "secret-key-change-in-production"
    ALGORITHM: str = "HS256"

    model_config = {"env_file": ".env"}


settings = Settings()

__all__ = ["settings"]
