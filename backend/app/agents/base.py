"""Base agent class using OpenAI Agents SDK."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from agents import Agent, Runner
from datetime import datetime
import json

from app.core.config import settings
from app.core.prompt_cache import get_prompt_cache
from app.core.retry import retry_with_backoff, CircuitBreaker
from app.db.models import AgentExecutionLog
from sqlalchemy.ext.asyncio import AsyncSession


class BaseAgent(ABC):
    """Base class for all AI agents using OpenAI Agents SDK."""
    
    def __init__(self, agent_name: str, instructions: str, handoffs: Optional[List[str]] = None):
        self.agent_name = agent_name
        self.instructions = instructions
        self.handoffs = handoffs or []
        self.prompt_cache = get_prompt_cache()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60.0
        )
        
        # Create OpenAI Agent
        self.agent = Agent(
            name=agent_name,
            instructions=instructions,
            handoff_description=self.get_handoff_description(),
            handoffs=self.handoffs
        )
    
    @abstractmethod
    def get_handoff_description(self) -> str:
        """Get description for when this agent should hand off to others."""
        pass
    
    @abstractmethod
    def _get_fallback_response(self, context: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Get fallback response when agent fails."""
        pass
    
    def _build_user_message(self, context: Dict[str, Any]) -> str:
        """Build user message from context."""
        return f"Context:\n{json.dumps(context, indent=2)}\n\nPlease analyze and provide your response."
    
    def _parse_response(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse agent response."""
        try:
            # Try to parse as JSON
            return json.loads(content)
        except json.JSONDecodeError:
            # If not JSON, return as text
            return {"response": content, "raw": True}
    
    async def execute(
        self,
        context: Dict[str, Any],
        db: Optional[AsyncSession] = None,
        booking_id: Optional[str] = None,
        use_cache: bool = True,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute the agent with given context using OpenAI Agents SDK.
        
        Args:
            context: Input context for the agent
            db: Database session for logging
            booking_id: Optional booking ID for logging
            use_cache: Whether to use prompt cache
            session_id: Optional session ID for agent conversation
        
        Returns:
            Agent response
        """
        user_message = self._build_user_message(context)
        
        # Check cache
        if use_cache:
            cached_response = await self.prompt_cache.get(
                self.agent_name,
                self.instructions,
                context
            )
            if cached_response:
                return cached_response
        
        start_time = datetime.utcnow()
        execution_context = context.get("execution_context", "general")
        
        try:
            # Execute with retry and circuit breaker
            async def execute_with_retry():
                return await retry_with_backoff(
                    self._run_agent,
                    user_message=user_message,
                    session_id=session_id or f"session_{booking_id or 'default'}"
                )
            
            response_text = await self.circuit_breaker.call_async(execute_with_retry)
            
            execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Parse response
            response = self._parse_response(response_text, context)
            
            # Cache response
            if use_cache:
                await self.prompt_cache.set(
                    self.agent_name,
                    self.instructions,
                    context,
                    response
                )
            
            # Log execution
            if db:
                await self._log_execution(
                    db,
                    execution_context,
                    context,
                    response,
                    execution_time_ms,
                    success=True,
                    booking_id=booking_id
                )
            
            return response
            
        except Exception as e:
            execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Log failure
            if db:
                await self._log_execution(
                    db,
                    execution_context,
                    context,
                    None,
                    execution_time_ms,
                    success=False,
                    error_message=str(e),
                    booking_id=booking_id
                )
            
            # Return fallback response
            return self._get_fallback_response(context, str(e))
    
    async def _run_agent(self, user_message: str, session_id: str) -> str:
        """Run the agent using OpenAI Agents SDK Runner."""
        # Use Runner.run() class method with agent and message
        # The SDK handles model and API key from environment or passed parameters
        result = await Runner.run(
            self.agent,
            user_message,
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
            session_id=session_id
        )
        
        # Extract the final message content
        # The result should be a string or have a content attribute
        if isinstance(result, str):
            return result
        elif hasattr(result, 'messages') and result.messages:
            return result.messages[-1].content
        elif hasattr(result, 'content'):
            return result.content
        else:
            return str(result)
    
    async def _log_execution(
        self,
        db: AsyncSession,
        execution_context: str,
        input_data: Dict[str, Any],
        output_data: Optional[Dict[str, Any]],
        execution_time_ms: int,
        success: bool,
        error_message: Optional[str] = None,
        booking_id: Optional[str] = None
    ):
        """Log agent execution to database."""
        from uuid import UUID
        log = AgentExecutionLog(
            agent_name=self.agent_name,
            execution_context=execution_context,
            input_data=input_data,
            output_data=output_data,
            execution_time_ms=execution_time_ms,
            success=success,
            error_message=error_message,
            booking_id=UUID(booking_id) if booking_id else None
        )
        db.add(log)
        await db.flush()
