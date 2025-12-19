"""Search and discovery endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.sql import text
from typing import List, Optional
from decimal import Decimal

from app.core.security.dependencies import get_optional_user
from fastapi import Security
from fastapi.security import HTTPBearer
from app.db.client import get_db
from app.db.models import (
    ProviderProfile, Service, ServiceCategory, CustomerProfile, User
)
from app.domain.models import (
    SearchFilters,
    SearchResults,
    ProviderMatch,
    ProviderProfile as ProviderProfileResponse,
    ServiceCategory as ServiceCategoryResponse,
    Service as ServiceResponse
)
from app.services.matching import MatchingService
from app.services.recommendations import RecommendationService

router = APIRouter(prefix="/api/v1/search", tags=["search"])

matching_service = MatchingService()
recommendation_service = RecommendationService()


@router.get("/providers", response_model=SearchResults)
async def search_providers(
    category_id: Optional[str] = Query(None),
    latitude: Optional[Decimal] = Query(None),
    longitude: Optional[Decimal] = Query(None),
    radius_km: int = Query(10, ge=1, le=50),
    min_rating: Optional[Decimal] = Query(None, ge=0, le=5),
    max_price: Optional[Decimal] = Query(None),
    min_price: Optional[Decimal] = Query(None),
    city: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """Search for providers with filters."""
    # Build base query
    query = select(ProviderProfile).where(ProviderProfile.status == "approved")
    
    # Filter by category if provided
    if category_id:
        query = query.join(Service).where(Service.category_id == category_id)
    
    # Filter by city
    if city:
        query = query.where(ProviderProfile.city.ilike(f"%{city}%"))
    
    # Filter by rating
    if min_rating:
        query = query.where(ProviderProfile.rating_average >= min_rating)
    
    # Geospatial filter if location provided
    if latitude and longitude:
        # Use PostGIS for distance filtering
        distance_query = text("""
            SELECT 
                pp.*,
                ST_Distance(
                    pp.location::geography,
                    ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography
                ) / 1000.0 as distance_km
            FROM provider_profiles pp
            WHERE pp.status = 'approved'
                AND ST_DWithin(
                    pp.location::geography,
                    ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography,
                    :radius * 1000
                )
        """)
        
        # Add category filter if provided
        if category_id:
            distance_query = text("""
                SELECT 
                    pp.*,
                    ST_Distance(
                        pp.location::geography,
                        ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography
                    ) / 1000.0 as distance_km
                FROM provider_profiles pp
                INNER JOIN services s ON s.provider_id = pp.id
                WHERE pp.status = 'approved'
                    AND s.category_id = :category_id
                    AND ST_DWithin(
                        pp.location::geography,
                        ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography,
                        :radius * 1000
                    )
            """)
        
        result = await db.execute(
            distance_query,
            {
                "lat": float(latitude),
                "lng": float(longitude),
                "radius": radius_km,
                "category_id": category_id
            }
        )
        providers = result.fetchall()
    else:
        # Regular query without geospatial filtering
        result = await db.execute(query.limit(100))
        providers = result.scalars().all()
        providers = [(p, None) for p in providers]  # No distance
    
    # Convert to provider profiles and calculate match scores
    provider_matches = []
    for provider_data in providers:
        if isinstance(provider_data, tuple):
            provider = provider_data[0]
            distance_km = provider_data[1] if len(provider_data) > 1 else None
        else:
            provider = provider_data
            distance_km = None
        
        # Filter by price if provided
        if max_price or min_price:
            services_result = await db.execute(
                select(Service).where(Service.provider_id == provider.id)
            )
            services = services_result.scalars().all()
            if services:
                prices = [float(s.base_price) for s in services]
                if max_price and all(p > float(max_price) for p in prices):
                    continue
                if min_price and all(p < float(min_price) for p in prices):
                    continue
        
        # Calculate match score (simple for now, can use AI agent)
        match_score = float(provider.rating_average) * 20  # Base score from rating
        if distance_km and distance_km < 5:
            match_score += 20
        elif distance_km and distance_km < 10:
            match_score += 10
        
        provider_matches.append(ProviderMatch(
            provider=ProviderProfileResponse.model_validate(provider),
            match_score=Decimal(str(min(100, match_score))),
            distance_km=Decimal(str(distance_km)) if distance_km else None
        ))
    
    # Sort by match score
    provider_matches.sort(key=lambda x: x.match_score, reverse=True)
    
    # Paginate
    total = len(provider_matches)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_matches = provider_matches[start:end]
    
    return SearchResults(
        providers=paginated_matches,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/categories", response_model=List[ServiceCategoryResponse])
async def get_categories(
    db: AsyncSession = Depends(get_db)
):
    """Get all service categories."""
    result = await db.execute(
        select(ServiceCategory)
        .where(ServiceCategory.is_active == True)
        .order_by(ServiceCategory.display_order, ServiceCategory.name)
    )
    categories = result.scalars().all()
    
    return [ServiceCategoryResponse.model_validate(c) for c in categories]


@router.get("/recommendations", response_model=List[ProviderProfileResponse])
async def get_recommendations(
    category_id: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """Get personalized provider recommendations."""
    if not current_user:
        return []
    
    # Get customer profile
    customer_result = await db.execute(
        select(CustomerProfile).where(CustomerProfile.user_id == current_user.id)
    )
    customer = customer_result.scalar_one_or_none()
    
    if not customer:
        return []
    
    # Get recommendations using AI agent
    recommendations = await recommendation_service.get_recommendations(
        db=db,
        customer_id=str(customer.id),
        category_id=category_id,
        limit=limit
    )
    
    # Get provider details
    provider_ids = [r["provider_id"] for r in recommendations]
    if not provider_ids:
        return []
    
    result = await db.execute(
        select(ProviderProfile).where(ProviderProfile.id.in_(provider_ids))
    )
    providers = result.scalars().all()
    
    # Sort by recommendation confidence
    provider_dict = {str(p.id): p for p in providers}
    sorted_providers = [
        provider_dict[r["provider_id"]]
        for r in recommendations
        if r["provider_id"] in provider_dict
    ]
    
    return [ProviderProfileResponse.model_validate(p) for p in sorted_providers]


@router.get("/providers/{provider_id}", response_model=ProviderProfileResponse)
async def get_provider_public_profile(
    provider_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get public provider profile."""
    result = await db.execute(
        select(ProviderProfile).where(
            ProviderProfile.id == provider_id,
            ProviderProfile.status == "approved"
        )
    )
    provider = result.scalar_one_or_none()
    
    if not provider:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Provider not found")
    
    return ProviderProfileResponse.model_validate(provider)


@router.get("/providers/{provider_id}/services", response_model=List[ServiceResponse])
async def get_provider_services(
    provider_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get provider's services."""
    result = await db.execute(
        select(Service)
        .where(Service.provider_id == provider_id)
        .where(Service.is_active == True)
    )
    services = result.scalars().all()
    
    return [ServiceResponse.model_validate(s) for s in services]

