"""Admin API endpoints for platform oversight and moderation."""
from typing import Optional, List
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from pydantic import BaseModel, Field

from app.db.client import get_db
from app.core.security.permissions import require_admin
from app.db.models import User, CustomerProfile, ProviderProfile, Booking, Review, Service, Dispute
from app.core.exceptions import NotFoundError, ValidationError
from app.utils.validators import validate_pagination


router = APIRouter(prefix="/admin", tags=["admin"])


# Response Models
class UserSummary(BaseModel):
    """User summary for admin view."""
    id: uuid.UUID
    email: str
    phone: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    created_at: str

    class Config:
        from_attributes = True


class ProviderApproval(BaseModel):
    """Provider pending approval."""
    id: uuid.UUID
    user_id: uuid.UUID
    business_name: str
    email: str
    phone: Optional[str]
    is_verified: bool
    verification_status: Optional[str]
    total_services: int
    created_at: str

    class Config:
        from_attributes = True


class BookingOverview(BaseModel):
    """Booking overview for admin."""
    id: uuid.UUID
    customer_email: str
    provider_business_name: str
    service_name: str
    status: str
    quoted_price: Optional[float]
    payment_status: str
    created_at: str

    class Config:
        from_attributes = True


class PlatformMetrics(BaseModel):
    """Platform-level metrics."""
    total_users: int
    total_customers: int
    total_providers: int
    total_admins: int
    active_users: int
    total_bookings: int
    completed_bookings: int
    total_revenue: float
    pending_provider_approvals: int
    open_disputes: int


class DisputeSummary(BaseModel):
    """Dispute summary."""
    id: uuid.UUID
    booking_id: uuid.UUID
    dispute_type: str
    status: str
    description: str
    created_at: str
    raised_by_email: str

    class Config:
        from_attributes = True


# Request Models
class ApproveProviderRequest(BaseModel):
    """Request to approve a provider."""
    notes: Optional[str] = None


class RejectProviderRequest(BaseModel):
    """Request to reject a provider."""
    reason: str


class ResolveDisputeRequest(BaseModel):
    """Request to resolve a dispute."""
    resolution: str
    admin_notes: Optional[str] = None


