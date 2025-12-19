"""Prompt caching for AI agents to reduce API calls."""
import hashlib
import json
from typing import Optional, Dict, Any
from app.core.redis_client import get_redis


class PromptCache:
    """Cache for AI agent prompts and responses."""
    
    def __init__(self, ttl: int = 86400):  # 24 hours default
        self.ttl = ttl
    
    def _hash_prompt(self, agent_name: str, prompt: str, context: Dict[str, Any]) -> str:
        """Generate hash for prompt and context."""
        cache_key = f"{agent_name}:{prompt}:{json.dumps(context, sort_keys=True)}"
        return hashlib.sha256(cache_key.encode()).hexdigest()
    
    async def get(self, agent_name: str, prompt: str, context: Dict[str, Any]) -> Optional[Any]:
        """Get cached response."""
        redis = await get_redis()
        cache_key = f"agent:prompt:{self._hash_prompt(agent_name, prompt, context)}"
        return await redis.get_json(cache_key)
    
    async def set(self, agent_name: str, prompt: str, context: Dict[str, Any], response: Any):
        """Cache response."""
        redis = await get_redis()
        cache_key = f"agent:prompt:{self._hash_prompt(agent_name, prompt, context)}"
        await redis.set_json(cache_key, response, ex=self.ttl)
    
    async def invalidate(self, agent_name: str):
        """Invalidate all cached prompts for an agent."""
        # In production, use Redis SCAN to find and delete keys
        # For now, this is a placeholder
        pass


# Global prompt cache instance
_prompt_cache: Optional[PromptCache] = None


def get_prompt_cache() -> PromptCache:
    """Get the global prompt cache."""
    global _prompt_cache
    if _prompt_cache is None:
        _prompt_cache = PromptCache()
    return _prompt_cache

