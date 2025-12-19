"""Dispute endpoints for users."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.security import get_current_user
from app.core.exceptions import NotFoundError, BadRequestError
from app.db.client import get_db
from app.db.models import User, Booking as BookingModel, CustomerProfile, ProviderProfile, Dispute
from app.domain.models import DisputeCreate

router = APIRouter(prefix="/api/v1/disputes", tags=["disputes"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_dispute(
    dispute_data: DisputeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a dispute for a booking."""
    # Get booking
    result = await db.execute(
        select(BookingModel).where(BookingModel.id == dispute_data.booking_id)
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise NotFoundError("Booking not found")
    
    # Check if user is involved in the booking
    customer_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    )
    customer = customer_result.scalar_one_or_none()
    
    provider_result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == current_user.id)
    )
    provider = provider_result.scalar_one_or_none()
    
    if current_user.role != "admin":
        if customer and booking.customer_id != customer.id:
            if not provider or booking.provider_id != provider.id:
                raise NotFoundError("Booking not found")
    
    # Check if dispute already exists
    existing_dispute = await db.execute(
        select(Dispute).where(Dispute.booking_id == dispute_data.booking_id)
    )
    if existing_dispute.scalar_one_or_none():
        raise BadRequestError("Dispute already exists for this booking")
    
    # Create dispute
    dispute = Dispute(
        booking_id=dispute_data.booking_id,
        raised_by=current_user.id,
        dispute_type=dispute_data.dispute_type,
        description=dispute_data.description,
        evidence=dispute_data.evidence or []
    )
    db.add(dispute)
    
    # Update booking status
    booking.status = "disputed"
    
    await db.commit()
    await db.refresh(dispute)
    
    # Notify the other party
    from app.utils.notifications import create_notification
    
    if customer and booking.customer_id == customer.id:
        # Customer raised dispute, notify provider
        await create_notification(
            db=db,
            user_id=booking.provider.user_id,
            notification_type="system",
            title="Dispute Raised",
            message=f"A dispute has been raised for booking #{booking.id}",
            data={"dispute_id": str(dispute.id), "booking_id": str(booking.id)}
        )
    elif provider and booking.provider_id == provider.id:
        # Provider raised dispute, notify customer
        await create_notification(
            db=db,
            user_id=booking.customer.user_id,
            notification_type="system",
            title="Dispute Raised",
            message=f"A dispute has been raised for booking #{booking.id}",
            data={"dispute_id": str(dispute.id), "booking_id": str(booking.id)}
        )
    
    return {
        "id": dispute.id,
        "booking_id": dispute.booking_id,
        "status": dispute.status,
        "created_at": dispute.created_at
    }

