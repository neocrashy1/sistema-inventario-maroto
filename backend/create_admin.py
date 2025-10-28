"""
Script para criar usuário administrador padrão
"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.sql import func
from app.core.database import sync_engine, Base
import enum
import bcrypt

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

class SimpleUser(Base):
    """Simplified User model for admin creation"""
    
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

def create_admin_user():
    """Criar usuário administrador padrão"""
    SessionLocal = sessionmaker(bind=sync_engine)
    db = SessionLocal()
    
    try:
        # Verificar se já existe um admin
        existing_admin = db.query(SimpleUser).filter(SimpleUser.email == "admin@levitiis.com").first()
        if existing_admin:
            print("Usuário administrador já existe!")
            return
        
        # Criar usuário administrador
        password = "admin123"
        # Hash da senha usando bcrypt diretamente
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            
        admin_user = SimpleUser(
            email="admin@levitiis.com",
            username="admin",
            full_name="Administrador",
            hashed_password=hashed_password,
            is_active=True,
            role=UserRole.ADMIN
        )
        
        db.add(admin_user)
        db.commit()
        print("Usuário administrador criado com sucesso!")
        print("Email: admin@levitiis.com")
        print("Senha: admin123")
        
    except Exception as e:
        print(f"Erro ao criar usuário administrador: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()