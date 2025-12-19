"""Permission decorators and dependencies for role-based access control."""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security.jwt import verify_token
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.db.client import get_db
from app.db.models import User
from sqlalchemy import select


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    token = credentials.credentials
    payload = verify_token(token, token_type="access")
    
    if not payload:
        raise UnauthorizedError("Invalid or expired token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid token payload")
    
    # Check if token is revoked (would check Redis here)
    # For now, we'll skip this check but it should be implemented
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise UnauthorizedError("User not found")
    
    if not user.is_active:
        raise ForbiddenError("User account is inactive")
    
    return user


async def require_customer(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require the user to be a customer."""
    if current_user.role != "customer":
        raise ForbiddenError("Customer access required")
    return current_user


async def require_provider(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require the user to be a provider."""
    if current_user.role != "provider":
        raise ForbiddenError("Provider access required")
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require the user to be an admin."""
    if current_user.role != "admin":
        raise ForbiddenError("Admin access required")
    return current_user


async def require_provider_or_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """Require the user to be a provider or admin."""
    if current_user.role not in ["provider", "admin"]:
        raise ForbiddenError("Provider or admin access required")
    return current_user

