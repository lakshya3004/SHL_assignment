import functools
from typing import Any, Dict
from loguru import logger

class SimpleCache:
    """
    Lightweight in-memory cache to reduce redundant embedding 
    and retrieval operations during multi-turn conversations.
    """
    
    _cache: Dict[str, Any] = {}
    MAX_SIZE = 500

    @classmethod
    def get(cls, key: str) -> Any:
        return cls._cache.get(key)

    @classmethod
    def set(cls, key: str, value: Any):
        if len(cls._cache) >= cls.MAX_SIZE:
            # Simple eviction: clear entire cache
            logger.info("Cache full, clearing in-memory storage.")
            cls._cache.clear()
        cls._cache[key] = value

def cache_query(func):
    """Decorator for caching function results based on arguments."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        # Create a cache key from arguments (simple string representation)
        key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
        
        cached_val = SimpleCache.get(key)
        if cached_val is not None:
            logger.debug(f"Cache hit for {func.__name__}")
            return cached_val
            
        result = await func(*args, **kwargs)
        SimpleCache.set(key, result)
        return result
    return wrapper
