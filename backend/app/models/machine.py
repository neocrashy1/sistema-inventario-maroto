"""
Machine model for agent management
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
import enum

from app.core.database import Base


class MachineStatus(str, enum.Enum):
    """Machine status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    UNKNOWN = "unknown"
    DISCONNECTED = "disconnected"


class MachineType(str, enum.Enum):
    """Machine type enumeration"""
    WORKSTATION = "workstation"
    SERVER = "server"
    LAPTOP = "laptop"
    MOBILE = "mobile"
    VIRTUAL = "virtual"
    CONTAINER = "container"
    IOT = "iot"
    OTHER = "other"


class OperatingSystem(str, enum.Enum):
    """Operating system enumeration"""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    ANDROID = "android"
    IOS = "ios"
    OTHER = "other"


class Machine(Base):
    """
    Machine model for tracking computers and devices with agents
    """
    __tablename__ = "machines"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Machine identification
    hostname = Column(String(100), unique=True, nullable=False, index=True)
    machine_id = Column(String(100), unique=True, nullable=False, index=True)  # UUID from agent
    name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    
    # Classification
    machine_type = Column(String(20), default=MachineType.WORKSTATION, nullable=False, index=True)
    status = Column(String(20), default=MachineStatus.UNKNOWN, nullable=False, index=True)
    
    # System information
    operating_system = Column(String(20), nullable=True, index=True)
    os_version = Column(String(100), nullable=True)
    architecture = Column(String(20), nullable=True)  # x64, x86, arm64, etc.
    
    # Hardware information
    cpu_model = Column(String(200), nullable=True)
    cpu_cores = Column(Integer, nullable=True)
    ram_total_gb = Column(Float, nullable=True)
    disk_total_gb = Column(Float, nullable=True)
    
    # Network information
    ip_address = Column(String(45), nullable=True, index=True)
    mac_address = Column(String(17), nullable=True, index=True)
    domain = Column(String(100), nullable=True)
    
    # Location and assignment
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True, index=True)
    assigned_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Agent information
    agent_version = Column(String(50), nullable=True)
    agent_last_seen = Column(DateTime(timezone=True), nullable=True)
    agent_config = Column(JSON, nullable=True)  # Agent configuration
    
    # Monitoring
    last_boot_time = Column(DateTime(timezone=True), nullable=True)
    uptime_seconds = Column(Integer, nullable=True)
    cpu_usage_percent = Column(Float, nullable=True)
    ram_usage_percent = Column(Float, nullable=True)
    disk_usage_percent = Column(Float, nullable=True)
    
    # Security
    antivirus_status = Column(String(50), nullable=True)
    firewall_status = Column(String(50), nullable=True)
    last_security_scan = Column(DateTime(timezone=True), nullable=True)
    
    # Compliance
    is_compliant = Column(Boolean, default=True)
    compliance_notes = Column(Text, nullable=True)
    last_compliance_check = Column(DateTime(timezone=True), nullable=True)
    
    # Management
    is_managed = Column(Boolean, default=True)
    management_notes = Column(Text, nullable=True)
    
    # Additional data
    custom_metadata = Column(JSON, nullable=True)  # Custom fields, additional hardware info, etc.
    tags = Column(JSON, nullable=True)  # Array of tags
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    first_seen = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    location = relationship("Location", back_populates="machines")
    assigned_user = relationship("User")
    software_inventory = relationship("SoftwareInventory", back_populates="machine")
    machine_metrics = relationship("MachineMetric", back_populates="machine")
    
    def __repr__(self):
        return f"<Machine(id={self.id}, hostname='{self.hostname}', status='{self.status}')>"


class SoftwareInventory(Base):
    """
    Software inventory model for tracking installed software
    """
    __tablename__ = "software_inventory"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Machine reference
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    
    # Software information
    name = Column(String(200), nullable=False, index=True)
    version = Column(String(100), nullable=True)
    vendor = Column(String(200), nullable=True)
    install_date = Column(DateTime(timezone=True), nullable=True)
    install_location = Column(String(500), nullable=True)
    
    # Classification
    category = Column(String(100), nullable=True)
    is_licensed = Column(Boolean, nullable=True)
    license_key = Column(String(200), nullable=True)
    
    # Security
    is_vulnerable = Column(Boolean, default=False)
    vulnerability_count = Column(Integer, default=0)
    last_vulnerability_scan = Column(DateTime(timezone=True), nullable=True)
    
    # Additional data
    custom_metadata = Column(JSON, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    machine = relationship("Machine", back_populates="software_inventory")
    
    def __repr__(self):
        return f"<SoftwareInventory(id={self.id}, name='{self.name}', version='{self.version}')>"


class MachineMetric(Base):
    """
    Machine metrics model for storing performance and monitoring data
    """
    __tablename__ = "machine_metrics"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Machine reference
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False, index=True)
    
    # Metric information
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20), nullable=True)
    
    # Context
    category = Column(String(50), nullable=True, index=True)  # cpu, memory, disk, network, etc.
    
    # Additional data
    custom_metadata = Column(JSON, nullable=True)
    
    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    machine = relationship("Machine", back_populates="machine_metrics")
    
    def __repr__(self):
        return f"<MachineMetric(id={self.id}, machine_id={self.machine_id}, metric='{self.metric_name}', value={self.metric_value})>"