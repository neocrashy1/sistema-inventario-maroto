"""
Application configuration settings
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Sistema Inventario Levitiis API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    API_V1_STR: str = "/api/v1"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    # Additional security
    ENABLE_HTTPS_REDIRECT: bool = False
    ALLOWED_HOSTS: str = "localhost,127.0.0.1,*.levitiis.com"
    
    # TLS/SSL for direct Uvicorn (optional, when terminating TLS in app)
    SSL_CERT_PATH: Optional[str] = None
    SSL_KEY_PATH: Optional[str] = None
    
    # Database
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    ASYNC_DATABASE_URL: Optional[str] = None
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080,http://localhost:5173"
    
    def get_cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    def get_allowed_hosts(self) -> List[str]:
        return [host.strip() for host in self.ALLOWED_HOSTS.split(",")]
    
    # File Upload
    MAX_FILE_SIZE: int = 10485760  # 10MB
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    UPLOAD_PATH: str = "./uploads"
    
    # Network Discovery
    NETWORK_SCAN_TIMEOUT: int = 30
    NETWORK_DISCOVERY_TIMEOUT: int = 30
    MAX_CONCURRENT_SCANS: int = 10
    NETWORK_DISCOVERY_CONCURRENT_SCANS: int = 10
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_TLS: bool = True
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # Redis
    REDIS_URL: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_FILE_PATH: str = "./logs/app.log"
    
    # Agent
    AGENT_HEARTBEAT_INTERVAL: int = 300
    AGENT_CONFIG_REFRESH_INTERVAL: int = 3600

    # API Key Auth for agents
    API_KEY_HEADER_NAME: str = "X-API-Key"
    AGENT_API_KEYS: Optional[str] = None  # Comma-separated list of allowed API keys

    @field_validator("AGENT_API_KEYS")
    def normalize_agent_api_keys(cls, v):
        # Allow empty/None; when present, strip spaces
        return v.strip() if isinstance(v, str) else v

    def get_agent_api_keys(self) -> List[str]:
        if not self.AGENT_API_KEYS:
            return []
        return [k.strip() for k in self.AGENT_API_KEYS.split(",") if k.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()