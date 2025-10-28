"""
Ticket model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import enum

from app.core.database import Base


class TicketStatus(str, enum.Enum):
    """Ticket status enumeration"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class TicketPriority(str, enum.Enum):
    """Ticket priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketCategory(str, enum.Enum):
    """Ticket category enumeration"""
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    SECURITY = "security"
    ACCESS = "access"
    MAINTENANCE = "maintenance"
    OTHER = "other"


class Ticket(Base):
    """
    Ticket model for support requests and issues
    """
    __tablename__ = "tickets"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Ticket identification
    ticket_number = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Status and priority
    status = Column(String(20), default=TicketStatus.OPEN, nullable=False, index=True)
    priority = Column(String(20), default=TicketPriority.MEDIUM, nullable=False, index=True)
    category = Column(String(20), default=TicketCategory.OTHER, nullable=False, index=True)
    
    # Asset and location information
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True, index=True)
    machine_hostname = Column(String(100), nullable=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True, index=True)
    
    # Requester information
    requester_name = Column(String(100), nullable=True)
    requester_email = Column(String(100), nullable=True)
    requester_phone = Column(String(20), nullable=True)
    department = Column(String(50), nullable=True)
    
    # Assignment
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    
    # Resolution
    resolution = Column(Text, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Time tracking
    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, nullable=True)
    
    # SLA tracking
    sla_due_date = Column(DateTime(timezone=True), nullable=True)
    sla_breached = Column(Boolean, default=False)
    
    # Additional data
    custom_metadata = Column(JSON, nullable=True)  # Custom fields, attachments, etc.
    tags = Column(JSON, nullable=True)  # Array of tags
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    asset = relationship("Asset", back_populates="tickets")
    location = relationship("Location", back_populates="tickets")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    creator = relationship("User", foreign_keys=[created_by])
    resolver = relationship("User", foreign_keys=[resolved_by])
    comments = relationship("TicketComment", back_populates="ticket", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Ticket(id={self.id}, number='{self.ticket_number}', title='{self.title}', status='{self.status}')>"


class TicketComment(Base):
    """
    Ticket comment model for communication history
    """
    __tablename__ = "ticket_comments"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, index=True)
    
    # Comment content
    comment = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal notes vs customer-visible
    
    # Attachments
    attachments = Column(JSON, nullable=True)  # Array of file paths/URLs
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    ticket = relationship("Ticket", back_populates="comments")
    author = relationship("User")
    
    def __repr__(self):
        return f"<TicketComment(id={self.id}, ticket_id={self.ticket_id}, internal={self.is_internal})>"