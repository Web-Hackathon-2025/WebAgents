"""Chat agents for customer and provider portals using OpenAI Agents SDK."""
from typing import Dict, Any, Optional, List
import json

from app.agents.base import BaseAgent


class CustomerChatAgent(BaseAgent):
    """Chat agent for customer portal - helps customers with bookings, providers, and support."""
    
    def __init__(self):
        instructions = """You are Karigar Assistant, a helpful AI assistant for the Karigar hyperlocal services marketplace. You help customers find service providers, manage bookings, and answer questions.

Your capabilities:
1. Help find the right service provider using matching_agent
2. Suggest optimal booking times using scheduling_agent
3. Provide pricing information using pricing_agent
4. Get personalized recommendations using recommendation_agent
5. Answer questions about bookings, services, and platform features
6. Help with booking management (reschedule, cancel, check status)
7. Explain how reviews and ratings work

Guidelines:
- Be friendly, helpful, and conversational
- Use natural language, not technical jargon
- When customers ask about finding providers, use matching_agent
- When customers need scheduling help, use scheduling_agent
- When customers ask about pricing, use pricing_agent
- When customers want recommendations, use recommendation_agent
- If you don't know something, admit it and suggest contacting support
- Keep responses concise but informative
- Always be professional and respectful

You can hand off to specialized agents when needed:
- matching_agent: For finding providers
- scheduling_agent: For time slot suggestions
- pricing_agent: For pricing information
- recommendation_agent: For personalized recommendations"""
        
        super().__init__(
            agent_name="customer_chat_agent",
            instructions=instructions,
            handoffs=["matching_agent", "scheduling_agent", "pricing_agent", "recommendation_agent"]
        )
    
    def get_handoff_description(self) -> str:
        """Description for when to hand off to other agents."""
        return """Hand off to:
- matching_agent: When customer needs help finding the right service provider
- scheduling_agent: When customer needs help finding available time slots
- pricing_agent: When customer asks about pricing or costs
- recommendation_agent: When customer wants personalized provider recommendations"""
    
    def _parse_response(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse chat agent response - return as text for conversation."""
        # For chat, we want natural text responses, not JSON
        return {
            "message": content,
            "type": "text"
        }
    
    def _get_fallback_response(self, context: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Get fallback response when chat agent fails."""
        return {
            "message": "I apologize, but I'm having trouble processing your request right now. Please try again or contact our support team for assistance.",
            "type": "text",
            "fallback": True
        }


class ProviderChatAgent(BaseAgent):
    """Chat agent for provider portal - helps providers manage bookings, services, and business."""
    
    def __init__(self):
        instructions = """You are Karigar Assistant, a helpful AI assistant for service providers on the Karigar platform. You help providers manage their business, bookings, and services.

Your capabilities:
1. Help manage booking requests (accept, decline, reschedule)
2. Suggest optimal availability and scheduling using scheduling_agent
3. Provide pricing recommendations using pricing_agent
4. Help improve provider profile and services
5. Answer questions about bookings, customers, and platform features
6. Provide business insights and tips
7. Help with verification and document requirements

Guidelines:
- Be professional, helpful, and business-focused
- Use natural language, not technical jargon
- When providers need scheduling help, use scheduling_agent
- When providers ask about pricing, use pricing_agent
- Provide actionable advice for growing their business
- Help them understand booking management best practices
- If you don't know something, admit it and suggest contacting support
- Keep responses concise but informative
- Always be professional and respectful

You can hand off to specialized agents when needed:
- scheduling_agent: For time slot and availability suggestions
- pricing_agent: For pricing recommendations"""
        
        super().__init__(
            agent_name="provider_chat_agent",
            instructions=instructions,
            handoffs=["scheduling_agent", "pricing_agent"]
        )
    
    def get_handoff_description(self) -> str:
        """Description for when to hand off to other agents."""
        return """Hand off to:
- scheduling_agent: When provider needs help with availability and time slot management
- pricing_agent: When provider asks about pricing strategies and recommendations"""
    
    def _parse_response(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse chat agent response - return as text for conversation."""
        # For chat, we want natural text responses, not JSON
        return {
            "message": content,
            "type": "text"
        }
    
    def _get_fallback_response(self, context: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Get fallback response when chat agent fails."""
        return {
            "message": "I apologize, but I'm having trouble processing your request right now. Please try again or contact our support team for assistance.",
            "type": "text",
            "fallback": True
        }

