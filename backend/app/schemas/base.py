"""
Base schemas for common patterns
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True
    )


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AuditMixin(TimestampMixin):
    """Mixin for audit fields"""
    created_by: Optional[int] = None


class PaginationParams(BaseModel):
    """Standard pagination parameters"""
    skip: int = 0
    limit: int = 100
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid"
    )


class PaginatedResponse(BaseModel):
    """Standard paginated response"""
    items: list
    total: int
    skip: int
    limit: int
    has_next: bool
    has_prev: bool
    
    model_config = ConfigDict(from_attributes=True)


class StatusResponse(BaseModel):
    """Standard status response"""
    success: bool
    message: str
    data: Optional[dict] = None
    
    model_config = ConfigDict(from_attributes=True)