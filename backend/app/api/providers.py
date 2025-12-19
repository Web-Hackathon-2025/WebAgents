"""Provider endpoints."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from uuid import UUID

from app.core.security import require_provider, get_current_user
from app.core.exceptions import NotFoundError, BadRequestError
from app.db.client import get_db
from app.db.models import (
    User, ProviderProfile, Service, Booking as BookingModel,
    ProviderAvailability, ProviderTimeOff, Review
)
from app.domain.models import (
    ProviderProfile as ProviderProfileResponse,
    ProviderProfileUpdate,
    Service as ServiceResponse,
    ServiceCreate,
    ServiceUpdate,
    ProviderAvailability as ProviderAvailabilityResponse,
    ProviderAvailabilityCreate,
    ProviderTimeOff as ProviderTimeOffResponse,
    ProviderTimeOffCreate,
    Booking,
    PaginatedResponse
)

router = APIRouter(prefix="/api/v1/providers", tags=["providers"])


@router.get("/profile", response_model=ProviderProfileResponse)
async def get_provider_profile(
    current_user: User = Depends(require_provider),
    db: AsyncSession = Depends(get_db)
):
    """Get provider profile."""
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise NotFoundError("Provider profile not found")
    
    return ProviderProfileResponse.model_validate(profile)


@router.patch("/profile", response_model=ProviderProfileResponse)
async def update_provider_profile(
    profile_data: ProviderProfileUpdate,
    current_user: User = Depends(require_provider),
    db: AsyncSession = Depends(get_db)
):
    """Update provider profile."""
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        raise NotFoundError("Provider profile not found")
    
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
    
    return ProviderProfileResponse.model_validate(profile)


@router.get("/services", response_model=List[ServiceResponse])
async def get_provider_services(
    current_user: User = Depends(require_provider),
    db: AsyncSession = Depends(get_db)
):
    """Get provider's services."""
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == current_user.id)
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise NotFoundError("Provider profile not found")
    
    services_result = await db.execute(
        select(Service).where(Service.provider_id == provider.id)
    )
    services = services_result.scalars().all()
    
    return [ServiceResponse.model_validate(s) for s in services]


@router.post("/services", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    service_data: ServiceCreate,
    current_user: User = Depends(require_provider),
    db: AsyncSession = Depends(get_db)
):
    """Create a new service."""
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == current_user.id)
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise NotFoundError("Provider profile not found")
    
    service = Service(
        provider_id=provider.id,
        category_id=service_data.category_id,
        title=service_data.title,
        description=service_data.description,
        base_price=service_data.base_price,
        price_unit=service_data.price_unit,
        duration_minutes=service_data.duration_minutes,
        tags=service_data.tags or [],
        images=service_data.images or []
    )
    db.add(service)
    await db.commit()
    await db.refresh(service)
    
    return ServiceResponse.model_validate(service)


@router.patch("/services/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: UUID,
    service_data: ServiceUpdate,
    current_user: User = Depends(require_provider),
    db: AsyncSession = Depends(get_db)
):
    """Update a service."""
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == current_user.id)
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise NotFoundError("Provider profile not found")
    
    service_result = await db.execute(
        select(Service).where(
            Service.id == service_id,
            Service.provider_id == provider.id
        )
    )
    service = service_result.scalar_one_or_none()
    
    if not service:
        raise NotFoundError("Service not found")
    
    # Update fields
    update_data = service_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(service, field, value)
    
    await db.commit()
    await db.refresh(service)
    
    return ServiceResponse.model_validate(service)


@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: UUID,
    current_user: User = Depends(require_provider),
    db: AsyncSession = Depends(get_db)
):
    """Delete a service."""
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == current_user.id)
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise NotFoundError("Provider profile not found")
    
    service_result = await db.execute(
        select(Service).where(
            Service.id == service_id,
            Service.provider_id == provider.id
        )
    )
    service = service_result.scalar_one_or_none()
    
    if not service:
        raise NotFoundError("Service not found")
    
    await db.delete(service)
    await db.commit()


