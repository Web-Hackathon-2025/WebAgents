"""Centralized agent communication hub."""
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict
import asyncio
from uuid import uuid4

from app.core.config import settings


class AgentMessage:
    """Message between agents."""
    def __init__(
        self,
        sender: str,
        receiver: str,
        message_type: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None
    ):
        self.id = str(uuid4())
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type
        self.payload = payload
        self.correlation_id = correlation_id or str(uuid4())
        self.timestamp = asyncio.get_event_loop().time()


class AgentCommunicationHub:
    """Central hub for agent communication and coordination."""
    
    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.message_queue: Dict[str, List[AgentMessage]] = defaultdict(list)
        self.response_handlers: Dict[str, Callable] = {}
        self.pending_responses: Dict[str, asyncio.Future] = {}
    
    def register_agent(
        self,
        agent_name: str,
        agent_type: str,
        capabilities: List[str],
        handler: Optional[Callable] = None
    ):
        """Register an agent with the hub."""
        self.agents[agent_name] = {
            "name": agent_name,
            "type": agent_type,
            "capabilities": capabilities,
            "handler": handler,
            "status": "active",
            "registered_at": asyncio.get_event_loop().time()
        }
    
    def unregister_agent(self, agent_name: str):
        """Unregister an agent."""
        if agent_name in self.agents:
            del self.agents[agent_name]
        if agent_name in self.message_queue:
            del self.message_queue[agent_name]
    
    async def send_message(
        self,
        sender: str,
        receiver: str,
        message_type: str,
        payload: Dict[str, Any],
        wait_for_response: bool = False,
        timeout: float = 30.0
    ) -> Optional[AgentMessage]:
        """Send a message from one agent to another."""
        message = AgentMessage(sender, receiver, message_type, payload)
        
        if receiver not in self.agents:
            raise ValueError(f"Agent {receiver} not registered")
        
        # Add to message queue
        self.message_queue[receiver].append(message)
        
        if wait_for_response:
            future = asyncio.Future()
            self.pending_responses[message.correlation_id] = future
            
            try:
                response = await asyncio.wait_for(future, timeout=timeout)
                return response
            except asyncio.TimeoutError:
                if message.correlation_id in self.pending_responses:
                    del self.pending_responses[message.correlation_id]
                return None
        
        return message
    
    async def get_messages(self, agent_name: str) -> List[AgentMessage]:
        """Get pending messages for an agent."""
        messages = self.message_queue[agent_name].copy()
        self.message_queue[agent_name].clear()
        return messages
    
    def send_response(self, correlation_id: str, response: AgentMessage):
        """Send a response to a pending request."""
        if correlation_id in self.pending_responses:
            future = self.pending_responses[correlation_id]
            if not future.done():
                future.set_result(response)
            del self.pending_responses[correlation_id]
    
    def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get status of an agent."""
        return self.agents.get(agent_name)
    
    def list_agents(self) -> List[str]:
        """List all registered agents."""
        return list(self.agents.keys())
    
    def find_agents_by_capability(self, capability: str) -> List[str]:
        """Find agents with a specific capability."""
        return [
            name for name, info in self.agents.items()
            if capability in info["capabilities"]
        ]


# Global agent hub instance
_agent_hub: Optional[AgentCommunicationHub] = None


def get_agent_hub() -> AgentCommunicationHub:
    """Get the global agent communication hub."""
    global _agent_hub
    if _agent_hub is None:
        _agent_hub = AgentCommunicationHub()
    return _agent_hub

