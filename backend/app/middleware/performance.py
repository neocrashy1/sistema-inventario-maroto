"""
Performance monitoring middleware
"""

import time
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import structlog

from app.core.monitoring import metrics_collector, RequestMetric

logger = structlog.get_logger()


class PerformanceMiddleware:
    """Middleware to monitor request performance (function-based)"""
    
    async def __call__(self, request: Request, call_next):
        """Monitor request performance"""
        start_time = time.time()
        metrics_collector.active_requests += 1
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate metrics
            response_time = time.time() - start_time
            
            # Create metric
            metric = RequestMetric(
                endpoint=str(request.url.path),
                method=request.method,
                status_code=response.status_code,
                response_time=response_time,
                timestamp=datetime.utcnow()
            )
            
            # Add metric to collector
            metrics_collector.add_request_metric(metric)
            
            return response
            
        except Exception as e:
            # Record failed request
            response_time = time.time() - start_time
            
            metric = RequestMetric(
                endpoint=str(request.url.path),
                method=request.method,
                status_code=500,
                response_time=response_time,
                timestamp=datetime.utcnow(),
                error_message=str(e)
            )
            
            metrics_collector.add_request_metric(metric)
            raise
            
        finally:
            metrics_collector.active_requests -= 1


# Create middleware instance
performance_middleware = PerformanceMiddleware()