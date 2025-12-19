"""Matching service using AI matching agent."""
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.sql import text
from decimal import Decimal

from app.agents.matching_agent import MatchingAgent
from app.db.models import ProviderProfile, Service, ServiceCategory, Booking as BookingModel
from app.utils.distance import haversine_distance
from app.core.parallel import execute_parallel_with_timeout


class MatchingService:
    """Service for intelligent provider matching."""
    
    def __init__(self):
        self.matching_agent = MatchingAgent()
    
    async def find_matching_providers(
        self,
        db: AsyncSession,
        service_id: str,
        customer_lat: Decimal,
        customer_lng: Decimal,
        preferred_date: Optional[str] = None,
        preferred_time: Optional[str] = None,
        budget: Optional[Decimal] = None,
        booking_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find matching providers for a service request.
        
        Returns list of providers with match scores.
        """
        # Get service details
        service_result = await db.execute(
            select(Service).where(Service.id == service_id)
        )
        service = service_result.scalar_one_or_none()
        
        if not service:
            return []
        
        # Find providers offering this service category within radius
        # Using PostGIS for geospatial query
        radius_km = 50  # Default search radius
        
        query = text("""
            SELECT 
                pp.*,
                ST_Distance(
                    pp.location::geography,
                    ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography
                ) / 1000.0 as distance_km
            FROM provider_profiles pp
            INNER JOIN services s ON s.provider_id = pp.id
            WHERE s.category_id = :category_id
                AND s.is_active = true
                AND pp.status = 'approved'
                AND ST_DWithin(
                    pp.location::geography,
                    ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography,
                    :radius * 1000
                )
            ORDER BY distance_km
            LIMIT 20
        """)
        
        result = await db.execute(
            query,
            {
                "lat": float(customer_lat),
                "lng": float(customer_lng),
                "category_id": str(service.category_id),
                "radius": radius_km
            }
        )
        
        providers_data = []
        for row in result:
            provider_id = row.id
            
            # Get provider's recent reviews summary
            reviews_result = await db.execute(
                select(func.avg(BookingModel.final_price))
                .where(BookingModel.provider_id == provider_id)
                .where(BookingModel.status == "completed")
            )
            avg_price = reviews_result.scalar() or service.base_price
            
            # Build provider context
            provider_data = {
                "id": str(provider_id),
                "name": row.business_name,
                "distance_km": round(float(row.distance_km), 2),
                "rating": float(row.rating_average),
                "total_reviews": row.rating_count,
                "completion_rate": float(row.completion_rate),
                "base_price": float(service.base_price),
                "avg_price": float(avg_price),
                "response_time_minutes": row.response_time_minutes,
                "total_bookings": row.total_bookings,
            }
            providers_data.append(provider_data)
        
        if not providers_data:
            return []
        
        # Prepare context for matching agent
        context = {
            "customer_request": {
                "service_category": service.category_id,
                "service_type": service.title,
                "location": {"lat": float(customer_lat), "lng": float(customer_lng)},
                "preferred_date": preferred_date,
                "preferred_time": preferred_time,
                "budget": float(budget) if budget else None
            },
            "available_providers": providers_data,
            "execution_context": "matching"
        }
        
        # Execute matching agent
        agent_response = await self.matching_agent.execute(
            context=context,
            db=db,
            booking_id=booking_id
        )
        
        # Process agent response
        matches = agent_response.get("matches", [])
        
        # Enrich matches with full provider data
        enriched_matches = []
        for match in matches:
            provider_id = match.get("provider_id")
            provider_data = next(
                (p for p in providers_data if p["id"] == provider_id),
                None
            )
            
            if provider_data:
                enriched_matches.append({
                    "provider_id": provider_id,
                    "match_score": match.get("match_score", 0),
                    "reasoning": match.get("reasoning", ""),
                    "provider": provider_data,
                    "strengths": match.get("strengths", []),
                    "concerns": match.get("concerns", [])
                })
        
        # Sort by match score
        enriched_matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return enriched_matches[:10]  # Return top 10 matches

