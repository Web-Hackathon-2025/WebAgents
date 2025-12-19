"""Pytest configuration and shared fixtures."""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient

from app.main import app
from app.db.client import get_db, Base
from app.core.config import settings
from app.core.security.password import hash_password
from app.db.models import User, CustomerProfile, ProviderProfile, ServiceCategory, Service


# Test database URL (use in-memory SQLite for speed, or separate test DB)
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/karigar_test"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.
    Creates all tables before tests and drops them after.
    """
    # Create engine
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()
    
    # Cleanup
    await engine.dispose()


@pytest.fixture
async def client(test_db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test HTTP client."""
    
    async def override_get_db():
        yield test_db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_customer(test_db: AsyncSession) -> User:
    """Create a test customer user."""
    user = User(
        email="testcustomer@test.com",
        password_hash=hash_password("Test@123"),
        phone="+923001111111",
        role="customer",
        is_active=True,
        is_verified=True
    )
    test_db.add(user)
    await test_db.flush()
    
    profile = CustomerProfile(
        user_id=user.id,
        full_name="Test Customer",
        address="123 Test St",
        latitude=24.8607,
        longitude=67.0011
    )
    test_db.add(profile)
    await test_db.commit()
    await test_db.refresh(user)
    
    return user


@pytest.fixture
async def test_provider(test_db: AsyncSession) -> User:
    """Create a test provider user."""
    user = User(
        email="testprovider@test.com",
        password_hash=hash_password("Test@123"),
        phone="+923002222222",
        role="provider",
        is_active=True,
        is_verified=True
    )
    test_db.add(user)
    await test_db.flush()
    
    profile = ProviderProfile(
        user_id=user.id,
        business_name="Test Provider",
        business_type="individual",
        description="Test provider",
        address="456 Test Ave",
        latitude=24.8707,
        longitude=67.0111,
        is_verified=True,
        rating=4.5
    )
    test_db.add(profile)
    await test_db.commit()
    await test_db.refresh(user)
    
    return user


@pytest.fixture
async def test_admin(test_db: AsyncSession) -> User:
    """Create a test admin user."""
    user = User(
        email="testadmin@test.com",
        password_hash=hash_password("Admin@123"),
        phone="+923003333333",
        role="admin",
        is_active=True,
        is_verified=True
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    return user


@pytest.fixture
async def test_service(test_db: AsyncSession, test_provider: User) -> Service:
    """Create a test service."""
    # First create a category
    category = ServiceCategory(
        name="Plumbing",
        description="Plumbing services"
    )
    test_db.add(category)
    await test_db.flush()
    
    # Get provider profile
    from sqlalchemy import select
    result = await test_db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == test_provider.id)
    )
    provider_profile = result.scalar_one()
    
    # Create service
    service = Service(
        provider_id=provider_profile.id,
        category_id=category.id,
        name="Pipe Repair",
        description="Professional pipe repair",
        base_price=1000.00,
        price_type="fixed",
        duration_minutes=60,
        is_available=True
    )
    test_db.add(service)
    await test_db.commit()
    await test_db.refresh(service)
    
    return service


@pytest.fixture
async def auth_headers_customer(client: AsyncClient, test_customer: User) -> dict:
    """Get authentication headers for customer."""
    response = await client.post(
        "/auth/login",
        json={
            "email": test_customer.email,
            "password": "Test@123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def auth_headers_provider(client: AsyncClient, test_provider: User) -> dict:
    """Get authentication headers for provider."""
    response = await client.post(
        "/auth/login",
        json={
            "email": test_provider.email,
            "password": "Test@123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def auth_headers_admin(client: AsyncClient, test_admin: User) -> dict:
    """Get authentication headers for admin."""
    response = await client.post(
        "/auth/login",
        json={
            "email": test_admin.email,
            "password": "Admin@123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_gemini_client():
    """Mock Gemini/OpenAI client for AI agent tests."""
    mock_client = AsyncMock()
    
    # Mock successful completion
    mock_completion = MagicMock()
    mock_completion.choices = [
        MagicMock(message=MagicMock(content='{"score": 85, "reasoning": "Good match"}'))
    ]
    mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
    
    return mock_client


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.ping = AsyncMock(return_value=True)
    return mock
