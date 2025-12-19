"""Booking endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from app.core.security import get_current_user, require_customer, require_provider
from app.core.exceptions import NotFoundError, BadRequestError
from app.db.client import get_db
from app.db.models import User, Booking as BookingModel, CustomerProfile, ProviderProfile, Service
from app.domain.models import BookingRequest, Booking, BookingUpdate
from datetime import datetime
from decimal import Decimal
from typing import Optional
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
        select(BookingModel).where(
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
        select(BookingModel).where(
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


@router.post("/{booking_id}/schedule", response_model=Booking)
async def schedule_booking(
    booking_id: UUID,
    scheduled_datetime: datetime,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Schedule a confirmed booking."""
    # Get booking
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
    
    if booking.status != "accepted":
        raise BadRequestError("Booking must be accepted before scheduling")
    
    # Use scheduling agent to validate time slot
    slots = await scheduling_service.get_available_slots(
        db=db,
        provider_id=str(booking.provider_id),
        preferred_date=scheduled_datetime.date(),
        service_duration_minutes=booking.estimated_duration_minutes or 120,
        booking_id=str(booking.id)
    )
    
    # Check if scheduled time is in available slots
    scheduled_time_str = scheduled_datetime.isoformat()
    available_times = [slot.get("start_datetime") for slot in slots.get("suggested_slots", [])]
    
    if available_times and scheduled_time_str not in available_times:
        raise BadRequestError("Selected time slot is not available")
    
    booking.status = "scheduled"
    booking.scheduled_datetime = scheduled_datetime
    
    await db.commit()
    await db.refresh(booking)
    
    # Notify both parties
    await create_notification(
        db=db,
        user_id=booking.customer.user_id,
        notification_type="booking_accepted",
        title="Booking Scheduled",
        message=f"Your booking has been scheduled for {scheduled_datetime.strftime('%Y-%m-%d %H:%M')}",
        data={"booking_id": str(booking.id)}
    )
    
    await create_notification(
        db=db,
        user_id=booking.provider.user_id,
        notification_type="booking_accepted",
        title="Booking Scheduled",
        message=f"You have a booking scheduled for {scheduled_datetime.strftime('%Y-%m-%d %H:%M')}",
        data={"booking_id": str(booking.id)}
    )
    
    return booking


@router.post("/{booking_id}/start", response_model=Booking)
async def start_booking(
    booking_id: UUID,
    current_user: User = Depends(require_provider),
    db: AsyncSession = Depends(get_db)
):
    """Mark booking as in progress."""
    # Get provider
    provider_result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == current_user.id)
    )
    provider = provider_result.scalar_one_or_none()
    
    if not provider:
        raise NotFoundError("Provider profile not found")
    
    # Get booking
    result = await db.execute(
        select(BookingModel).where(
            BookingModel.id == booking_id,
            BookingModel.provider_id == provider.id
        )
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise NotFoundError("Booking not found")
    
    if booking.status != "scheduled":
        raise BadRequestError("Booking must be scheduled before starting")
    
    booking.status = "in_progress"
    await db.commit()
    await db.refresh(booking)
    
    # Notify customer
    await create_notification(
        db=db,
        user_id=booking.customer.user_id,
        notification_type="system",
        title="Service Started",
        message="Your service provider has started the service",
        data={"booking_id": str(booking.id)}
    )
    
    return booking


@router.post("/{booking_id}/complete", response_model=Booking)
async def complete_booking(
    booking_id: UUID,
    final_price: Optional[Decimal] = None,
    current_user: User = Depends(require_provider),
    db: AsyncSession = Depends(get_db)
):
    """Mark booking as completed."""
    # Get provider
    provider_result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == current_user.id)
    )
    provider = provider_result.scalar_one_or_none()
    
    if not provider:
        raise NotFoundError("Provider profile not found")
    
    # Get booking
    result = await db.execute(
        select(BookingModel).where(
            BookingModel.id == booking_id,
            BookingModel.provider_id == provider.id
        )
    )
    booking = result.scalar_one_or_none()
    
    if not booking:
        raise NotFoundError("Booking not found")
    
    if booking.status != "in_progress":
        raise BadRequestError("Booking must be in progress before completing")
    
    booking.status = "completed"
    booking.completed_at = datetime.utcnow()
    if final_price:
        booking.final_price = final_price
    
    # Update provider stats
    provider.total_bookings += 1
    # Recalculate completion rate
    completed_bookings = await db.execute(
        select(func.count(BookingModel.id)).where(
            BookingModel.provider_id == provider.id,
            BookingModel.status == "completed"
        )
    )
    total_accepted = await db.execute(
        select(func.count(BookingModel.id)).where(
            BookingModel.provider_id == provider.id,
            BookingModel.status.in_(["accepted", "scheduled", "in_progress", "completed"])
        )
    )
    if total_accepted.scalar() > 0:
        provider.completion_rate = (completed_bookings.scalar() / total_accepted.scalar()) * 100
    
    await db.commit()
    await db.refresh(booking)
    
    # Notify customer
    await create_notification(
        db=db,
        user_id=booking.customer.user_id,
        notification_type="booking_accepted",
        title="Service Completed",
        message="Your service has been completed. Please leave a review!",
        data={"booking_id": str(booking.id)}
    )
    
    return booking


@router.post("/{booking_id}/cancel", response_model=Booking)
async def cancel_booking(
    booking_id: UUID,
    reason: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a booking."""
    # Get booking
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
    
    cancelled_by_role = None
    if current_user.role == "admin":
        cancelled_by_role = "admin"
    elif customer and booking.customer_id == customer.id:
        cancelled_by_role = "customer"
    elif provider and booking.provider_id == provider.id:
        cancelled_by_role = "provider"
    else:
        raise NotFoundError("Booking not found")
    
    if booking.status in ["completed", "cancelled"]:
        raise BadRequestError(f"Booking cannot be cancelled in {booking.status} status")
    
    booking.status = "cancelled"
    booking.cancellation_reason = reason
    booking.cancelled_by = cancelled_by_role
    booking.cancelled_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(booking)
    
    # Notify the other party
    if cancelled_by_role == "customer":
        await create_notification(
            db=db,
            user_id=booking.provider.user_id,
            notification_type="booking_cancelled",
            title="Booking Cancelled",
            message=f"Booking cancelled by customer: {reason}",
            data={"booking_id": str(booking.id)}
        )
    elif cancelled_by_role == "provider":
        await create_notification(
            db=db,
            user_id=booking.customer.user_id,
            notification_type="booking_cancelled",
            title="Booking Cancelled",
            message=f"Booking cancelled by provider: {reason}",
            data={"booking_id": str(booking.id)}
        )
    
    return booking


@router.get("/{booking_id}/timeline")
async def get_booking_timeline(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get booking status timeline."""
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
    
    timeline = [
        {
            "status": "requested",
            "timestamp": booking.created_at,
            "notes": "Booking request created"
        }
    ]
    
    if booking.status in ["accepted", "scheduled", "in_progress", "completed", "cancelled"]:
        timeline.append({
            "status": "accepted",
            "timestamp": booking.updated_at,
            "notes": "Booking accepted by provider"
        })
    
    if booking.scheduled_datetime:
        timeline.append({
            "status": "scheduled",
            "timestamp": booking.scheduled_datetime,
            "notes": f"Scheduled for {booking.scheduled_datetime.strftime('%Y-%m-%d %H:%M')}"
        })
    
    if booking.status == "in_progress":
        timeline.append({
            "status": "in_progress",
            "timestamp": booking.updated_at,
            "notes": "Service started"
        })
    
    if booking.completed_at:
        timeline.append({
            "status": "completed",
            "timestamp": booking.completed_at,
            "notes": "Service completed"
        })
    
    if booking.cancelled_at:
        timeline.append({
            "status": "cancelled",
            "timestamp": booking.cancelled_at,
            "notes": f"Cancelled by {booking.cancelled_by}: {booking.cancellation_reason}"
        })
    
    return {"timeline": timeline}

