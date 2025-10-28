"""
User model
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles enumeration"""
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    AUDITOR = "auditor"
    TECHNICIAN = "technician"


class UserStatus(str, enum.Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class User(Base):
    """User model"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Role and permissions
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Profile information
    phone = Column(String(20))
    department = Column(String(100))
    position = Column(String(100))
    employee_id = Column(String(50))
    
    # Security
    last_login = Column(DateTime(timezone=True))
    failed_login_attempts = Column(Integer, default=0)
    password_changed_at = Column(DateTime(timezone=True))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer)
    notes = Column(Text)
    
    # Relationships (simplified to avoid circular import issues)
    # Will be added back as needed when other models are properly configured
    setores_gerenciados = relationship("Setor", back_populates="gestor")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"