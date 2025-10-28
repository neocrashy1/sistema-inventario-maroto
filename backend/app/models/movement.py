"""
Movement model for asset tracking
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import enum

from app.core.database import Base


class MovementType(str, enum.Enum):
    """Movement type enumeration"""
    ASSIGNMENT = "assignment"  # Asset assigned to user
    TRANSFER = "transfer"  # Asset moved to different location
    CHECKOUT = "checkout"  # Asset checked out
    CHECKIN = "checkin"  # Asset checked in
    DEPLOYMENT = "deployment"  # Asset deployed
    RETURN = "return"  # Asset returned
    MAINTENANCE = "maintenance"  # Asset sent for maintenance
    DISPOSAL = "disposal"  # Asset disposed
    LOST = "lost"  # Asset reported lost
    FOUND = "found"  # Asset found
    STOLEN = "stolen"  # Asset reported stolen
    DAMAGED = "damaged"  # Asset reported damaged


class MovementStatus(str, enum.Enum):
    """Movement status enumeration"""
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Movement(Base):
    """
    Movement model for tracking asset movements and assignments
    """
    __tablename__ = "movements"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Movement identification
    movement_number = Column(String(50), unique=True, nullable=False, index=True)
    movement_type = Column(String(20), nullable=False, index=True)
    status = Column(String(20), default=MovementStatus.PENDING, nullable=False, index=True)
    
    # Asset information
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, index=True)
    
    # Source information
    from_location_id = Column(Integer, ForeignKey("locations.id"), nullable=True, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Destination information
    to_location_id = Column(Integer, ForeignKey("locations.id"), nullable=True, index=True)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Movement details
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timing
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expected_return_date = Column(DateTime(timezone=True), nullable=True)
    
    # Approval workflow
    requires_approval = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_notes = Column(Text, nullable=True)
    
    # Tracking
    tracking_number = Column(String(100), nullable=True)
    carrier = Column(String(100), nullable=True)
    
    # Condition tracking
    condition_before = Column(String(50), nullable=True)
    condition_after = Column(String(50), nullable=True)
    condition_notes = Column(Text, nullable=True)
    
    # Cost tracking
    cost = Column(String(20), nullable=True)  # Using string to handle different currencies
    cost_center = Column(String(100), nullable=True)
    
    # Additional data
    custom_metadata = Column(JSON, nullable=True)  # Custom fields
    attachments = Column(JSON, nullable=True)  # Array of file references
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    asset = relationship("Asset", back_populates="movements")
    from_location = relationship("Location", foreign_keys=[from_location_id], back_populates="movements_from")
    to_location = relationship("Location", foreign_keys=[to_location_id], back_populates="movements_to")
    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])
    approver = relationship("User", foreign_keys=[approved_by])
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<Movement(id={self.id}, number='{self.movement_number}', type='{self.movement_type}', status='{self.status}')>"


class AssetAudit(Base):
    """
    Asset audit model for tracking all changes to assets
    """
    __tablename__ = "asset_audits"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Asset information
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False, index=True)
    
    # Audit information
    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, MOVE, etc.
    table_name = Column(String(50), nullable=False)
    record_id = Column(Integer, nullable=True)
    
    # Change tracking
    field_name = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    # Context
    reason = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Additional data
    custom_metadata = Column(JSON, nullable=True)

    # Audit integrity
    prev_hash = Column(String(64), nullable=True)
    record_hash = Column(String(64), nullable=True)
    signature = Column(String(128), nullable=True)
    signature_algorithm = Column(String(50), default="HMAC-SHA256", nullable=True)

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    asset = relationship("Asset", back_populates="audit_logs")
    user = relationship("User")
    
    def __repr__(self):
        return f"<AssetAudit(id={self.id}, asset_id={self.asset_id}, action='{self.action}')>"