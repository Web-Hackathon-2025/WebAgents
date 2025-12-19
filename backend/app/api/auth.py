"""Authentication endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
    verify_password,
    get_password_hash,
    get_current_user,
)
from app.core.redis_client import get_redis
from app.core.exceptions import UnauthorizedError, ConflictError, BadRequestError
from app.db.client import get_db
from app.db.models import User, CustomerProfile, ProviderProfile
from app.domain.models import (
    UserCreate,
    UserLogin,
    UserProfile,
    TokenResponse,
    TokenRefresh,
    CustomerProfileCreate,
    ProviderProfileCreate,
)

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/register/customer", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_customer(
    user_data: UserCreate,
    profile_data: CustomerProfileCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new customer."""
    # Check if email exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise ConflictError("Email already registered")
    
    # Check if phone exists
    if user_data.phone:
        result = await db.execute(select(User).where(User.phone == user_data.phone))
        if result.scalar_one_or_none():
            raise ConflictError("Phone number already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        phone=user_data.phone,
        role="customer",
        is_active=True,
        is_verified=False
    )
    db.add(user)
    await db.flush()
    
    # Create customer profile
    profile = CustomerProfile(
        user_id=user.id,
        full_name=profile_data.full_name,
        address=profile_data.address,
        latitude=profile_data.latitude,
        longitude=profile_data.longitude,
        city=profile_data.city,
        postal_code=profile_data.postal_code,
        preferred_language=profile_data.preferred_language
    )
    db.add(profile)
    await db.commit()
    
    # Generate tokens
    token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
    access_token, access_jti = create_access_token(token_data)
    refresh_token, refresh_jti = create_refresh_token(token_data)
    
    # Store refresh token in Redis
    redis = await get_redis()
    await redis.set(f"auth:refresh:{refresh_jti}", str(user.id), ex=604800)  # 7 days
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/register/provider", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_provider(
    user_data: UserCreate,
    profile_data: ProviderProfileCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new provider."""
    # Check if email exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise ConflictError("Email already registered")
    
    # Check if phone exists
    if user_data.phone:
        result = await db.execute(select(User).where(User.phone == user_data.phone))
        if result.scalar_one_or_none():
            raise ConflictError("Phone number already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        phone=user_data.phone,
        role="provider",
        is_active=True,
        is_verified=False
    )
    db.add(user)
    await db.flush()
    
    # Create provider profile
    from geoalchemy2 import WKTElement
    location = WKTElement(f"POINT({profile_data.longitude} {profile_data.latitude})", srid=4326)
    
    profile = ProviderProfile(
        user_id=user.id,
        business_name=profile_data.business_name,
        full_name=profile_data.full_name,
        bio=profile_data.bio,
        address=profile_data.address,
        latitude=profile_data.latitude,
        longitude=profile_data.longitude,
        location=location,
        city=profile_data.city,
        postal_code=profile_data.postal_code,
        service_radius_km=profile_data.service_radius_km,
        status="pending"
    )
    db.add(profile)
    await db.commit()
    
    # Generate tokens
    token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
    access_token, access_jti = create_access_token(token_data)
    refresh_token, refresh_jti = create_refresh_token(token_data)
    
    # Store refresh token in Redis
    redis = await get_redis()
    await redis.set(f"auth:refresh:{refresh_jti}", str(user.id), ex=604800)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login user."""
    # Find user
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")
    
    if not user.is_active:
        raise UnauthorizedError("Account is inactive")
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Generate tokens
    token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
    access_token, access_jti = create_access_token(token_data)
    refresh_token, refresh_jti = create_refresh_token(token_data)
    
    # Store refresh token in Redis
    redis = await get_redis()
    await redis.set(f"auth:refresh:{refresh_jti}", str(user.id), ex=604800)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token."""
    # Verify refresh token
    payload = verify_token(token_data.refresh_token, token_type="refresh")
    if not payload:
        raise UnauthorizedError("Invalid refresh token")
    
    # Check if token is revoked
    jti = payload.get("jti")
    redis = await get_redis()
    if not await redis.exists(f"auth:refresh:{jti}"):
        raise UnauthorizedError("Refresh token revoked")
    
    # Get user
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive")
    
    # Generate new tokens
    token_data_dict = {"sub": str(user.id), "email": user.email, "role": user.role}
    access_token, access_jti = create_access_token(token_data_dict)
    refresh_token, refresh_jti = create_refresh_token(token_data_dict)
    
    # Revoke old refresh token and store new one
    await redis.delete(f"auth:refresh:{jti}")
    await redis.set(f"auth:refresh:{refresh_jti}", str(user.id), ex=604800)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout user (revoke refresh tokens)."""
    # In a real implementation, we would revoke all refresh tokens for this user
    # For now, this is a placeholder
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile."""
    return UserProfile.model_validate(current_user)

