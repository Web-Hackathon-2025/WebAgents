"""Recommendation agent for personalized provider recommendations."""
from typing import Dict, Any, List

from app.agents.base import BaseAgent


class RecommendationAgent(BaseAgent):
    """Agent for personalized provider recommendations based on user history."""
    
    def __init__(self):
        super().__init__("recommendation_agent")
    
    def get_system_prompt(self) -> str:
        return """You are a recommendation agent. Suggest service providers based on user preferences and history.

Consider:
1. User's past bookings and ratings
2. Services frequently used
3. Preferred price ranges
4. Location patterns
5. Time preferences
6. Providers user has rated highly
7. Similar users' preferences
8. Trending providers in user's area

Return a JSON response with:
{
    "recommendations": [
        {
            "provider_id": "uuid",
            "confidence": 0-1,
            "reasoning": "why this provider is recommended",
            "match_factors": ["factor1", "factor2"]
        }
    ],
    "personalization_insights": {
        "preferred_categories": ["list"],
        "price_range": {"min": decimal, "max": decimal},
        "location_preference": "description"
    },
    "summary": "overall recommendation summary"
}"""
    
    def _parse_response(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse recommendation agent response."""
        import json
        import re
        
        try:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(content)
        except (json.JSONDecodeError, AttributeError):
            return {
                "recommendations": self._create_fallback_recommendations(context),
                "personalization_insights": {},
                "summary": "Fallback recommendations"
            }
    
    def _create_fallback_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create fallback recommendations based on simple rules."""
        recommendations = []
        available_providers = context.get("available_providers", [])
        user_history = context.get("user_history", {})
        
        # Sort by rating and distance
        sorted_providers = sorted(
            available_providers,
            key=lambda p: (
                -float(p.get("rating", 0)),  # Higher rating first
                float(p.get("distance_km", 100))  # Closer distance second
            )
        )
        
        for i, provider in enumerate(sorted_providers[:10]):
            confidence = 0.8 - (i * 0.05)  # Decreasing confidence
            
            recommendations.append({
                "provider_id": provider.get("id"),
                "confidence": round(confidence, 2),
                "reasoning": f"High rating ({provider.get('rating')}) and nearby ({provider.get('distance_km')}km)",
                "match_factors": ["rating", "proximity"]
            })
        
        return recommendations
    
    def _get_fallback_response(self, context: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Get fallback response when recommendation agent fails."""
        return {
            "recommendations": self._create_fallback_recommendations(context),
            "personalization_insights": {},
            "summary": f"Fallback recommendations used due to error: {error}",
            "fallback": True
        }

