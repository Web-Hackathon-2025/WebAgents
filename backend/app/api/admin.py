"""Admin endpoints."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date

from app.core.security import require_admin, get_current_user
from app.core.exceptions import NotFoundError, BadRequestError
from app.db.client import get_db
from app.db.models import (
    User, CustomerProfile, ProviderProfile, Booking as BookingModel,
    Review, Dispute, Service, ServiceCategory
)
from app.domain.models import (
    UserProfile,
    ProviderProfile as ProviderProfileResponse,
    ProviderVerification,
    DisputeResolution,
    Booking,
    Review as ReviewResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/users", response_model=PaginatedResponse)
async def list_users(
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all users with filters."""
    query = select(User)
    
    if role:
        query = query.where(User.role == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    if search:
        query = query.where(
            or_(
                User.email.ilike(f"%{search}%"),
                User.phone.ilike(f"%{search}%")
            )
        )
    
    # Get total count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()
    
    # Get paginated results
    query = query.order_by(User.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return PaginatedResponse.create(
        items=[UserProfile.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/users/{user_id}", response_model=UserProfile)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get user details."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise NotFoundError("User not found")
    
    return UserProfile.model_validate(user)


@router.patch("/users/{user_id}")
async def update_user(
    user_id: UUID,
    is_active: Optional[bool] = None,
    is_verified: Optional[bool] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update user (suspend, activate, verify)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise NotFoundError("User not found")
    
    if is_active is not None:
        user.is_active = is_active
    if is_verified is not None:
        user.is_verified = is_verified
    
    await db.commit()
    await db.refresh(user)
    
    return UserProfile.model_validate(user)


@router.get("/providers/pending", response_model=List[ProviderProfileResponse])
async def list_pending_providers(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """List pending provider approvals."""
    result = await db.execute(
        select(ProviderProfile)
        .where(ProviderProfile.status == "pending")
        .order_by(ProviderProfile.created_at)
    )
    providers = result.scalars().all()
    
    return [ProviderProfileResponse.model_validate(p) for p in providers]


@router.post("/providers/{provider_id}/approve")
async def approve_provider(
    provider_id: UUID,
    verification_data: ProviderVerification,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Approve a provider."""
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.id == provider_id)
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise NotFoundError("Provider not found")
    
    if provider.status != "pending":
        raise BadRequestError(f"Provider is already {provider.status}")
    
    provider.status = "approved"
    provider.is_verified = True
    
    # Update user verification status
    user_result = await db.execute(select(User).where(User.id == provider.user_id))
    user = user_result.scalar_one_or_none()
    if user:
        user.is_verified = True
    
    await db.commit()
    await db.refresh(provider)
    
    # Create notification
    from app.utils.notifications import create_notification
    await create_notification(
        db=db,
        user_id=provider.user_id,
        notification_type="system",
        title="Provider Account Approved",
        message="Your provider account has been approved. You can now start accepting bookings!",
        data={"provider_id": str(provider.id)}
    )
    
    return ProviderProfileResponse.model_validate(provider)


@router.post("/providers/{provider_id}/reject")
async def reject_provider(
    provider_id: UUID,
    verification_data: ProviderVerification,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Reject a provider."""
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.id == provider_id)
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        raise NotFoundError("Provider not found")
    
    if provider.status != "pending":
        raise BadRequestError(f"Provider is already {provider.status}")
    
    provider.status = "rejected"
    
    await db.commit()
    await db.refresh(provider)
    
    # Create notification
    from app.utils.notifications import create_notification
    await create_notification(
        db=db,
        user_id=provider.user_id,
        notification_type="system",
        title="Provider Account Rejected",
        message=f"Your provider account application has been rejected. {verification_data.notes or 'Please contact support for more information.'}",
        data={"provider_id": str(provider.id)}
    )
    
    return ProviderProfileResponse.model_validate(provider)


@router.get("/bookings", response_model=PaginatedResponse)
async def list_all_bookings(
    status: Optional[str] = Query(None),
    customer_id: Optional[UUID] = Query(None),
    provider_id: Optional[UUID] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all bookings with filters."""
    query = select(BookingModel)
    
    if status:
        query = query.where(BookingModel.status == status)
    if customer_id:
        query = query.where(BookingModel.customer_id == customer_id)
    if provider_id:
        query = query.where(BookingModel.provider_id == provider_id)
    if start_date:
        query = query.where(BookingModel.created_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.where(BookingModel.created_at <= datetime.combine(end_date, datetime.max.time()))
    
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


@router.get("/reviews/flagged", response_model=List[ReviewResponse])
async def list_flagged_reviews(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """List flagged reviews for moderation."""
    result = await db.execute(
        select(Review)
        .where(Review.is_flagged == True)
        .order_by(Review.created_at.desc())
    )
    reviews = result.scalars().all()
    
    return [ReviewResponse.model_validate(r) for r in reviews]


@router.post("/reviews/{review_id}/moderate")
async def moderate_review(
    review_id: UUID,
    action: str = Query(..., pattern="^(approve|reject|remove)$"),
    reason: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Moderate a flagged review."""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise NotFoundError("Review not found")
    
    if action == "approve":
        review.is_flagged = False
        review.flag_reason = None
    elif action == "reject":
        review.is_flagged = True
        review.flag_reason = reason or "Rejected by admin"
    elif action == "remove":
        await db.delete(review)
        await db.commit()
        return {"message": "Review removed"}
    
    await db.commit()
    await db.refresh(review)
    
    return ReviewResponse.model_validate(review)


@router.get("/disputes", response_model=PaginatedResponse)
async def list_disputes(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all disputes."""
    query = select(Dispute)
    
    if status:
        query = query.where(Dispute.status == status)
    
    # Get total count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar()
    
    # Get paginated results
    query = query.order_by(Dispute.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    disputes = result.scalars().all()
    
    # Convert to dict for response
    disputes_data = []
    for dispute in disputes:
        disputes_data.append({
            "id": dispute.id,
            "booking_id": dispute.booking_id,
            "raised_by": dispute.raised_by,
            "dispute_type": dispute.dispute_type,
            "description": dispute.description,
            "status": dispute.status,
            "ai_resolution_suggestion": dispute.ai_resolution_suggestion,
            "resolution": dispute.resolution,
            "created_at": dispute.created_at,
            "updated_at": dispute.updated_at
        })
    
    return PaginatedResponse.create(
        items=disputes_data,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/disputes/{dispute_id}")
async def get_dispute(
    dispute_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get dispute details."""
    result = await db.execute(select(Dispute).where(Dispute.id == dispute_id))
    dispute = result.scalar_one_or_none()
    
    if not dispute:
        raise NotFoundError("Dispute not found")
    
    return {
        "id": dispute.id,
        "booking_id": dispute.booking_id,
        "raised_by": dispute.raised_by,
        "dispute_type": dispute.dispute_type,
        "description": dispute.description,
        "evidence": dispute.evidence,
        "status": dispute.status,
        "ai_resolution_suggestion": dispute.ai_resolution_suggestion,
        "admin_notes": dispute.admin_notes,
        "resolution": dispute.resolution,
        "created_at": dispute.created_at,
        "updated_at": dispute.updated_at
    }


@router.post("/disputes/{dispute_id}/resolve")
async def resolve_dispute(
    dispute_id: UUID,
    resolution_data: DisputeResolution,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Resolve a dispute."""
    result = await db.execute(select(Dispute).where(Dispute.id == dispute_id))
    dispute = result.scalar_one_or_none()
    
    if not dispute:
        raise NotFoundError("Dispute not found")
    
    dispute.status = resolution_data.status
    dispute.resolution = resolution_data.resolution
    dispute.admin_notes = resolution_data.admin_notes
    dispute.resolved_by = current_user.id
    dispute.resolved_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(dispute)
    
    # Create notifications for both parties
    from app.utils.notifications import create_notification
    
    # Get booking to find both parties
    booking_result = await db.execute(
        select(BookingModel).where(BookingModel.id == dispute.booking_id)
    )
    booking = booking_result.scalar_one_or_none()
    
    if booking:
        # Notify customer
        customer_result = await db.execute(
            select(CustomerProfile).where(CustomerProfile.id == booking.customer_id)
        )
        customer = customer_result.scalar_one_or_none()
        if customer:
            await create_notification(
                db=db,
                user_id=customer.user_id,
                notification_type="system",
                title="Dispute Resolved",
                message=f"Your dispute has been resolved: {resolution_data.resolution}",
                data={"dispute_id": str(dispute.id), "booking_id": str(booking.id)}
            )
        
        # Notify provider
        provider_result = await db.execute(
            select(ProviderProfile).where(ProviderProfile.id == booking.provider_id)
        )
        provider = provider_result.scalar_one_or_none()
        if provider:
            await create_notification(
                db=db,
                user_id=provider.user_id,
                notification_type="system",
                title="Dispute Resolved",
                message=f"The dispute has been resolved: {resolution_data.resolution}",
                data={"dispute_id": str(dispute.id), "booking_id": str(booking.id)}
            )
    
    return {
        "id": dispute.id,
        "status": dispute.status,
        "resolution": dispute.resolution,
        "resolved_at": dispute.resolved_at
    }


@router.get("/analytics")
async def get_platform_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get platform analytics."""
    # Total users
    total_users = await db.execute(select(func.count(User.id)))
    total_customers = await db.execute(
        select(func.count(User.id)).where(User.role == "customer")
    )
    total_providers = await db.execute(
        select(func.count(User.id)).where(User.role == "provider")
    )
    
    # Total bookings
    bookings_query = select(func.count(BookingModel.id))
    if start_date:
        bookings_query = bookings_query.where(BookingModel.created_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        bookings_query = bookings_query.where(BookingModel.created_at <= datetime.combine(end_date, datetime.max.time()))
    
    total_bookings = await db.execute(bookings_query)
    
    # Bookings by status
    bookings_by_status = await db.execute(
        select(BookingModel.status, func.count(BookingModel.id))
        .group_by(BookingModel.status)
    )
    
    # Total revenue
    revenue_query = select(func.sum(BookingModel.final_price)).where(
        BookingModel.payment_status == "paid",
        BookingModel.final_price.isnot(None)
    )
    if start_date:
        revenue_query = revenue_query.where(BookingModel.completed_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        revenue_query = revenue_query.where(BookingModel.completed_at <= datetime.combine(end_date, datetime.max.time()))
    
    total_revenue = await db.execute(revenue_query)
    
    # Top categories
    top_categories = await db.execute(
        select(ServiceCategory.name, func.count(Service.id))
        .join(Service)
        .join(BookingModel)
        .group_by(ServiceCategory.name)
        .order_by(func.count(Service.id).desc())
        .limit(10)
    )
    
    return {
        "users": {
            "total": total_users.scalar(),
            "customers": total_customers.scalar(),
            "providers": total_providers.scalar()
        },
        "bookings": {
            "total": total_bookings.scalar(),
            "by_status": {row[0]: row[1] for row in bookings_by_status.fetchall()}
        },
        "revenue": {
            "total": float(total_revenue.scalar() or 0)
        },
        "top_categories": [
            {"name": row[0], "count": row[1]} for row in top_categories.fetchall()
        ]
    }


@router.get("/analytics/providers")
async def get_provider_analytics(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get provider analytics."""
    # Provider stats
    total_providers = await db.execute(
        select(func.count(ProviderProfile.id))
    )
    approved_providers = await db.execute(
        select(func.count(ProviderProfile.id)).where(ProviderProfile.status == "approved")
    )
    pending_providers = await db.execute(
        select(func.count(ProviderProfile.id)).where(ProviderProfile.status == "pending")
    )
    
    # Average rating
    avg_rating = await db.execute(
        select(func.avg(ProviderProfile.rating_average))
        .where(ProviderProfile.status == "approved")
    )
    
    # Top providers by bookings
    top_providers = await db.execute(
        select(
            ProviderProfile.business_name,
            ProviderProfile.rating_average,
            ProviderProfile.total_bookings,
            ProviderProfile.completion_rate
        )
        .where(ProviderProfile.status == "approved")
        .order_by(ProviderProfile.total_bookings.desc())
        .limit(10)
    )
    
    return {
        "total": total_providers.scalar(),
        "approved": approved_providers.scalar(),
        "pending": pending_providers.scalar(),
        "average_rating": float(avg_rating.scalar() or 0),
        "top_providers": [
            {
                "name": row[0],
                "rating": float(row[1]),
                "total_bookings": row[2],
                "completion_rate": float(row[3])
            }
            for row in top_providers.fetchall()
        ]
    }


@router.get("/analytics/bookings")
async def get_booking_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get booking analytics."""
    base_query = select(BookingModel)
    if start_date:
        base_query = base_query.where(BookingModel.created_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        base_query = base_query.where(BookingModel.created_at <= datetime.combine(end_date, datetime.max.time()))
    
    # Bookings by status
    bookings_by_status = await db.execute(
        base_query.select_from(base_query.subquery())
        .with_only_columns([BookingModel.status, func.count(BookingModel.id)])
        .group_by(BookingModel.status)
    )
    
    # Completion rate
    completed = await db.execute(
        base_query.where(BookingModel.status == "completed")
    )
    total = await db.execute(base_query)
    
    # Average booking value
    avg_value = await db.execute(
        select(func.avg(BookingModel.final_price))
        .where(BookingModel.final_price.isnot(None))
    )
    
    return {
        "total": total.rowcount,
        "completed": completed.rowcount,
        "completion_rate": (completed.rowcount / total.rowcount * 100) if total.rowcount > 0 else 0,
        "by_status": {row[0]: row[1] for row in bookings_by_status.fetchall()},
        "average_value": float(avg_value.scalar() or 0)
    }

