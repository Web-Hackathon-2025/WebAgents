"""Redis client for caching and session management."""
import redis.asyncio as redis
import json
from typing import Optional, Any
from app.core.config import settings


class RedisClient:
    """Async Redis client wrapper."""
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self.client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.client.ping()
        except Exception as e:
            self.client = None
            raise ConnectionError(f"Failed to connect to Redis at {settings.REDIS_URL}: {str(e)}")
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.client:
            await self.client.close()
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        if not self.client:
            await self.connect()
        return await self.client.get(key)
    
    async def set(self, key: str, value: Any, ex: Optional[int] = None):
        """Set value in Redis with optional expiration."""
        if not self.client:
            await self.connect()
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await self.client.set(key, value, ex=ex)
    
    async def delete(self, key: str):
        """Delete key from Redis."""
        if not self.client:
            await self.connect()
        await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self.client:
            await self.connect()
        return bool(await self.client.exists(key))
    
    async def expire(self, key: str, seconds: int):
        """Set expiration on key."""
        if not self.client:
            await self.connect()
        await self.client.expire(key, seconds)
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get and parse JSON value."""
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set_json(self, key: str, value: Any, ex: Optional[int] = None):
        """Set JSON value."""
        await self.set(key, value, ex=ex)


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """Dependency for getting Redis client."""
    if not redis_client.client:
        await redis_client.connect()
    return redis_client

