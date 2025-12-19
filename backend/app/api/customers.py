"""Customer endpoints."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from uuid import UUID

from app.core.security import require_customer, get_current_user
from app.core.exceptions import NotFoundError
from app.db.client import get_db
from app.db.models import User, CustomerProfile, Booking as BookingModel, Review, Service as ServiceModel
from app.domain.models import (
    CustomerProfile as CustomerProfileResponse,
    CustomerProfileUpdate,
    Booking,
    Review as ReviewResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/api/v1/customers", tags=["customers"])


@router.get("/profile", response_model=CustomerProfileResponse)
async def get_customer_profile(
    current_user: User = Depends(require_customer),
    db: AsyncSession = Depends(get_db)
):
    """Get customer profile."""
    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise NotFoundError("Customer profile not found")
    
    return CustomerProfileResponse.model_validate(profile)


@router.patch("/profile", response_model=CustomerProfileResponse)
async def update_customer_profile(
    profile_data: CustomerProfileUpdate,
    current_user: User = Depends(require_customer),
    db: AsyncSession = Depends(get_db)
):
    """Update customer profile."""
    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise NotFoundError("Customer profile not found")
    
    # Update fields
    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    # Update location if lat/lng provided
    if profile_data.latitude and profile_data.longitude:
        from geoalchemy2 import WKTElement
        profile.location = WKTElement(
            f"POINT({profile_data.longitude} {profile_data.latitude})",
            srid=4326
        )
    
    await db.commit()
    await db.refresh(profile)
    
    return CustomerProfileResponse.model_validate(profile)


@router.get("/bookings", response_model=PaginatedResponse)
async def get_customer_bookings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    current_user: User = Depends(require_customer),
    db: AsyncSession = Depends(get_db)
):
    """Get customer's bookings."""
    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise NotFoundError("Customer profile not found")
    
    query = select(BookingModel).where(BookingModel.customer_id == customer.id)
    
    if status_filter:
        query = query.where(BookingModel.status == status_filter)
    
    # Get total count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()
    
    # Get paginated results
    query = query.order_by(BookingModel.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    bookings = result.scalars().all()
    
    return PaginatedResponse.create(
        items=[Booking.model_validate(b) for b in bookings],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/reviews", response_model=List[ReviewResponse])
async def get_customer_reviews(
    current_user: User = Depends(require_customer),
    db: AsyncSession = Depends(get_db)
):
    """Get customer's reviews."""
    result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    )
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise NotFoundError("Customer profile not found")
    
    reviews_result = await db.execute(
        select(Review)
        .where(Review.customer_id == customer.id)
        .order_by(Review.created_at.desc())
    )
    reviews = reviews_result.scalars().all()
    
    return [ReviewResponse.model_validate(r) for r in reviews]

