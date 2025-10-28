"""
Alert model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import enum

from app.core.database import Base


class AlertType(str, enum.Enum):
    """Alert type enumeration"""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"
    MAINTENANCE = "maintenance"


class AlertStatus(str, enum.Enum):
    """Alert status enumeration"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    EXPIRED = "expired"


class AlertCategory(str, enum.Enum):
    """Alert category enumeration"""
    HARDWARE = "hardware"
    SOFTWARE = "software"
    NETWORK = "network"
    SECURITY = "security"
    PERFORMANCE = "performance"
    AVAILABILITY = "availability"
    CAPACITY = "capacity"
    OTHER = "other"


class AlertSource(str, enum.Enum):
    """Alert source enumeration"""
    SYSTEM = "system"
    AGENT = "agent"
    USER = "user"
    MONITORING = "monitoring"
    EXTERNAL = "external"


class Alert(Base):
    """
    Alert model for system notifications and monitoring
    """
    __tablename__ = "alerts"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Alert identification
    alert_number = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Classification
    alert_type = Column(String(20), default=AlertType.INFO, nullable=False, index=True)
    status = Column(String(20), default=AlertStatus.ACTIVE, nullable=False, index=True)
    severity = Column(Integer, default=1, nullable=False, index=True)  # 1-5 scale
    category = Column(String(20), default=AlertCategory.OTHER, nullable=False, index=True)
    source = Column(String(20), default=AlertSource.SYSTEM, nullable=False, index=True)
    
    # Asset and location information
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=True, index=True)
    machine_hostname = Column(String(100), nullable=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True, index=True)
    
    # Acknowledgment
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledgment_notes = Column(Text, nullable=True)
    
    # Resolution
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Escalation
    escalation_level = Column(Integer, default=1, nullable=False)
    escalated_at = Column(DateTime(timezone=True), nullable=True)
    escalated_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Notification tracking
    notification_count = Column(Integer, default=0)
    last_notification_at = Column(DateTime(timezone=True), nullable=True)
    notification_channels = Column(JSON, nullable=True)  # Array of channels used
    
    # Auto-resolution
    auto_resolve = Column(Boolean, default=False)
    auto_resolve_at = Column(DateTime(timezone=True), nullable=True)
    
    # Correlation and grouping
    correlation_id = Column(String(100), nullable=True, index=True)
    parent_alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=True)
    
    # Additional data
    custom_metadata = Column(JSON, nullable=True)  # Custom fields, metrics, etc.
    tags = Column(JSON, nullable=True)  # Array of tags
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Can be system-generated
    
    # Relationships
    asset = relationship("Asset", back_populates="alerts")
    location = relationship("Location", back_populates="alerts")
    acknowledger = relationship("User", foreign_keys=[acknowledged_by])
    resolver = relationship("User", foreign_keys=[resolved_by])
    escalated_user = relationship("User", foreign_keys=[escalated_to])
    creator = relationship("User", foreign_keys=[created_by])
    parent_alert = relationship("Alert", remote_side=[id], back_populates="child_alerts")
    child_alerts = relationship("Alert", back_populates="parent_alert")
    
    def __repr__(self):
        return f"<Alert(id={self.id}, number='{self.alert_number}', type='{self.alert_type}', severity={self.severity})>"


class AlertRule(Base):
    """
    Alert rule model for automated alert generation
    """
    __tablename__ = "alert_rules"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Rule identification
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Rule configuration
    condition = Column(JSON, nullable=False)  # Rule conditions and thresholds
    alert_template = Column(JSON, nullable=False)  # Alert template to generate
    
    # Rule status
    is_active = Column(Boolean, default=True)
    
    # Targeting
    asset_types = Column(JSON, nullable=True)  # Array of asset types to monitor
    locations = Column(JSON, nullable=True)  # Array of location IDs
    tags = Column(JSON, nullable=True)  # Array of tags to match
    
    # Timing
    evaluation_interval = Column(Integer, default=300)  # Seconds
    cooldown_period = Column(Integer, default=900)  # Seconds before re-alerting
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User")
    
    def __repr__(self):
        return f"<AlertRule(id={self.id}, name='{self.name}', active={self.is_active})>"