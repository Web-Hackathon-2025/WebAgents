"""Recommendation service using AI recommendation agent."""
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.agents.recommendation_agent import RecommendationAgent
from app.db.models import CustomerProfile, Booking as BookingModel, ProviderProfile, Service


class RecommendationService:
    """Service for personalized provider recommendations."""
    
    def __init__(self):
        self.recommendation_agent = RecommendationAgent()
    
    async def get_recommendations(
        self,
        db: AsyncSession,
        customer_id: str,
        category_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get personalized provider recommendations for a customer.
        
        Returns list of recommended providers.
        """
        # Get customer's booking history
        bookings_result = await db.execute(
            select(BookingModel)
            .where(BookingModel.customer_id == customer_id)
            .where(BookingModel.status == "completed")
            .order_by(BookingModel.completed_at.desc())
            .limit(20)
        )
        past_bookings = bookings_result.scalars().all()
        
        # Analyze user preferences
        user_history = {
            "total_bookings": len(past_bookings),
            "preferred_categories": [],
            "average_rating_given": 0.0,
            "price_range": {"min": 0, "max": 0}
        }
        
        if past_bookings:
            ratings = [b.review.rating for b in past_bookings if b.review]
            if ratings:
                user_history["average_rating_given"] = sum(ratings) / len(ratings)
            
            prices = [float(b.final_price) for b in past_bookings if b.final_price]
            if prices:
                user_history["price_range"] = {
                    "min": min(prices),
                    "max": max(prices)
                }
        
        # Get customer location
        customer_result = await db.execute(
            select(CustomerProfile).where(CustomerProfile.id == customer_id)
        )
        customer = customer_result.scalar_one_or_none()
        
        if not customer or not customer.latitude or not customer.longitude:
            return []
        
        # Find available providers
        query = select(ProviderProfile).where(
            ProviderProfile.status == "approved"
        )
        
        if category_id:
            query = query.join(Service).where(Service.category_id == category_id)
        
        providers_result = await db.execute(query.limit(50))
        providers = providers_result.scalars().all()
        
        # Build provider data
        available_providers = []
        for provider in providers:
            distance = self._calculate_distance(
                float(customer.latitude),
                float(customer.longitude),
                float(provider.latitude),
                float(provider.longitude)
            )
            
            available_providers.append({
                "id": str(provider.id),
                "name": provider.business_name,
                "rating": float(provider.rating_average),
                "distance_km": distance,
                "total_bookings": provider.total_bookings,
                "completion_rate": float(provider.completion_rate)
            })
        
        # Prepare context for recommendation agent
        context = {
            "customer_id": customer_id,
            "user_history": user_history,
            "available_providers": available_providers,
            "category_id": category_id,
            "execution_context": "recommendations"
        }
        
        # Execute recommendation agent
        agent_response = await self.recommendation_agent.execute(
            context=context,
            db=db
        )
        
        recommendations = agent_response.get("recommendations", [])
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        return recommendations[:limit]
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points."""
        from app.utils.distance import haversine_distance
        return haversine_distance(lat1, lng1, lat2, lng2)

