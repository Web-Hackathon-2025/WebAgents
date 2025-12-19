"""Main FastAPI application."""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import structlog
import logging
import sys

from app.core.config import settings
from app.core.redis_client import redis_client
from app.core.exceptions import KarigarException
from app.api import auth

# Configure structured logging
# Use console renderer for development, JSON for production
if settings.DEBUG:
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )
else:
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer()
        ]
    )

logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("=" * 60)
    logger.info("Starting Karigar Backend API")
    logger.info("=" * 60)
    
    # Log configuration status
    logger.info("Configuration Status:")
    logger.info(f"  Environment: {settings.ENVIRONMENT}")
    logger.info(f"  Debug Mode: {settings.DEBUG}")
    logger.info(f"  Frontend URL: {settings.FRONTEND_URL}")
    logger.info(f"  API Base URL: {settings.API_BASE_URL}")
    
    # Check OpenAI API Key
    logger.info("OpenAI Configuration:")
    if settings.OPENAI_API_KEY:
        masked_key = f"{settings.OPENAI_API_KEY[:7]}...{settings.OPENAI_API_KEY[-4:]}" if len(settings.OPENAI_API_KEY) > 11 else "***"
        logger.info(f"  ✓ API Key: {masked_key}")
        logger.info(f"  ✓ Model: {settings.OPENAI_MODEL}")
    else:
        logger.warning("  ✗ OpenAI API Key not configured!")
    
    # Check Database Connection
    logger.info("Database Configuration:")
    # Mask database URL for security
    db_url_display = settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'
    logger.info(f"  Database Host: {db_url_display.split('/')[0] if '/' in db_url_display else db_url_display}")
    try:
        from app.db.client import engine
        from sqlalchemy import text
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("  ✓ Database connection: SUCCESS")
        # Check PostGIS extension
        try:
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT PostGIS_version()"))
                version = result.fetchone()
                if version:
                    logger.info(f"  ✓ PostGIS extension: Available (version: {version[0]})")
                else:
                    logger.warning("  ⚠ PostGIS extension: Not available")
        except Exception:
            logger.warning("  ⚠ PostGIS extension: Not available (optional)")
    except Exception as e:
        logger.error(f"  ✗ Database connection: FAILED - {str(e)}")
        logger.error(f"  Error details: {type(e).__name__}")
    
    # Check Redis Connection
    logger.info("Redis Configuration:")
    logger.info(f"  Redis URL: {settings.REDIS_URL}")
    try:
        await redis_client.connect()
        if redis_client.client:
            await redis_client.client.ping()
            logger.info("  ✓ Redis connection: SUCCESS")
            logger.info("  ✓ Redis client: Connected")
        else:
            logger.warning("  ✗ Redis client: Not initialized")
    except Exception as e:
        logger.error(f"  ✗ Redis connection: FAILED - {str(e)}")
        logger.warning("  Note: Some features may not work without Redis")
    
    # Check Google Maps API (Optional)
    if settings.GOOGLE_MAPS_API_KEY:
        masked_key = f"{settings.GOOGLE_MAPS_API_KEY[:7]}...{settings.GOOGLE_MAPS_API_KEY[-4:]}" if len(settings.GOOGLE_MAPS_API_KEY) > 11 else "***"
        logger.info(f"  ✓ Google Maps API Key: {masked_key}")
    else:
        logger.info("  ⚠ Google Maps API Key: Not configured (optional)")
    
    # Check JWT Configuration
    logger.info("JWT Configuration:")
    if settings.JWT_SECRET_KEY:
        masked_secret = f"{settings.JWT_SECRET_KEY[:8]}...{settings.JWT_SECRET_KEY[-4:]}" if len(settings.JWT_SECRET_KEY) > 12 else "***"
        logger.info(f"  ✓ Secret Key: {masked_secret}")
        logger.info(f"  ✓ Algorithm: {settings.JWT_ALGORITHM}")
        logger.info(f"  ✓ Access Token Expiry: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
        logger.info(f"  ✓ Refresh Token Expiry: {settings.REFRESH_TOKEN_EXPIRE_MINUTES} minutes")
    else:
        logger.error("  ✗ JWT Secret Key: Not configured!")
    
    logger.info("=" * 60)
    logger.info("Server starting...")
    logger.info("=" * 60)
    
    yield
    
    # Shutdown
    logger.info("=" * 60)
    logger.info("Shutting down Karigar Backend API")
    logger.info("=" * 60)
    try:
        await redis_client.disconnect()
        logger.info("  ✓ Redis disconnected")
    except Exception as e:
        logger.error(f"  ✗ Error disconnecting Redis: {str(e)}")
    logger.info("=" * 60)


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
from app.api import bookings, customers, providers, search, reviews, admin, notifications, disputes
app.include_router(bookings.router)
app.include_router(customers.router)
app.include_router(providers.router)
app.include_router(search.router)
app.include_router(reviews.router)
app.include_router(admin.router)
app.include_router(notifications.router)
app.include_router(disputes.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Karigar Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }

