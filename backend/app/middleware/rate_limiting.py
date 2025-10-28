"""
Rate limiting middleware for API protection
"""
import time
from typing import Dict, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import asyncio
from collections import defaultdict, deque
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Token bucket rate limiter implementation
    """
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients: Dict[str, deque] = defaultdict(deque)
        self.lock = asyncio.Lock()
    
    async def is_allowed(self, client_id: str) -> bool:
        """
        Check if client is allowed to make request
        """
        async with self.lock:
            now = datetime.now()
            client_requests = self.clients[client_id]
            
            # Remove old requests outside the window
            while client_requests and client_requests[0] < now - timedelta(seconds=self.window_seconds):
                client_requests.popleft()
            
            # Check if under limit
            if len(client_requests) < self.max_requests:
                client_requests.append(now)
                return True
            
            return False
    
    async def get_reset_time(self, client_id: str) -> Optional[datetime]:
        """
        Get when the rate limit will reset for client
        """
        async with self.lock:
            client_requests = self.clients[client_id]
            if client_requests:
                return client_requests[0] + timedelta(seconds=self.window_seconds)
            return None

class RateLimitMiddleware:
    """
    Rate limiting middleware for FastAPI
    """
    
    def __init__(self):
        # Different limits for different endpoint types
        self.limiters = {
            'auth': RateLimiter(max_requests=50, window_seconds=60),      # 50 auth requests per minute
            'api': RateLimiter(max_requests=200, window_seconds=60),     # 200 API requests per minute
            'dashboard': RateLimiter(max_requests=100, window_seconds=60), # 100 dashboard requests per minute
            'default': RateLimiter(max_requests=60, window_seconds=60)   # 60 requests per minute default
        }
    
    def get_client_id(self, request: Request) -> str:
        """
        Get client identifier from request
        """
        # Try to get user ID from auth if available
        if hasattr(request.state, 'user_id'):
            return f"user:{request.state.user_id}"
        
        # Fallback to IP address
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"
        
        client_host = request.client.host if request.client else 'unknown'
        return f"ip:{client_host}"
    
    def get_limiter_type(self, request: Request) -> str:
        """
        Determine which rate limiter to use based on request path
        """
        path = request.url.path
        
        if '/auth/' in path:
            return 'auth'
        elif '/dashboard/' in path:
            return 'dashboard'
        elif '/api/' in path:
            return 'api'
        else:
            return 'default'
    
    async def __call__(self, request: Request, call_next):
        """
        Process request with rate limiting
        """
        client_id = self.get_client_id(request)
        limiter_type = self.get_limiter_type(request)
        limiter = self.limiters[limiter_type]
        
        # Check rate limit
        if not await limiter.is_allowed(client_id):
            reset_time = await limiter.get_reset_time(client_id)
            
            logger.warning(f"Rate limit exceeded for client {client_id} on {request.url.path}")
            
            headers = {
                "X-RateLimit-Limit": str(limiter.max_requests),
                "X-RateLimit-Window": str(limiter.window_seconds),
                "X-RateLimit-Remaining": "0"
            }
            
            if reset_time:
                headers["X-RateLimit-Reset"] = str(int(reset_time.timestamp()))
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Too many requests.",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "retry_after": limiter.window_seconds
                },
                headers=headers
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        
        # Get current usage
        async with limiter.lock:
            current_requests = len(limiter.clients[client_id])
            remaining = max(0, limiter.max_requests - current_requests)
        
        response.headers["X-RateLimit-Limit"] = str(limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = str(limiter.window_seconds)
        
        return response

# Global rate limiter instance
rate_limit_middleware = RateLimitMiddleware()