# User Management
@router.get("/users", response_model=List[UserSummary])
async def get_users(
    role: Optional[str] = Query(None, description="Filter by role (customer/provider/admin)"),
    status: Optional[str] = Query(None, description="Filter by status (active/inactive)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get all users with optional filters.
    
    - **role**: Filter by user role
    - **status**: Filter by active status
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    
    Requires admin access.
    """
    try:
        page, page_size = validate_pagination(page, page_size)
        
        # Build query
        query = select(User)
        
        if role:
            query = query.where(User.role == role)
        if status == "active":
            query = query.where(User.is_active == True)
        elif status == "inactive":
            query = query.where(User.is_active == False)
            
        # Add pagination
        query = query.order_by(desc(User.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        users = result.scalars().all()
        
        return [
            UserSummary(
                id=user.id,
                email=user.email,
                phone=user.phone,
                role=user.role,
                is_active=user.is_active,
                is_verified=user.is_verified,
                created_at=user.created_at.isoformat()
            )
            for user in users
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")


@router.patch("/users/{user_id}/suspend")
async def suspend_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Suspend a user account.
    
    - **user_id**: ID of the user to suspend
    
    Requires admin access.
    """
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise NotFoundError(f"User {user_id} not found")
            
        if user.role == "admin":
            raise ValidationError("Cannot suspend admin users")
            
        user.is_active = False
        await db.commit()
        
        return {"message": f"User {user.email} suspended successfully"}
        
    except (NotFoundError, ValidationError) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to suspend user: {str(e)}")


@router.patch("/users/{user_id}/activate")
async def activate_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Activate a suspended user account.
    
    - **user_id**: ID of the user to activate
    
    Requires admin access.
    """
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise NotFoundError(f"User {user_id} not found")
            
        user.is_active = True
        await db.commit()
        
        return {"message": f"User {user.email} activated successfully"}
        
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to activate user: {str(e)}")


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Permanently delete a user account.
    
    - **user_id**: ID of the user to delete
    
    ⚠️ This is a destructive operation. Use with caution.
    Requires admin access.
    """
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise NotFoundError(f"User {user_id} not found")
            
        if user.role == "admin":
            raise ValidationError("Cannot delete admin users")
            
        # Delete user (cascade will handle related records)
        await db.delete(user)
        await db.commit()
        
        return {"message": f"User {user.email} deleted successfully"}
        
    except (NotFoundError, ValidationError) as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")


# Provider Approval
@router.get("/providers/pending", response_model=List[ProviderApproval])
async def get_pending_providers(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get all providers pending approval.
    
    Returns providers who are not yet verified.
    Requires admin access.
    """
    try:
        query = select(ProviderProfile, User, func.count(Service.id).label("total_services")).join(
            User, ProviderProfile.user_id == User.id
        ).outerjoin(
            Service, Service.provider_id == ProviderProfile.id
        ).where(
            ProviderProfile.is_verified == False
        ).group_by(ProviderProfile.id, User.id)
        
        result = await db.execute(query)
        rows = result.all()
        
        return [
            ProviderApproval(
                id=row.ProviderProfile.id,
                user_id=row.User.id,
                business_name=row.ProviderProfile.business_name or "N/A",
                email=row.User.email,
                phone=row.User.phone,
                is_verified=row.ProviderProfile.is_verified,
                verification_status=row.ProviderProfile.verification_status,
                total_services=row.total_services,
                created_at=row.ProviderProfile.created_at.isoformat()
            )
            for row in rows
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pending providers: {str(e)}")


@router.post("/providers/{provider_id}/approve")
async def approve_provider(
    provider_id: uuid.UUID,
    request: ApproveProviderRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Approve a provider.
    
    - **provider_id**: ID of the provider to approve
    - **notes**: Optional admin notes
    
    Requires admin access.
    """
    try:
        result = await db.execute(
            select(ProviderProfile).where(ProviderProfile.id == provider_id)
        )
        provider = result.scalar_one_or_none()
        
        if not provider:
            raise NotFoundError(f"Provider {provider_id} not found")
            
        provider.is_verified = True
        provider.verification_status = "approved"
        provider.admin_notes = request.notes
        
        await db.commit()
        
        return {"message": "Provider approved successfully"}
        
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to approve provider: {str(e)}")


@router.post("/providers/{provider_id}/reject")
async def reject_provider(
    provider_id: uuid.UUID,
    request: RejectProviderRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Reject a provider application.
    
    - **provider_id**: ID of the provider to reject
    - **reason**: Reason for rejection
    
    Requires admin access.
    """
    try:
        result = await db.execute(
            select(ProviderProfile).where(ProviderProfile.id == provider_id)
        )
        provider = result.scalar_one_or_none()
        
        if not provider:
            raise NotFoundError(f"Provider {provider_id} not found")
            
        provider.is_verified = False
        provider.verification_status = "rejected"
        provider.admin_notes = request.reason
        
        await db.commit()
        
        return {"message": "Provider rejected"}
        
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to reject provider: {str(e)}")


# Booking Oversight
@router.get("/bookings", response_model=List[BookingOverview])
async def get_all_bookings(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get all bookings across the platform.
    
    - **status**: Filter by booking status
    - **page**: Page number
    - **page_size**: Items per page
    
    Requires admin access.
    """
    try:
        page, page_size = validate_pagination(page, page_size)
        
        query = select(Booking, CustomerProfile, ProviderProfile, Service, User).join(
            CustomerProfile, Booking.customer_id == CustomerProfile.id
        ).join(
            ProviderProfile, Booking.provider_id == ProviderProfile.id
        ).join(
            Service, Booking.service_id == Service.id
        ).join(
            User, CustomerProfile.user_id == User.id
        )
        
        if status:
            query = query.where(Booking.status == status)
            
        query = query.order_by(desc(Booking.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        rows = result.all()
        
        return [
            BookingOverview(
                id=row.Booking.id,
                customer_email=row.User.email,
                provider_business_name=row.ProviderProfile.business_name or "N/A",
                service_name=row.Service.name,
                status=row.Booking.status,
                quoted_price=float(row.Booking.quoted_price) if row.Booking.quoted_price else None,
                payment_status=row.Booking.payment_status,
                created_at=row.Booking.created_at.isoformat()
            )
            for row in rows
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch bookings: {str(e)}")


# Review Moderation
@router.delete("/reviews/{review_id}")
async def delete_review(
    review_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Delete an inappropriate review.
    
    - **review_id**: ID of the review to delete
    
    Requires admin access.
    """
    try:
        result = await db.execute(select(Review).where(Review.id == review_id))
        review = result.scalar_one_or_none()
        
        if not review:
            raise NotFoundError(f"Review {review_id} not found")
            
        await db.delete(review)
        await db.commit()
        
        return {"message": "Review deleted successfully"}
        
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete review: {str(e)}")


# Disputes
@router.get("/disputes", response_model=List[DisputeSummary])
async def get_disputes(
    status: Optional[str] = Query(None, description="Filter by status (open/under_review/resolved)"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get all disputes.
    
    - **status**: Filter by dispute status
    
    Requires admin access.
    """
    try:
        query = select(Dispute, User).join(User, Dispute.raised_by == User.id)
        
        if status:
            query = query.where(Dispute.status == status)
            
        query = query.order_by(desc(Dispute.created_at))
        
        result = await db.execute(query)
        rows = result.all()
        
        return [
            DisputeSummary(
                id=row.Dispute.id,
                booking_id=row.Dispute.booking_id,
                dispute_type=row.Dispute.dispute_type,
                status=row.Dispute.status,
                description=row.Dispute.description,
                created_at=row.Dispute.created_at.isoformat(),
                raised_by_email=row.User.email
            )
            for row in rows
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch disputes: {str(e)}")


@router.patch("/disputes/{dispute_id}/resolve")
async def resolve_dispute(
    dispute_id: uuid.UUID,
    request: ResolveDisputeRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Resolve a dispute.
    
    - **dispute_id**: ID of the dispute
    - **resolution**: Resolution description
    - **admin_notes**: Optional admin notes
    
    Requires admin access.
    """
    try:
        result = await db.execute(select(Dispute).where(Dispute.id == dispute_id))
        dispute = result.scalar_one_or_none()
        
        if not dispute:
            raise NotFoundError(f"Dispute {dispute_id} not found")
            
        dispute.status = "resolved"
        dispute.resolution = request.resolution
        dispute.admin_notes = request.admin_notes
        dispute.resolved_by = admin.id
        dispute.resolved_at = datetime.utcnow()
        
        await db.commit()
        
        return {"message": "Dispute resolved successfully"}
        
    except NotFoundError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to resolve dispute: {str(e)}")


# Platform Metrics
@router.get("/metrics", response_model=PlatformMetrics)
async def get_platform_metrics(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get platform-level metrics and statistics.
    
    Requires admin access.
    """
    try:
        # Count users by role
        user_counts = await db.execute(
            select(User.role, func.count(User.id)).group_by(User.role)
        )
        role_counts = {row.role: row.count for row in user_counts}
        
        # Count active users
        active_users_result = await db.execute(
            select(func.count(User.id)).where(User.is_active == True)
        )
        active_users = active_users_result.scalar()
        
        # Count bookings
        total_bookings_result = await db.execute(
            select(func.count(Booking.id))
        )
        total_bookings = total_bookings_result.scalar()
        
        # Count completed bookings
        completed_bookings_result = await db.execute(
            select(func.count(Booking.id)).where(Booking.status == "completed")
        )
        completed_bookings = completed_bookings_result.scalar()
        
        # Calculate total revenue (sum of completed bookings)
        revenue_result = await db.execute(
            select(func.coalesce(func.sum(Booking.final_price), 0)).where(
                Booking.status == "completed"
            )
        )
        total_revenue = float(revenue_result.scalar())
        
        # Count pending provider approvals
        pending_providers_result = await db.execute(
            select(func.count(ProviderProfile.id)).where(
                ProviderProfile.is_verified == False
            )
        )
        pending_providers = pending_providers_result.scalar()
        
        # Count open disputes
        open_disputes_result = await db.execute(
            select(func.count(Dispute.id)).where(Dispute.status == "open")
        )
        open_disputes = open_disputes_result.scalar()
        
        return PlatformMetrics(
            total_users=sum(role_counts.values()),
            total_customers=role_counts.get("customer", 0),
            total_providers=role_counts.get("provider", 0),
            total_admins=role_counts.get("admin", 0),
            active_users=active_users or 0,
            total_bookings=total_bookings or 0,
            completed_bookings=completed_bookings or 0,
            total_revenue=total_revenue,
            pending_provider_approvals=pending_providers or 0,
            open_disputes=open_disputes or 0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")
