"""Review endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from app.core.security import require_customer, require_provider, get_current_user
from app.core.exceptions import NotFoundError, BadRequestError
from app.db.client import get_db
from app.db.models import User, Review, Booking as BookingModel, CustomerProfile, ProviderProfile
from app.domain.models import ReviewCreate, ReviewUpdate, Review as ReviewResponse
from app.agents.review_agent import ReviewAnalysisAgent
from app.utils.notifications import create_notification

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])

review_agent = ReviewAnalysisAgent()


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(require_customer),
    db: AsyncSession = Depends(get_db)
):
    """Submit a review for a completed booking."""
    # Get customer profile
    customer_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    )
    customer = customer_result.scalar_one_or_none()
    
    if not customer:
        raise NotFoundError("Customer profile not found")
    
    # Get booking
    booking_result = await db.execute(
        select(BookingModel).where(
            BookingModel.id == review_data.booking_id,
            BookingModel.customer_id == customer.id,
            BookingModel.status == "completed"
        )
    )
    booking = booking_result.scalar_one_or_none()
    
    if not booking:
        raise NotFoundError("Booking not found or not completed")
    
    # Check if review already exists
    existing_review = await db.execute(
        select(Review).where(Review.booking_id == review_data.booking_id)
    )
    if existing_review.scalar_one_or_none():
        raise BadRequestError("Review already exists for this booking")
    
    # Create review
    review = Review(
        booking_id=review_data.booking_id,
        customer_id=customer.id,
        provider_id=booking.provider_id,
        rating=review_data.rating,
        review_text=review_data.review_text,
        service_quality=review_data.service_quality,
        punctuality=review_data.punctuality,
        professionalism=review_data.professionalism,
        value_for_money=review_data.value_for_money,
        images=review_data.images or []
    )
    db.add(review)
    await db.flush()
    
    # Analyze review with AI agent
    context = {
        "rating": review_data.rating,
        "review_text": review_data.review_text or "",
        "service_quality": review_data.service_quality,
        "punctuality": review_data.punctuality,
        "professionalism": review_data.professionalism,
        "value_for_money": review_data.value_for_money,
        "execution_context": "review_analysis"
    }
    
    agent_response = await review_agent.execute(
        context=context,
        db=db,
        booking_id=str(booking.id)
    )
    
    # Update review with AI analysis
    review.ai_sentiment_score = agent_response.get("sentiment_score")
    review.ai_quality_score = agent_response.get("quality_score")
    review.is_flagged = agent_response.get("is_likely_fake", False)
    
    # Update provider ratings
    provider_result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.id == booking.provider_id)
    )
    provider = provider_result.scalar_one_or_none()
    
    if provider:
        # Recalculate average rating
        reviews_result = await db.execute(
            select(Review).where(Review.provider_id == provider.id)
        )
        all_reviews = reviews_result.scalars().all()
        
        if all_reviews:
            total_rating = sum(r.rating for r in all_reviews)
            provider.rating_average = total_rating / len(all_reviews)
            provider.rating_count = len(all_reviews)
    
    await db.commit()
    await db.refresh(review)
    
    # Notify provider
    await create_notification(
        db=db,
        user_id=provider.user_id,
        notification_type="review_received",
        title="New Review Received",
        message=f"You received a {review_data.rating}-star review",
        data={"review_id": str(review.id), "booking_id": str(booking.id)}
    )
    
    return ReviewResponse.model_validate(review)


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get review details."""
    result = await db.execute(
        select(Review).where(Review.id == review_id)
    )
    review = result.scalar_one_or_none()
    
    if not review:
        raise NotFoundError("Review not found")
    
    return ReviewResponse.model_validate(review)


@router.patch("/{review_id}/response", response_model=ReviewResponse)
async def respond_to_review(
    review_id: UUID,
    response_data: ReviewUpdate,
    current_user: User = Depends(require_provider),
    db: AsyncSession = Depends(get_db)
):
    """Provider responds to a review."""
    # Get provider
    provider_result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.user_id == current_user.id)
    )
    provider = provider_result.scalar_one_or_none()
    
    if not provider:
        raise NotFoundError("Provider profile not found")
    
    # Get review
    result = await db.execute(
        select(Review).where(
            Review.id == review_id,
            Review.provider_id == provider.id
        )
    )
    review = result.scalar_one_or_none()
    
    if not review:
        raise NotFoundError("Review not found")
    
    # Update review response
    from datetime import datetime
    review.provider_response = response_data.provider_response
    review.provider_responded_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(review)
    
    # Notify customer
    await create_notification(
        db=db,
        user_id=review.customer.user_id,
        notification_type="review_received",
        title="Provider Responded to Your Review",
        message=f"The provider has responded to your review",
        data={"review_id": str(review.id)}
    )
    
    return ReviewResponse.model_validate(review)

