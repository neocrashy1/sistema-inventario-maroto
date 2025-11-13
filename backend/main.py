"""
Levitiis Asset Management System (AMS) - Main Application
"""

import structlog
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.exceptions import AppException
from app.middleware import (
    rate_limit_middleware,
    validation_middleware,
    security_middleware,
    performance_middleware
)
from app.core.monitoring import monitor_performance, start_monitoring, stop_monitoring
from app.core.redis_config import init_redis, close_redis
from app.api.v1.api import api_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Levitiis AMS API", version=settings.APP_VERSION)
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize Redis
    init_redis()
    logger.info("Redis initialized")
    
    # Start performance monitoring
    start_monitoring()
    logger.info("Performance monitoring started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Levitiis AMS API")
    
    # Stop monitoring
    stop_monitoring()
    logger.info("Performance monitoring stopped")
    
    # Close Redis connection
    close_redis()
    logger.info("Redis connection closed")
    
    # Close database connections
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API do Sistema Invetario Maroto",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# Performance middlewares
# 1. GZip compression for response optimization
app.add_middleware(
    GZipMiddleware, 
    minimum_size=1000,  # Only compress responses larger than 1KB
    compresslevel=6     # Balance between compression ratio and speed
)

# Optional HTTPS redirect (controlled via settings)
if settings.ENABLE_HTTPS_REDIRECT:
    app.add_middleware(HTTPSRedirectMiddleware)

# Security middlewares (order matters - applied in reverse order)
# 1. Performance monitoring (first to track all requests)
app.middleware("http")(performance_middleware)

# 2. Rate limiting
app.middleware("http")(rate_limit_middleware)

# 4. Input validation and sanitization
app.middleware("http")(validation_middleware)

# 5. General security middleware
app.middleware("http")(security_middleware)

# 6. Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.get_allowed_hosts()
)

# 7. CORS middleware (setup with secure defaults)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle application exceptions"""
    logger.error("Application exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": exc.error_code}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Ensure HTTPException preserves its status code and detail"""
    logger.warning(
        "HTTP exception",
        error=str(exc),
        path=request.url.path,
        status=getattr(exc, "status_code", 500)
    )
    return JSONResponse(
        status_code=getattr(exc, "status_code", 500),
        content={"detail": getattr(exc, "detail", "HTTP error")}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error("Unhandled exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error_code": "INTERNAL_ERROR"}
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.APP_VERSION}


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST if hasattr(settings, "HOST") else "0.0.0.0",
        port=settings.PORT if hasattr(settings, "PORT") else 8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        ssl_certfile=settings.SSL_CERT_PATH if settings.SSL_CERT_PATH else None,
        ssl_keyfile=settings.SSL_KEY_PATH if settings.SSL_KEY_PATH else None,
    )