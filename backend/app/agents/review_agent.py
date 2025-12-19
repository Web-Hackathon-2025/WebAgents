"""Review analysis agent for sentiment analysis and fake review detection using OpenAI Agents SDK."""
from typing import Dict, Any

from app.agents.base import BaseAgent


class ReviewAnalysisAgent(BaseAgent):
    """Agent for analyzing review sentiment and detecting fake reviews."""
    
    def __init__(self):
        instructions = """You are a review analysis agent. Analyze customer reviews for quality and authenticity.

Evaluate:
1. Sentiment (positive, neutral, negative)
2. Specificity and detail level
3. Language patterns (generic vs specific)
4. Consistency with booking details
5. Potential fake review indicators
6. Key themes and topics mentioned
7. Actionable feedback for provider

Return a JSON response with:
{
    "sentiment_score": -1 to 1,
    "quality_score": 0 to 1,
    "is_likely_fake": boolean,
    "sentiment": "positive|neutral|negative",
    "key_themes": ["list", "of", "themes"],
    "actionable_feedback": ["list", "of", "feedback", "items"],
    "summary": "overall analysis summary",
    "red_flags": ["any", "suspicious", "indicators"]
}"""
        
        super().__init__(
            agent_name="review_agent",
            instructions=instructions,
            handoffs=[]
        )
    
    def get_handoff_description(self) -> str:
        """Description for when to hand off to other agents."""
        return "This agent handles review analysis and typically doesn't hand off to other agents."
    
    def _parse_response(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse review analysis agent response."""
        import re
        import json
        
        try:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(content)
        except (json.JSONDecodeError, AttributeError):
            return self._create_fallback_analysis(context)
    
    def _create_fallback_analysis(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback analysis based on rating."""
        rating = int(context.get("rating", 3))
        review_text = context.get("review_text", "")
        
        # Simple sentiment based on rating
        if rating >= 4:
            sentiment_score = 0.7
            sentiment = "positive"
        elif rating == 3:
            sentiment_score = 0.0
            sentiment = "neutral"
        else:
            sentiment_score = -0.7
            sentiment = "negative"
        
        # Quality score based on text length
        text_length = len(review_text) if review_text else 0
        quality_score = min(1.0, text_length / 100)  # Higher quality for longer reviews
        
        return {
            "sentiment_score": round(sentiment_score, 2),
            "quality_score": round(quality_score, 2),
            "is_likely_fake": False,
            "sentiment": sentiment,
            "key_themes": [],
            "actionable_feedback": [],
            "summary": f"Rating: {rating}/5",
            "red_flags": []
        }
    
    def _get_fallback_response(self, context: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Get fallback response when review agent fails."""
        analysis = self._create_fallback_analysis(context)
        analysis["summary"] = f"Fallback analysis used due to error: {error}"
        analysis["fallback"] = True
        return analysis
