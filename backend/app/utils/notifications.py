"""Notification utilities."""
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.db.models import Notification, User


async def create_notification(
    db: AsyncSession,
    user_id: UUID,
    notification_type: str,
    title: str,
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> Notification:
    """Create a new notification."""
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        title=title,
        message=message,
        data=data or {}
    )
    db.add(notification)
    await db.flush()
    return notification


async def get_unread_count(db: AsyncSession, user_id: UUID) -> int:
    """Get count of unread notifications for a user."""
    result = await db.execute(
        select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
    )
    notifications = result.scalars().all()
    return len(notifications)

