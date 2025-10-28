#!/usr/bin/env python3
"""
Minimal FastAPI application for testing - without custom middlewares
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import init_db
# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Sistema de Inventário de Ativos - API Minimal",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Initialize database
init_db()

print("Minimal server initialized")

# Add only basic middlewares
app.add_middleware(
    GZipMiddleware, 
    minimum_size=1000,
    compresslevel=6
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.get_allowed_hosts()
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "asset-inventory-api"}

if __name__ == "__main__":
    uvicorn.run(
        "main_minimal:app",
        host="0.0.0.0",
        port=8004,
        log_level="debug",
        reload=True
    )