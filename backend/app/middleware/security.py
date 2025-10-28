"""
Security middleware for CORS, headers, and general security
"""
import logging
from typing import List, Optional
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import secrets
from app.core.config import settings

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """
    General security middleware
    """
    
    def __init__(self, 
                 allowed_hosts: Optional[List[str]] = None,
                 max_request_time: int = 30):
        self.allowed_hosts = allowed_hosts or ['localhost', '127.0.0.1']
        self.max_request_time = max_request_time
        self.request_id_header = "X-Request-ID"
    
    def generate_request_id(self) -> str:
        """
        Generate unique request ID
        """
        return secrets.token_urlsafe(16)
    
    def validate_host(self, request: Request) -> bool:
        """
        Validate request host
        """
        host = request.headers.get('host', '').split(':')[0]
        return host in self.allowed_hosts or host.startswith('localhost') or host.startswith('127.0.0.1')
    
    async def __call__(self, request: Request, call_next):
        """
        Process request with security checks
        """
        start_time = time.time()
        
        # Generate request ID
        request_id = self.generate_request_id()
        request.state.request_id = request_id
        
        # Validate host (in production)
        # if not self.validate_host(request):
        #     logger.warning(f"Invalid host: {request.headers.get('host')}")
        #     return JSONResponse(
        #         status_code=403,
        #         content={"detail": "Forbidden", "error_code": "INVALID_HOST"}
        #     )
        
        # Add request logging
        logger.info(f"Request {request_id}: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            # Check request processing time
            process_time = time.time() - start_time
            if process_time > self.max_request_time:
                logger.warning(f"Slow request {request_id}: {process_time:.2f}s")
            
            # Add security headers
            self.add_security_headers(response, request_id)
            
            # Add timing header
            response.headers["X-Process-Time"] = str(round(process_time, 3))
            
            logger.info(f"Response {request_id}: {response.status_code} in {process_time:.3f}s")
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Error in request {request_id}: {str(e)} after {process_time:.3f}s")
            raise
    
    def add_security_headers(self, response: Response, request_id: str):
        """
        Add security headers to response
        """
        # Request ID
        response.headers[self.request_id_header] = request_id
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy (adjusted for environment)
        script_inline = " 'unsafe-inline'" if settings.DEBUG else ""
        style_inline = " 'unsafe-inline'" if settings.DEBUG else ""
        csp = (
            "default-src 'self'; "
            f"script-src 'self'{script_inline}; "
            f"style-src 'self'{style_inline}; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        # HSTS (HTTP Strict Transport Security) - only in production with HTTPS enabled
        try:
            if (not settings.DEBUG) and (settings.ENABLE_HTTPS_REDIRECT or (settings.SSL_CERT_PATH and settings.SSL_KEY_PATH)):
                response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        except Exception:
            # Safeguard in case settings are not available
            pass

def setup_cors_middleware(app, 
                         allowed_origins: List[str] = None,
                         allowed_methods: List[str] = None,
                         allowed_headers: List[str] = None):
    """
    Setup CORS middleware with secure defaults
    """
    if allowed_origins is None:
        allowed_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8080",
            "http://127.0.0.1:8080"
        ]
    
    if allowed_methods is None:
        allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    
    if allowed_headers is None:
        allowed_headers = [
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Request-ID"
        ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=allowed_methods,
        allow_headers=allowed_headers,
        expose_headers=["X-Request-ID", "X-Process-Time", "X-RateLimit-Remaining"]
    )
    
    logger.info(f"CORS configured with origins: {allowed_origins}")

# Global security middleware instance
security_middleware = SecurityMiddleware()