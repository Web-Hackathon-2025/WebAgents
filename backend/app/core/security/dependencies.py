"""Optional dependencies for authentication."""
from typing import Optional
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer
from app.db.models import User
from .permissions import get_current_user

security = HTTPBearer(auto_error=False)


async def get_optional_user(
    credentials: Optional[HTTPBearer] = Security(security)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise."""
    if not credentials:
        return None
    try:
        return await get_current_user(credentials=credentials)
    except Exception:
        return None

