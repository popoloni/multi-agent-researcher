"""
Cache Service for Phase 4 Kenobi Code Analysis Agent
Implements Redis-based caching with fallback to in-memory storage
"""

import json
import pickle
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import asyncio
from dataclasses import dataclass

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: Any
    timestamp: datetime
    ttl: Optional[int] = None
    access_count: int = 0
    last_accessed: datetime = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.timestamp
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.ttl is None:
            return False
        return datetime.now() > self.timestamp + timedelta(seconds=self.ttl)
    
    def access(self):
        """Mark entry as accessed"""
        self.access_count += 1
        self.last_accessed = datetime.now()


class InMemoryCache:
    """In-memory cache implementation as fallback"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, CacheEntry] = {}
        self.max_size = max_size
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                if entry.is_expired():
                    del self.cache[key]
                    return None
                entry.access()
                return entry.data
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        async with self._lock:
            # Evict if at max size
            if len(self.cache) >= self.max_size and key not in self.cache:
                await self._evict_lru()
            
            self.cache[key] = CacheEntry(
                data=value,
                timestamp=datetime.now(),
                ttl=ttl
            )
            return True
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        async with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                if entry.is_expired():
                    del self.cache[key]
                    return False
                return True
            return False
    
    async def clear(self) -> bool:
        """Clear all cache entries"""
        async with self._lock:
            self.cache.clear()
            return True
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """Get all keys matching pattern"""
        async with self._lock:
            # Simple pattern matching (only supports * wildcard)
            if pattern == "*":
                return list(self.cache.keys())
            
            # Remove expired entries first
            expired_keys = [k for k, v in self.cache.items() if v.is_expired()]
            for k in expired_keys:
                del self.cache[k]
            
            if "*" in pattern:
                prefix = pattern.replace("*", "")
                return [k for k in self.cache.keys() if k.startswith(prefix)]
            else:
                return [k for k in self.cache.keys() if k == pattern]
    
    async def _evict_lru(self):
        """Evict least recently used entry"""
        if not self.cache:
            return
        
        lru_key = min(self.cache.keys(), key=lambda k: self.cache[k].last_accessed)
        del self.cache[lru_key]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        async with self._lock:
            total_entries = len(self.cache)
            expired_entries = sum(1 for entry in self.cache.values() if entry.is_expired())
            total_accesses = sum(entry.access_count for entry in self.cache.values())
            
            return {
                "total_entries": total_entries,
                "expired_entries": expired_entries,
                "active_entries": total_entries - expired_entries,
                "total_accesses": total_accesses,
                "cache_type": "in_memory",
                "max_size": self.max_size
            }


class RedisCache:
    """Redis-based cache implementation"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", db: int = 0):
        self.redis_url = redis_url
        self.db = db
        self.redis_client: Optional[redis.Redis] = None
        self._connected = False
    
    async def connect(self) -> bool:
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(self.redis_url, db=self.db, decode_responses=False)
            await self.redis_client.ping()
            self._connected = True
            return True
        except Exception as e:
            print(f"Redis connection failed: {e}")
            self._connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self._connected = False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        if not self._connected:
            return None
        
        try:
            data = await self.redis_client.get(key)
            if data is None:
                return None
            
            # Try to deserialize as JSON first, then pickle
            try:
                return json.loads(data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return pickle.loads(data)
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache"""
        if not self._connected:
            return False
        
        try:
            # Try to serialize as JSON first, then pickle
            try:
                data = json.dumps(value).encode('utf-8')
            except (TypeError, ValueError):
                data = pickle.dumps(value)
            
            if ttl:
                await self.redis_client.setex(key, ttl, data)
            else:
                await self.redis_client.set(key, data)
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from Redis cache"""
        if not self._connected:
            return False
        
        try:
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache"""
        if not self._connected:
            return False
        
        try:
            result = await self.redis_client.exists(key)
            return result > 0
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all cache entries"""
        if not self._connected:
            return False
        
        try:
            await self.redis_client.flushdb()
            return True
        except Exception as e:
            print(f"Redis clear error: {e}")
            return False
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """Get all keys matching pattern"""
        if not self._connected:
            return []
        
        try:
            keys = await self.redis_client.keys(pattern)
            return [key.decode('utf-8') if isinstance(key, bytes) else key for key in keys]
        except Exception as e:
            print(f"Redis keys error: {e}")
            return []
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics"""
        if not self._connected:
            return {"cache_type": "redis", "connected": False}
        
        try:
            info = await self.redis_client.info()
            return {
                "cache_type": "redis",
                "connected": True,
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "connected_clients": info.get("connected_clients", 0)
            }
        except Exception as e:
            print(f"Redis stats error: {e}")
            return {"cache_type": "redis", "connected": False, "error": str(e)}


class CacheService:
    """Main cache service with Redis and in-memory fallback"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", use_redis: bool = True):
        self.use_redis = use_redis and REDIS_AVAILABLE
        self.redis_cache = RedisCache(redis_url) if self.use_redis else None
        self.memory_cache = InMemoryCache()
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
            "errors": 0
        }
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize cache service"""
        if self._initialized:
            return True
        
        if self.use_redis and self.redis_cache:
            redis_connected = await self.redis_cache.connect()
            if not redis_connected:
                print("Redis connection failed, falling back to in-memory cache")
                self.use_redis = False
        
        self._initialized = True
        return True
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            # Try Redis first if available
            if self.use_redis and self.redis_cache:
                value = await self.redis_cache.get(key)
                if value is not None:
                    self.cache_stats["hits"] += 1
                    return value
            
            # Fallback to in-memory cache
            value = await self.memory_cache.get(key)
            if value is not None:
                self.cache_stats["hits"] += 1
                return value
            
            self.cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            self.cache_stats["errors"] += 1
            print(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            success = False
            
            # Try Redis first if available
            if self.use_redis and self.redis_cache:
                success = await self.redis_cache.set(key, value, ttl)
            
            # Always set in memory cache as backup
            memory_success = await self.memory_cache.set(key, value, ttl)
            
            if success or memory_success:
                self.cache_stats["sets"] += 1
                return True
            
            return False
            
        except Exception as e:
            self.cache_stats["errors"] += 1
            print(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            success = False
            
            # Delete from Redis if available
            if self.use_redis and self.redis_cache:
                success = await self.redis_cache.delete(key)
            
            # Delete from memory cache
            memory_success = await self.memory_cache.delete(key)
            
            if success or memory_success:
                self.cache_stats["deletes"] += 1
                return True
            
            return False
            
        except Exception as e:
            self.cache_stats["errors"] += 1
            print(f"Cache delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            # Check Redis first if available
            if self.use_redis and self.redis_cache:
                if await self.redis_cache.exists(key):
                    return True
            
            # Check memory cache
            return await self.memory_cache.exists(key)
            
        except Exception as e:
            self.cache_stats["errors"] += 1
            print(f"Cache exists error: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all cache entries"""
        try:
            success = False
            
            # Clear Redis if available
            if self.use_redis and self.redis_cache:
                success = await self.redis_cache.clear()
            
            # Clear memory cache
            memory_success = await self.memory_cache.clear()
            
            return success or memory_success
            
        except Exception as e:
            self.cache_stats["errors"] += 1
            print(f"Cache clear error: {e}")
            return False
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """Get all keys matching pattern"""
        try:
            all_keys = set()
            
            # Get keys from Redis if available
            if self.use_redis and self.redis_cache:
                redis_keys = await self.redis_cache.keys(pattern)
                all_keys.update(redis_keys)
            
            # Get keys from memory cache
            memory_keys = await self.memory_cache.keys(pattern)
            all_keys.update(memory_keys)
            
            return list(all_keys)
            
        except Exception as e:
            self.cache_stats["errors"] += 1
            print(f"Cache keys error: {e}")
            return []
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        try:
            stats = {
                "service_stats": self.cache_stats.copy(),
                "redis_enabled": self.use_redis,
                "redis_available": REDIS_AVAILABLE
            }
            
            # Get Redis stats if available
            if self.use_redis and self.redis_cache:
                stats["redis_stats"] = await self.redis_cache.get_stats()
            
            # Get memory cache stats
            stats["memory_stats"] = await self.memory_cache.get_stats()
            
            # Calculate hit rate
            total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
            if total_requests > 0:
                stats["hit_rate"] = self.cache_stats["hits"] / total_requests
            else:
                stats["hit_rate"] = 0.0
            
            return stats
            
        except Exception as e:
            return {"error": f"Failed to get cache stats: {str(e)}"}
    
    def generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from prefix and arguments"""
        # Create a deterministic key from arguments
        key_parts = [prefix]
        
        # Add positional arguments
        for arg in args:
            if isinstance(arg, (str, int, float, bool)):
                key_parts.append(str(arg))
            else:
                # Hash complex objects
                key_parts.append(hashlib.md5(str(arg).encode()).hexdigest()[:8])
        
        # Add keyword arguments (sorted for consistency)
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (str, int, float, bool)):
                key_parts.append(f"{k}:{v}")
            else:
                key_parts.append(f"{k}:{hashlib.md5(str(v).encode()).hexdigest()[:8]}")
        
        return ":".join(key_parts)
    
    async def get_or_set(self, key: str, factory_func, ttl: Optional[int] = None) -> Any:
        """Get value from cache or set it using factory function"""
        # Try to get from cache first
        value = await self.get(key)
        if value is not None:
            return value
        
        # Generate value using factory function
        try:
            if asyncio.iscoroutinefunction(factory_func):
                value = await factory_func()
            else:
                value = factory_func()
            
            # Set in cache
            await self.set(key, value, ttl)
            return value
            
        except Exception as e:
            print(f"Factory function error: {e}")
            return None
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern"""
        try:
            keys = await self.keys(pattern)
            deleted_count = 0
            
            for key in keys:
                if await self.delete(key):
                    deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            print(f"Pattern invalidation error: {e}")
            return 0
    
    async def close(self):
        """Close cache connections"""
        if self.use_redis and self.redis_cache:
            await self.redis_cache.disconnect()


# Global cache service instance
cache_service = CacheService()


# Cache decorators for common use cases
def cache_result(ttl: int = 3600, key_prefix: str = "result"):
    """Decorator to cache function results"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_service.generate_cache_key(key_prefix, func.__name__, *args, **kwargs)
            
            # Try to get from cache
            cached_result = await cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            await cache_service.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator


def cache_repository_analysis(ttl: int = 1800):  # 30 minutes
    """Decorator specifically for repository analysis caching"""
    return cache_result(ttl=ttl, key_prefix="repo_analysis")


def cache_code_quality(ttl: int = 900):  # 15 minutes
    """Decorator specifically for code quality analysis caching"""
    return cache_result(ttl=ttl, key_prefix="code_quality")


def cache_dependency_analysis(ttl: int = 1200):  # 20 minutes
    """Decorator specifically for dependency analysis caching"""
    return cache_result(ttl=ttl, key_prefix="dependency_analysis")