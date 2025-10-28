"""
Redis configuration for distributed caching and session management
"""

import redis
import json
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import structlog
from functools import wraps
import pickle
import hashlib

from app.core.config import settings

logger = structlog.get_logger()


class RedisManager:
    """Redis connection and operations manager"""
    
    def __init__(self):
        self.redis_client = None
        self.is_connected = False
        
    def connect(self):
        """Initialize Redis connection"""
        try:
            # Try to connect to Redis
            self.redis_client = redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                db=getattr(settings, 'REDIS_DB', 0),
                password=getattr(settings, 'REDIS_PASSWORD', None),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            self.redis_client.ping()
            self.is_connected = True
            logger.info("Redis connected successfully")
            
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Falling back to in-memory cache")
            self.redis_client = None
            self.is_connected = False
    
    def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            self.redis_client.close()
            self.is_connected = False
            logger.info("Redis disconnected")
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a key-value pair with optional expiration"""
        try:
            if not self.is_connected:
                return False
                
            # Serialize complex objects
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            elif not isinstance(value, (str, int, float)):
                value = pickle.dumps(value)
                
            result = self.redis_client.set(key, value, ex=expire)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value by key"""
        try:
            if not self.is_connected:
                return None
                
            value = self.redis_client.get(key)
            if value is None:
                return None
                
            # Try to deserialize JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # Try pickle if JSON fails
                try:
                    return pickle.loads(value.encode() if isinstance(value, str) else value)
                except:
                    # Return as string if all else fails
                    return value
                    
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key"""
        try:
            if not self.is_connected:
                return False
                
            result = self.redis_client.delete(key)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            if not self.is_connected:
                return False
                
            return bool(self.redis_client.exists(key))
            
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for a key"""
        try:
            if not self.is_connected:
                return False
                
            return bool(self.redis_client.expire(key, seconds))
            
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False
    
    def keys(self, pattern: str = "*") -> list:
        """Get keys matching pattern"""
        try:
            if not self.is_connected:
                return []
                
            return self.redis_client.keys(pattern)
            
        except Exception as e:
            logger.error(f"Redis KEYS error for pattern {pattern}: {e}")
            return []
    
    def flushdb(self) -> bool:
        """Clear all keys in current database"""
        try:
            if not self.is_connected:
                return False
                
            self.redis_client.flushdb()
            return True
            
        except Exception as e:
            logger.error(f"Redis FLUSHDB error: {e}")
            return False


# Global Redis manager instance
redis_manager = RedisManager()


def init_redis():
    """Initialize Redis connection"""
    redis_manager.connect()


def close_redis():
    """Close Redis connection"""
    redis_manager.disconnect()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_parts = []
    
    # Add positional arguments
    for arg in args:
        if isinstance(arg, (dict, list)):
            key_parts.append(hashlib.md5(json.dumps(arg, sort_keys=True).encode()).hexdigest())
        else:
            key_parts.append(str(arg))
    
    # Add keyword arguments
    for k, v in sorted(kwargs.items()):
        if isinstance(v, (dict, list)):
            key_parts.append(f"{k}:{hashlib.md5(json.dumps(v, sort_keys=True).encode()).hexdigest()}")
        else:
            key_parts.append(f"{k}:{v}")
    
    return ":".join(key_parts)


def redis_cache(expire: int = 300, key_prefix: str = "cache"):
    """
    Redis cache decorator
    
    Args:
        expire: Cache expiration in seconds (default: 5 minutes)
        key_prefix: Prefix for cache keys
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            func_name = f"{func.__module__}.{func.__name__}"
            cache_key_str = f"{key_prefix}:{func_name}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_result = redis_manager.get(cache_key_str)
            if cached_result is not None:
                logger.debug(f"Cache HIT for {func_name}")
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_manager.set(cache_key_str, result, expire)
            logger.debug(f"Cache MISS for {func_name}, result cached")
            
            return result
        return wrapper
    return decorator


class SessionManager:
    """Redis-based session management"""
    
    def __init__(self, prefix: str = "session"):
        self.prefix = prefix
    
    def create_session(self, session_id: str, data: Dict[str, Any], expire: int = 3600) -> bool:
        """Create a new session"""
        key = f"{self.prefix}:{session_id}"
        return redis_manager.set(key, data, expire)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        key = f"{self.prefix}:{session_id}"
        return redis_manager.get(key)
    
    def update_session(self, session_id: str, data: Dict[str, Any], expire: int = 3600) -> bool:
        """Update session data"""
        key = f"{self.prefix}:{session_id}"
        return redis_manager.set(key, data, expire)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        key = f"{self.prefix}:{session_id}"
        return redis_manager.delete(key)
    
    def extend_session(self, session_id: str, expire: int = 3600) -> bool:
        """Extend session expiration"""
        key = f"{self.prefix}:{session_id}"
        return redis_manager.expire(key, expire)


class TokenManager:
    """Redis-based token management for refresh tokens"""
    
    def __init__(self, prefix: str = "token"):
        self.prefix = prefix
    
    def store_refresh_token(self, token_id: str, user_id: str, expire_days: int = 30) -> bool:
        """Store refresh token information"""
        key = f"{self.prefix}:refresh:{token_id}"
        data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True
        }
        expire_seconds = expire_days * 24 * 3600
        return redis_manager.set(key, data, expire_seconds)
    
    def get_refresh_token(self, token_id: str) -> Optional[Dict[str, Any]]:
        """Get refresh token information"""
        key = f"{self.prefix}:refresh:{token_id}"
        return redis_manager.get(key)
    
    def revoke_refresh_token(self, token_id: str) -> bool:
        """Revoke a refresh token"""
        key = f"{self.prefix}:refresh:{token_id}"
        token_data = redis_manager.get(key)
        if token_data:
            token_data["is_active"] = False
            return redis_manager.set(key, token_data, 86400)  # Keep for 24h for audit
        return False
    
    def revoke_user_tokens(self, user_id: str) -> int:
        """Revoke all refresh tokens for a user"""
        pattern = f"{self.prefix}:refresh:*"
        keys = redis_manager.keys(pattern)
        revoked_count = 0
        
        for key in keys:
            token_data = redis_manager.get(key)
            if token_data and token_data.get("user_id") == user_id and token_data.get("is_active"):
                token_data["is_active"] = False
                redis_manager.set(key, token_data, 86400)  # Keep for 24h for audit
                revoked_count += 1
        
        return revoked_count
    
    def blacklist_token(self, token_id: str, expire: int = 86400) -> bool:
        """Add token to blacklist"""
        key = f"{self.prefix}:blacklist:{token_id}"
        return redis_manager.set(key, True, expire)
    
    def is_token_blacklisted(self, token_id: str) -> bool:
        """Check if token is blacklisted"""
        key = f"{self.prefix}:blacklist:{token_id}"
        return redis_manager.exists(key)


# Global instances
session_manager = SessionManager()
token_manager = TokenManager()


# Health check function
def redis_health_check() -> Dict[str, Any]:
    """Check Redis health status"""
    try:
        if not redis_manager.is_connected:
            return {
                "status": "disconnected",
                "message": "Redis is not connected"
            }
        
        # Test basic operations
        test_key = "health_check_test"
        redis_manager.set(test_key, "test_value", 10)
        value = redis_manager.get(test_key)
        redis_manager.delete(test_key)
        
        if value == "test_value":
            return {
                "status": "healthy",
                "message": "Redis is working properly"
            }
        else:
            return {
                "status": "error",
                "message": "Redis operations failed"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Redis health check failed: {e}"
        }