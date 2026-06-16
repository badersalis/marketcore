from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/market_user_db"
    RABBITMQ_URL: str = "amqp://rabbitmq:rabbitmq@localhost:5672/"
    SECRET_KEY: str = "secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    PERSONA_API_KEY: str = "persona_sandbox_placeholder"
    PERSONA_INQUIRY_TYPE_ID: str = "itmpl_placeholder"
    PERSONA_WEBHOOK_SECRET: str = "whsec_placeholder"

    model_config = {"env_file": ".env"}


settings = Settings()

__all__ = ["settings"]
