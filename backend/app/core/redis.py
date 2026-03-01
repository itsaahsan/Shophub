"""Redis connection and caching helpers (Upstash compatible)."""

import json
from typing import Any, Optional

import redis.asyncio as redis

from app.core.config import settings

redis_client: redis.Redis = None  # type: ignore


async def connect_redis() -> None:
    """Initialize Redis connection pool."""
    global redis_client
    
    # Fallback to local redis if URL is empty
    url = settings.REDIS_URL or "redis://localhost:6379"
    
    try:
        redis_client = redis.from_url(
            url,
            encoding="utf-8",
            decode_responses=True,
        )
        # Test connection
        await redis_client.ping()
        print(f"Connected to Redis at {url}")
    except Exception as e:
        print(f"Warning: Failed to connect to Redis at {url}: {e}")
        redis_client = None


async def close_redis() -> None:
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()


async def cache_get(key: str) -> Optional[Any]:
    """Retrieve a value from cache."""
    if not redis_client:
        return None
    try:
        val = await redis_client.get(key)
        return json.loads(val) if val else None
    except Exception:
        return None


async def cache_set(key: str, value: Any, ttl: int = 300) -> None:
    """Set a value in cache with TTL (seconds)."""
    if redis_client:
        try:
            await redis_client.set(key, json.dumps(value), ex=ttl)
        except Exception:
            pass


async def cache_delete_pattern(pattern: str) -> None:
    """Delete all keys matching a pattern (e.g. 'products:*')."""
    if not redis_client:
        return
    
    try:
        # scan_iter is efficient for large datasets
        keys = []
        async for key in redis_client.scan_iter(pattern):
            keys.append(key)
        
        if keys:
            await redis_client.delete(*keys)
    except Exception:
        pass
