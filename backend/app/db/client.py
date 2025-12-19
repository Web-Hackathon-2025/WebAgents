"""Database connection and session management."""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

from app.core.config import settings


def prepare_asyncpg_url(database_url: str) -> str:
    """
    Convert PostgreSQL URL to asyncpg-compatible format.
    Removes sslmode and channel_binding parameters and sets SSL via connect_args.
    """
    # Parse the URL
    parsed = urlparse(database_url)
    
    # Parse query parameters
    query_params = parse_qs(parsed.query)
    
    # Remove sslmode and channel_binding (asyncpg doesn't use these)
    query_params.pop('sslmode', None)
    query_params.pop('channel_binding', None)
    
    # Rebuild query string
    new_query = urlencode(query_params, doseq=True)
    
    # Reconstruct URL
    new_parsed = parsed._replace(query=new_query)
    new_url = urlunparse(new_parsed)
    
    # Convert to asyncpg format
    asyncpg_url = new_url.replace("postgresql://", "postgresql+asyncpg://")
    
    return asyncpg_url


# Prepare database URL for asyncpg
database_url = prepare_asyncpg_url(settings.DATABASE_URL)

# Create async engine with connection pooling
# For Neon, SSL is required - asyncpg needs it set explicitly
# Check if original URL had sslmode=require
ssl_required = 'sslmode=require' in settings.DATABASE_URL.lower()

connect_args = {}
if ssl_required:
    # For asyncpg with Neon, SSL is required
    # asyncpg accepts ssl=True or an SSL context
    import ssl
    # Use default SSL context for secure connection
    connect_args['ssl'] = ssl.create_default_context()

engine = create_async_engine(
    database_url,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    connect_args=connect_args if connect_args else {},
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

