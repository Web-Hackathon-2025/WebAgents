"""Base agent class for all AI agents."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import openai
import asyncio
from datetime import datetime

from app.core.config import settings
from app.core.prompt_cache import get_prompt_cache
from app.core.retry import retry_with_backoff, CircuitBreaker
from app.db.models import AgentExecutionLog
from sqlalchemy.ext.asyncio import AsyncSession


class BaseAgent(ABC):
    """Base class for all AI agents."""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.provider = settings.AI_PROVIDER
        
        # Configure AI client based on provider
        if self.provider == "gemini":
            # Gemini via OpenAI-compatible API
            self.client = openai.AsyncOpenAI(
                api_key=settings.GEMINI_API_KEY,
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            self.model = settings.GEMINI_MODEL
        else:
            # OpenAI
            self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL
            
        self.prompt_cache = get_prompt_cache()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60.0
        )
        self.timeout = settings.AI_TIMEOUT_SECONDS
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass
    
    async def execute(
        self,
        context: Dict[str, Any],
        db: Optional[AsyncSession] = None,
        booking_id: Optional[str] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Execute the agent with given context.
        
        Args:
            context: Input context for the agent
            db: Database session for logging
            booking_id: Optional booking ID for logging
            use_cache: Whether to use prompt cache
        
        Returns:
            Agent response
        """
        system_prompt = self.get_system_prompt()
        user_prompt = self._build_user_prompt(context)
        
        # Check cache
        if use_cache:
            cached_response = await self.prompt_cache.get(
                self.agent_name,
                system_prompt,
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
                    self._call_ai,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    context=context
                )
            
            # Add timeout to prevent hanging
            response = await asyncio.wait_for(
                self.circuit_breaker.call_async(execute_with_retry),
                timeout=self.timeout
            )
            
            execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Cache response
            if use_cache:
                await self.prompt_cache.set(
                    self.agent_name,
                    system_prompt,
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
            
        except asyncio.TimeoutError as e:
            execution_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            error_msg = f"AI request timed out after {self.timeout}s"
            
            # Log failure
            if db:
                await self._log_execution(
                    db,
                    execution_context,
                    context,
                    None,
                    execution_time_ms,
                    success=False,
                    error_message=error_msg,
                    booking_id=booking_id
                )
            
            # Return fallback response
            return self._get_fallback_response(context, error_msg)
            
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
    
    async def _call_ai(
        self,
        system_prompt: str,
        user_prompt: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call AI API (Gemini or OpenAI)."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        return self._parse_response(content, context)
    
    def _build_user_prompt(self, context: Dict[str, Any]) -> str:
        """Build user prompt from context."""
        import json
        return f"Context:\n{json.dumps(context, indent=2)}\n\nPlease analyze and provide your response."
    
    def _parse_response(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse agent response."""
        import json
        try:
            # Try to parse as JSON
            return json.loads(content)
        except json.JSONDecodeError:
            # If not JSON, return as text
            return {"response": content, "raw": True}
    
    @abstractmethod
    def _get_fallback_response(self, context: Dict[str, Any], error: str) -> Dict[str, Any]:
        """Get fallback response when agent fails."""
        pass
    
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

