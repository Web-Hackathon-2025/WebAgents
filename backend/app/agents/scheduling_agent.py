"""Scheduling agent for optimal time slot suggestions."""
from typing import Dict, Any, List
from datetime import datetime, timedelta

from app.agents.base import BaseAgent


class SchedulingAgent(BaseAgent):
    """Agent for finding optimal time slots and resolving scheduling conflicts."""
    
    def __init__(self):
        super().__init__("scheduling_agent")
    
    def get_system_prompt(self) -> str:
        return """You are a scheduling optimization agent. Your role is to suggest the best time slots for service bookings.

Consider:
1. Customer's preferred time windows
2. Provider's availability schedule
3. Provider's existing bookings
4. Travel time between appointments
5. Service duration estimates
6. Buffer time for preparation/cleanup
7. Peak vs off-peak hours
8. Weather conditions (if relevant)

Return a JSON response with:
{
    "suggested_slots": [
        {
            "start_datetime": "ISO datetime string",
            "end_datetime": "ISO datetime string",
            "confidence": 0-1,
            "reasoning": "why this slot is optimal",
            "conflicts": []
        }
    ],
    "alternatives": [
        {
            "start_datetime": "ISO datetime string",
            "end_datetime": "ISO datetime string",
            "reasoning": "alternative option"
        }
    ],
    "recommendations": "overall scheduling recommendations"
}"""
    
    def _parse_response(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse scheduling agent response."""
        import json
        import re
        
        try:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(content)
        except (json.JSONDecodeError, AttributeError):
            return {
                "suggested_slots": self._create_fallback_slots(context),
                "alternatives": [],
                "recommendations": content[:500] if content else "Scheduling analysis completed"
            }
    
    def _create_fallback_slots(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create fallback time slots based on availability."""
        slots = []
        preferred_date = context.get("preferred_date")
        preferred_time_start = context.get("preferred_time_start")
        preferred_time_end = context.get("preferred_time_end")
        available_slots = context.get("available_slots", [])
        
        if not available_slots:
            # Generate default slots if none provided
            if preferred_date and preferred_time_start:
                base_datetime = datetime.fromisoformat(f"{preferred_date}T{preferred_time_start}")
                for i in range(3):
                    slot_start = base_datetime + timedelta(hours=i*2)
                    slot_end = slot_start + timedelta(hours=2)
                    slots.append({
                        "start_datetime": slot_start.isoformat(),
                        "end_datetime": slot_end.isoformat(),
                        "confidence": 0.7 - (i * 0.1),
                        "reasoning": f"Suggested slot {i+1} based on preferred time",
                        "conflicts": []
                    })
        else:
            # Use provided available slots
            for slot in available_slots[:5]:
                slots.append({
                    "start_datetime": slot.get("start", ""),
                    "end_datetime": slot.get("end", ""),
                    "confidence": 0.8,
                    "reasoning": "Available slot from provider schedule",
                    "conflicts": []
                })
        
        return slots
    
    def _get_fallback_response(self, context: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Get fallback response when scheduling agent fails."""
        return {
            "suggested_slots": self._create_fallback_slots(context),
            "alternatives": [],
            "recommendations": f"Fallback scheduling used due to error: {error}",
            "fallback": True
        }

