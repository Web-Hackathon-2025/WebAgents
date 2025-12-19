"""Booking endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.security import get_current_user, require_customer, require_provider
from app.core.exceptions import NotFoundError, BadRequestError
from app.db.client import get_db
from app.db.models import User, Booking as BookingModel, CustomerProfile, ProviderProfile, Service
from app.domain.models import BookingRequest, Booking, BookingUpdate
from app.services.matching import MatchingService
from app.services.scheduling import SchedulingService
from app.utils.notifications import create_notification

router = APIRouter(prefix="/api/v1/bookings", tags=["bookings"])

matching_service = MatchingService()
scheduling_service = SchedulingService()


@router.post("/request", response_model=Booking, status_code=status.HTTP_201_CREATED)
async def create_booking_request(
    request_data: BookingRequest,
    current_user: User = Depends(require_customer),
    db: AsyncSession = Depends(get_db)
):
    """Create a booking request."""
    # Get customer profile
    customer_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    )
    customer = customer_result.scalar_one_or_none()
    
    if not customer:
        raise NotFoundError("Customer profile not found")
    
    # Get service
    service_result = await db.execute(
        select(Service).where(Service.id == request_data.service_id)
    )
    service = service_result.scalar_one_or_none()
    
    if not service:
        raise NotFoundError("Service not found")
    
    # If provider not specified, use matching agent
    provider_id = request_data.provider_id
    match_score = None
    match_reasoning = None
    
    if not provider_id:
        # Use matching service
        matches = await matching_service.find_matching_providers(
            db=db,
            service_id=str(request_data.service_id),
            customer_lat=customer.latitude or 0,
            customer_lng=customer.longitude or 0,
            preferred_date=request_data.preferred_date.isoformat() if request_data.preferred_date else None,
            budget=None
        )
        
        if not matches:
            raise BadRequestError("No matching providers found")
        
        # Use top match
        top_match = matches[0]
        provider_id = UUID(top_match["provider_id"])
        match_score = top_match["match_score"]
        match_reasoning = top_match["reasoning"]
    
    # Get provider
    provider_result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.id == provider_id)
    )
    provider = provider_result.scalar_one_or_none()
    
    if not provider:
        raise NotFoundError("Provider not found")
    
    # Create booking
    booking = BookingModel(
        customer_id=customer.id,
        provider_id=provider_id,
        service_id=request_data.service_id,
        status="requested",
        request_description=request_data.request_description,
        service_address=request_data.service_address,
        service_latitude=request_data.service_latitude,
        service_longitude=request_data.service_longitude,
        preferred_date=request_data.preferred_date,
        preferred_time_start=request_data.preferred_time_start,
        preferred_time_end=request_data.preferred_time_end,
        ai_match_score=match_score,
        ai_match_reasoning=match_reasoning
    )
    db.add(booking)
    await db.flush()
    
    # Notify provider
    await create_notification(
        db=db,
        user_id=provider.user_id,
        notification_type="booking_request",
        title="New Booking Request",
        message=f"You have a new booking request for {service.title}",
        data={"booking_id": str(booking.id)}
    )
    
    await db.commit()
    await db.refresh(booking)
    
    return booking


@router.get("/{booking_id}", response_model=Booking)
async def get_booking(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get booking details."""
    result = await db.execute(
        select(BookingModel).where(BookingModel.id == booking_id)
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise NotFoundError("Booking not found")
    
    # Check access
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
    
    return booking


@router.patch("/{booking_id}/accept", response_model=Booking)
async def accept_booking(
    booking_id: UUID,
    current_user: User = Depends(require_provider),
    db: AsyncSession = Depends(get_db)
):
    """Provider accepts a booking request."""
    # Get provider
    provider_result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == current_user.id)
    )
    provider = provider_result.scalar_one_or_none()
    
    if not provider:
        raise NotFoundError("Provider profile not found")
    
    # Get booking
    result = await db.execute(
        select(Booking).where(
            BookingModel.id == booking_id,
            BookingModel.provider_id == provider.id
        )
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise NotFoundError("Booking not found")
    
    if booking.status != "requested":
        raise BadRequestError("Booking cannot be accepted in current status")
    
    booking.status = "accepted"
    await db.commit()
    await db.refresh(booking)
    
    # Notify customer
    await create_notification(
        db=db,
        user_id=booking.customer.user_id,
        notification_type="booking_accepted",
        title="Booking Accepted",
        message=f"Your booking request has been accepted",
        data={"booking_id": str(booking.id)}
    )
    
    return booking


@router.patch("/{booking_id}/reject", response_model=Booking)
async def reject_booking(
    booking_id: UUID,
    reason: str,
    current_user: User = Depends(require_provider),
    db: AsyncSession = Depends(get_db)
):
    """Provider rejects a booking request."""
    # Get provider
    provider_result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == current_user.id)
    )
    provider = provider_result.scalar_one_or_none()
    
    if not provider:
        raise NotFoundError("Provider profile not found")
    
    # Get booking
    result = await db.execute(
        select(Booking).where(
            BookingModel.id == booking_id,
            BookingModel.provider_id == provider.id
        )
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise NotFoundError("Booking not found")
    
    if booking.status != "requested":
        raise BadRequestError("Booking cannot be rejected in current status")
    
    booking.status = "cancelled"
    booking.cancellation_reason = reason
    booking.cancelled_by = "provider"
    await db.commit()
    await db.refresh(booking)
    
    # Notify customer
    await create_notification(
        db=db,
        user_id=booking.customer.user_id,
        notification_type="booking_cancelled",
        title="Booking Rejected",
        message=f"Your booking request has been rejected: {reason}",
        data={"booking_id": str(booking.id)}
    )
    
    return booking