@router.get("/bookings", response_model=PaginatedResponse)
async def get_provider_bookings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    current_user: User = Depends(require_provider),
    db: AsyncSession = Depends(get_db)
):
    """Get provider's bookings."""
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == current_user.id)
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise NotFoundError("Provider profile not found")
    
    query = select(BookingModel).where(BookingModel.provider_id == provider.id)
    
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


@router.get("/availability", response_model=List[ProviderAvailabilityResponse])
async def get_availability(
    current_user: User = Depends(require_provider),
    db: AsyncSession = Depends(get_db)
):
    """Get provider availability schedule."""
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == current_user.id)
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise NotFoundError("Provider profile not found")
    
    availability_result = await db.execute(
        select(ProviderAvailability).where(ProviderAvailability.provider_id == provider.id)
    )
    availability = availability_result.scalars().all()
    
    return [ProviderAvailabilityResponse.model_validate(a) for a in availability]


@router.post("/availability", response_model=List[ProviderAvailabilityResponse], status_code=status.HTTP_201_CREATED)
async def set_availability(
    availability_data: List[ProviderAvailabilityCreate],
    current_user: User = Depends(require_provider),
    db: AsyncSession = Depends(get_db)
):
    """Set provider availability schedule."""
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == current_user.id)
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise NotFoundError("Provider profile not found")
    
    # Delete existing availability
    await db.execute(
        select(ProviderAvailability).where(ProviderAvailability.provider_id == provider.id)
    )
    existing = await db.execute(
        select(ProviderAvailability).where(ProviderAvailability.provider_id == provider.id)
    )
    for item in existing.scalars().all():
        await db.delete(item)
    
    # Create new availability
    new_availability = []
    for item_data in availability_data:
        item = ProviderAvailability(
            provider_id=provider.id,
            day_of_week=item_data.day_of_week,
            start_time=item_data.start_time,
            end_time=item_data.end_time,
            is_available=item_data.is_available
        )
        db.add(item)
        new_availability.append(item)
    
    await db.commit()
    
    return [ProviderAvailabilityResponse.model_validate(a) for a in new_availability]


@router.get("/time-off", response_model=List[ProviderTimeOffResponse])
async def get_time_off(
    current_user: User = Depends(require_provider),
    db: AsyncSession = Depends(get_db)
):
    """Get provider time-off periods."""
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == current_user.id)
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise NotFoundError("Provider profile not found")
    
    time_off_result = await db.execute(
        select(ProviderTimeOff)
        .where(ProviderTimeOff.provider_id == provider.id)
        .order_by(ProviderTimeOff.start_datetime)
    )
    time_off = time_off_result.scalars().all()
    
    return [ProviderTimeOffResponse.model_validate(t) for t in time_off]


@router.post("/time-off", response_model=ProviderTimeOffResponse, status_code=status.HTTP_201_CREATED)
async def create_time_off(
    time_off_data: ProviderTimeOffCreate,
    current_user: User = Depends(require_provider),
    db: AsyncSession = Depends(get_db)
):
    """Create a time-off period."""
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == current_user.id)
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise NotFoundError("Provider profile not found")
    
    time_off = ProviderTimeOff(
        provider_id=provider.id,
        start_datetime=time_off_data.start_datetime,
        end_datetime=time_off_data.end_datetime,
        reason=time_off_data.reason
    )
    db.add(time_off)
    await db.commit()
    await db.refresh(time_off)
    
    return ProviderTimeOffResponse.model_validate(time_off)


@router.delete("/time-off/{time_off_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_time_off(
    time_off_id: UUID,
    current_user: User = Depends(require_provider),
    db: AsyncSession = Depends(get_db)
):
    """Delete a time-off period."""
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == current_user.id)
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise NotFoundError("Provider profile not found")
    
    time_off_result = await db.execute(
        select(ProviderTimeOff).where(
            ProviderTimeOff.id == time_off_id,
            ProviderTimeOff.provider_id == provider.id
        )
    )
    time_off = time_off_result.scalar_one_or_none()
    
    if not time_off:
        raise NotFoundError("Time-off period not found")
    
    await db.delete(time_off)
    await db.commit()

