from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from infrastructure.messaging.event_publisher import EventPublisher
from infrastructure.persistence.database import Base, engine
from presentation.routers.auth_router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    publisher = EventPublisher(settings.RABBITMQ_URL)
    await publisher.connect()
    app.state.event_publisher = publisher

    yield

    await publisher.disconnect()
    await engine.dispose()


app = FastAPI(
    title="Auth Service",
    version="1.0.0",
    description="Authentication and authorization microservice",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "service": "auth-service"}
