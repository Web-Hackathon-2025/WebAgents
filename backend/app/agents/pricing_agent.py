"""Pricing agent for dynamic pricing recommendations using OpenAI Agents SDK."""
from typing import Dict, Any

from app.agents.base import BaseAgent


class PricingAgent(BaseAgent):
    """Agent for providing dynamic pricing recommendations."""
    
    def __init__(self):
        instructions = """You are a pricing recommendation agent. Analyze market conditions and suggest fair pricing.

Consider:
1. Base service rates in the area
2. Provider's experience and ratings
3. Service complexity and requirements
4. Time of day/week (surge pricing)
5. Distance and travel costs
6. Seasonal demand patterns
7. Competitor pricing
8. Customer budget constraints

Return a JSON response with:
{
    "recommended_price": decimal,
    "price_range": {
        "min": decimal,
        "max": decimal
    },
    "reasoning": "explanation of pricing recommendation",
    "factors": {
        "base_rate": decimal,
        "experience_multiplier": decimal,
        "complexity_adjustment": decimal,
        "demand_adjustment": decimal,
        "distance_cost": decimal
    },
    "market_comparison": "how this compares to market rates"
}"""
        
        super().__init__(
            agent_name="pricing_agent",
            instructions=instructions,
            handoffs=[]
        )
    
    def get_handoff_description(self) -> str:
        """Description for when to hand off to other agents."""
        return "This agent handles pricing and typically doesn't hand off to other agents."
    
    def _parse_response(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse pricing agent response."""
        import re
        import json
        
        try:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(content)
        except (json.JSONDecodeError, AttributeError):
            return self._create_fallback_pricing(context)
    
    def _create_fallback_pricing(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback pricing based on simple rules."""
        base_price = float(context.get("base_price", 1000))
        market_average = float(context.get("market_average", base_price))
        rating = float(context.get("rating", 4.0))
        
        # Adjust based on rating
        rating_multiplier = 1.0 + ((rating - 4.0) * 0.1)
        
        # Use average of base price and market average
        recommended = (base_price + market_average) / 2 * rating_multiplier
        
        return {
            "recommended_price": round(recommended, 2),
            "price_range": {
                "min": round(recommended * 0.8, 2),
                "max": round(recommended * 1.2, 2)
            },
            "reasoning": f"Based on base price ({base_price}) and market average ({market_average})",
            "factors": {
                "base_rate": base_price,
                "experience_multiplier": rating_multiplier,
                "complexity_adjustment": 0,
                "demand_adjustment": 0,
                "distance_cost": 0
            },
            "market_comparison": "Fallback pricing calculation"
        }
    
    def _get_fallback_response(self, context: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Get fallback response when pricing agent fails."""
        pricing = self._create_fallback_pricing(context)
        pricing["reasoning"] = f"Fallback pricing used due to error: {error}"
        pricing["fallback"] = True
        return pricing
