from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.persistence.database import Base, engine
from presentation.routers.category_router import router as category_router
from presentation.routers.product_router import router as product_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    title="Product Service",
    version="1.0.0",
    description="Product catalogue microservice",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(category_router, prefix="/categories", tags=["Categories"])
app.include_router(product_router, prefix="/products", tags=["Products"])


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "service": "product-service"}
