from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    AUTH_SERVICE_URL: str = "http://auth-service:8001"
    PRODUCT_SERVICE_URL: str = "http://product-service:8002"
    ORDER_SERVICE_URL: str = "http://order-service:8003"
    PAYMENT_SERVICE_URL: str = "http://payment-service:8004"
    NOTIFICATION_SERVICE_URL: str = "http://notification-service:8005"
    REDIS_URL: str = "redis://redis:6379/0"
    SECRET_KEY: str = "secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    RATE_LIMIT_PUBLIC: int = 100      # req/min per IP for public routes
    RATE_LIMIT_AUTHED: int = 300      # req/min per user for authenticated routes

    model_config = {"env_file": ".env"}


settings = Settings()

UPSTREAM_MAP = {
    "/auth": settings.AUTH_SERVICE_URL,
    "/products": settings.PRODUCT_SERVICE_URL,
    "/categories": settings.PRODUCT_SERVICE_URL,
    "/orders": settings.ORDER_SERVICE_URL,
    "/cart": settings.ORDER_SERVICE_URL,
    "/payments": settings.PAYMENT_SERVICE_URL,
}

PUBLIC_ROUTES = {
    ("POST", "/auth/register"),
    ("POST", "/auth/login"),
    ("POST", "/auth/refresh"),
    ("GET", "/health"),
    ("GET", "/docs"),
    ("GET", "/openapi.json"),
    ("GET", "/favicon.ico"),
}


def is_public_product_route(method: str, path: str) -> bool:
    if method != "GET":
        return False
    return path == "/products" or path.startswith("/products/") or path == "/categories" or path.startswith("/categories/")


__all__ = ["settings", "UPSTREAM_MAP", "PUBLIC_ROUTES", "is_public_product_route"]
