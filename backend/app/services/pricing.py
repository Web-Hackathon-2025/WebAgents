"""Pricing service using AI pricing agent."""
from typing import Dict, Any, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.agents.pricing_agent import PricingAgent
from app.db.models import Service, ProviderProfile, Booking as BookingModel


class PricingService:
    """Service for dynamic pricing recommendations."""
    
    def __init__(self):
        self.pricing_agent = PricingAgent()
    
    async def get_pricing_recommendation(
        self,
        db: AsyncSession,
        service_id: str,
        provider_id: str,
        booking_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get pricing recommendation for a service.
        
        Returns recommended price range.
        """
        # Get service details
        service_result = await db.execute(
            select(Service).where(Service.id == service_id)
        )
        service = service_result.scalar_one_or_none()
        
        if not service:
            return {}
        
        # Get provider details
        provider_result = await db.execute(
            select(ProviderProfile).where(ProviderProfile.id == provider_id)
        )
        provider = provider_result.scalar_one_or_none()
        
        if not provider:
            return {}
        
        # Get market average for this service category
        market_avg_result = await db.execute(
            select(func.avg(BookingModel.final_price))
            .join(Service)
            .where(Service.category_id == service.category_id)
            .where(BookingModel.status == "completed")
            .where(BookingModel.final_price.isnot(None))
        )
        market_average = float(market_avg_result.scalar() or service.base_price)
        
        # Prepare context for pricing agent
        context = {
            "service_id": str(service_id),
            "provider_id": str(provider_id),
            "base_price": float(service.base_price),
            "price_unit": service.price_unit,
            "market_average": market_average,
            "provider_rating": float(provider.rating_average),
            "provider_experience": provider.total_bookings,
            "execution_context": "pricing"
        }
        
        # Execute pricing agent
        agent_response = await self.pricing_agent.execute(
            context=context,
            db=db,
            booking_id=booking_id
        )
        
        return agent_response

