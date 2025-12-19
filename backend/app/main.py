"""Main FastAPI application."""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import structlog

from app.core.config import settings
from app.core.redis_client import redis_client
from app.core.exceptions import KarigarException
from app.api import auth

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Karigar backend")
    await redis_client.connect()
    logger.info("Redis connected")
    yield
    # Shutdown
    logger.info("Shutting down Karigar backend")
    await redis_client.disconnect()
    logger.info("Redis disconnected")


app = FastAPI(
    title="Karigar Backend API",
    description="Hyperlocal Services Marketplace Backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL] if settings.FRONTEND_URL else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(KarigarException)
async def karigar_exception_handler(request: Request, exc: KarigarException):
    """Handle custom exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy", "service": "karigar-backend"}


@app.get("/health/db")
async def db_health_check():
    """Database health check."""
    try:
        from app.db.client import engine
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "database": "disconnected", "error": str(e)}
        )


@app.get("/health/redis")
async def redis_health_check():
    """Redis health check."""
    try:
        redis = await redis_client.client
        if redis:
            await redis.ping()
            return {"status": "healthy", "redis": "connected"}
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "redis": "not connected"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "redis": "error", "error": str(e)}
        )


# Include routers
app.include_router(auth.router)

# Import and include other routers
from app.api import bookings, customers, providers, search, reviews
app.include_router(bookings.router)
app.include_router(customers.router)
app.include_router(providers.router)
app.include_router(search.router)
app.include_router(reviews.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Karigar Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }

