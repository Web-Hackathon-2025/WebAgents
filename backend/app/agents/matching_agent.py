"""Matching agent for intelligent provider matching using OpenAI Agents SDK."""
from typing import Dict, Any, List
import json

from app.agents.base import BaseAgent


class MatchingAgent(BaseAgent):
    """Agent for matching customers with best-fit service providers."""
    
    def __init__(self):
        instructions = """You are a service provider matching agent. Your role is to analyze customer requirements and find the best matching service providers.

Consider:
1. Service category and specific requirements
2. Geographic proximity (distance from customer)
3. Provider ratings and review sentiment
4. Provider availability for requested time
5. Pricing compatibility with customer budget
6. Provider's completion rate and reliability
7. Provider's specialization and experience
8. Recent performance trends

Return a JSON response with:
{
    "matches": [
        {
            "provider_id": "uuid",
            "match_score": 0-100,
            "reasoning": "explanation of why this provider is a good match",
            "strengths": ["list", "of", "strengths"],
            "concerns": ["any", "concerns"]
        }
    ],
    "summary": "overall matching summary"
}"""
        
        # Can hand off to scheduling agent if needed
        super().__init__(
            agent_name="matching_agent",
            instructions=instructions,
            handoffs=["scheduling_agent"]
        )
    
    def get_handoff_description(self) -> str:
        """Description for when to hand off to other agents."""
        return "Hand off to scheduling_agent when customer needs help finding available time slots after provider selection."
    
    def _parse_response(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse matching agent response."""
        import re
        
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # Try direct JSON parse
            return json.loads(content)
        except (json.JSONDecodeError, AttributeError):
            # Fallback: create response from text
            return {
                "matches": self._create_fallback_matches(context),
                "summary": content[:500] if content else "Matching analysis completed"
            }
    
    def _create_fallback_matches(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create fallback matches based on simple rules."""
        matches = []
        providers = context.get("available_providers", [])
        
        for provider in providers:
            score = 50.0  # Base score
            
            # Add score based on rating
            rating = provider.get("rating", 0)
            score += (rating - 3.0) * 10  # Boost for ratings above 3.0
            
            # Add score based on distance (closer is better)
            distance = provider.get("distance_km", 100)
            if distance < 5:
                score += 20
            elif distance < 10:
                score += 10
            
            # Add score based on completion rate
            completion_rate = provider.get("completion_rate", 0)
            score += (completion_rate - 80) * 0.2
            
            score = max(0, min(100, score))  # Clamp to 0-100
            
            matches.append({
                "provider_id": provider.get("id"),
                "match_score": round(score, 2),
                "reasoning": f"Based on rating ({rating}), distance ({distance}km), and completion rate ({completion_rate}%)",
                "strengths": [],
                "concerns": []
            })
        
        # Sort by match score descending
        matches.sort(key=lambda x: x["match_score"], reverse=True)
        return matches[:5]  # Return top 5
    
    def _get_fallback_response(self, context: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Get fallback response when matching agent fails."""
        return {
            "matches": self._create_fallback_matches(context),
            "summary": f"Fallback matching used due to error: {error}",
            "fallback": True
        }
