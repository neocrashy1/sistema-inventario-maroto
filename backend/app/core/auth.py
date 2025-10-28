"""
Authentication and authorization utilities
"""

from datetime import datetime, timedelta
from typing import Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import structlog

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User

logger = structlog.get_logger()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()

# Token types
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Check token type
        if payload.get("type") != token_type:
            return None
            
        # Check expiration
        exp = payload.get("exp")
        if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
            return None
            
        return payload
    except JWTError:
        return None


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    except Exception as e:
        logger.error("Authentication error", error=str(e))
        return None


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    try:
        return db.query(User).filter(User.id == user_id).first()
    except Exception as e:
        logger.error("Error getting user by ID", user_id=user_id, error=str(e))
        return None


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    try:
        return db.query(User).filter(User.email == email).first()
    except Exception as e:
        logger.error("Error getting user by email", email=email, error=str(e))
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Extract token from credentials
        token = credentials.credentials
        
        # Verify token
        payload = verify_token(token, "access")
        if payload is None:
            raise credentials_exception
            
        # Get user ID from token
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # Get user from database
        user = get_user_by_id(db, user_id=user_id)
        if user is None:
            raise credentials_exception
            
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user"
            )
            
        return user
        
    except JWTError:
        raise credentials_exception
    except Exception as e:
        logger.error("Error getting current user", error=str(e))
        raise credentials_exception


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current admin user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def check_permission(user: User, permission: str) -> bool:
    """Check if user has specific permission"""
    # Admin has all permissions
    if user.role == "admin":
        return True
    
    # Define role permissions
    role_permissions = {
        "manager": [
            "assets:read", "assets:write", "assets:delete",
            "locations:read", "locations:write",
            "users:read", "reports:read"
        ],
        "operator": [
            "assets:read", "assets:write",
            "locations:read", "movements:write"
        ],
        "viewer": [
            "assets:read", "locations:read", "reports:read"
        ]
    }
    
    user_permissions = role_permissions.get(user.role, [])
    return permission in user_permissions


def require_permission(permission: str):
    """Decorator to require specific permission"""
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not check_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    return permission_checker


# Permission dependencies
require_assets_read = require_permission("assets:read")
require_assets_write = require_permission("assets:write")
require_assets_delete = require_permission("assets:delete")
require_locations_read = require_permission("locations:read")
require_locations_write = require_permission("locations:write")
require_users_read = require_permission("users:read")
require_reports_read = require_permission("reports:read")