"""Shop Hub API — FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import close_db, connect_db
from app.core.redis import close_redis, connect_redis
from app.services.cloudinary_service import configure_cloudinary
from app.services.openai_service import init_openai
from app.services.seed_service import seed_products_if_empty

from app.api.routes import (
    auth,
    products,
    cart,
    orders,
    wishlist,
    reviews,
    recommendations,
    admin,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    await connect_db()
    await connect_redis()
    configure_cloudinary()
    init_openai()
    await seed_products_if_empty()
    yield
    await close_redis()
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow the frontend origin (must be added before other middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers under /api/v1
for router in [
    auth.router,
    products.router,
    cart.router,
    orders.router,
    wishlist.router,
    reviews.router,
    recommendations.router,
    admin.router,
]:
    app.include_router(router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.APP_NAME}
