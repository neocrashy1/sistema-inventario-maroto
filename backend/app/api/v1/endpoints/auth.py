"""
Authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import structlog
from typing import Optional

from app.core.database import get_async_session
from app.core.security import (
    create_access_token, 
    create_refresh_token, 
    verify_password, 
    get_password_hash,
    get_current_user_id,
    security,
    verify_token,
    revoke_refresh_token
)
from app.core.exceptions import AuthenticationException, ValidationException
from app.crud.user import authenticate_user, get_user_by_username_or_email, create_user

logger = structlog.get_logger()

router = APIRouter()


# Pydantic models
class UserLogin(BaseModel):
    """User login request"""
    username: str
    password: str


class UserRegister(BaseModel):
    """User registration request"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: str
    role: str = "USER"


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    username: str
    role: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """
    User login endpoint
    
    Accepts either application/json or application/x-www-form-urlencoded form data with fields:
    - username (or email)
    - password
    """
    try:
        content_type = (request.headers.get("content-type", "").lower())
        username = None
        password = None
        
        if "application/json" in content_type:
            data = await request.json()
            username = data.get("username") or data.get("email")
            password = data.get("password")
        else:
            try:
                form = await request.form()
                username = form.get("username") or form.get("email")
                password = form.get("password")
            except Exception:
                pass
        
        if not username or not password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="username/email and password are required"
            )
        
        logger.info("Login attempt", username=username)
        
        # Authenticate user with database
        user = await authenticate_user(db, username, password)
        if not user:
            # Invalid credentials should return 401
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not user.is_active:
            raise AuthenticationException("Account is disabled")
        
        user_id = user.id
        username = user.username
        role = user.role.value if hasattr(user.role, 'value') else user.role
        
        # Create tokens
        access_token = create_access_token(data={"sub": str(user_id), "username": username, "role": role})
        refresh_token = create_refresh_token(data={"sub": str(user_id)}, user_id=str(user_id))
        
        logger.info("Login successful", user_id=user_id, username=username)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600,  # 1 hour
            "user_id": user_id,
            "username": username,
            "role": role
        }
        
    except AuthenticationException:
        # Map authentication errors to 401
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    except HTTPException as e:
        # Propagate HTTPExceptions (e.g., 422 from validation) without converting to 500
        raise e
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/register", response_model=dict)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_async_session)
):
    """
    User registration endpoint
    """
    try:
        logger.info("Registration attempt", username=user_data.username, email=user_data.email)
        
        # Validate input
        if len(user_data.password) < 8:
            raise ValidationException("Password must be at least 8 characters long")
        
        # Normalize role to lowercase and validate
        role_lower = (user_data.role or "user").lower()
        valid_roles = {"admin", "manager", "user", "auditor", "technician"}
        if role_lower not in valid_roles:
            raise ValidationException("Invalid role")
        
        # Check if user already exists
        existing_user = await get_user_by_username_or_email(db, user_data.username, user_data.email)
        if existing_user:
            raise ValidationException("Username or email already exists")
        
        # Build full name from provided fields
        full_name = (user_data.full_name or "").strip()
        if not full_name:
            first = (user_data.first_name or "").strip()
            last = (user_data.last_name or "").strip()
            full_name = (f"{first} {last}".strip() or user_data.username)
        
        # Create user in database
        user = await create_user(
            db,
            username=user_data.username,
            email=user_data.email,
            full_name=full_name,
            password=user_data.password,
            role=role_lower
        )
        
        logger.info("Registration successful", user_id=user.id, username=user.username)
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user_id": user.id,
            "username": user.username
        }
        
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error("Registration failed", username=user_data.username, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Refresh access token using refresh token
    """
    try:
        # Validate refresh token
        payload = verify_token(token_request.refresh_token, token_type="refresh")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        # Resolve user
        from app.crud.user import get_user_by_id
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token subject"
            )
        user = await get_user_by_id(db, int(user_id))
        if not user or not getattr(user, "is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        username = user.username
        role = user.role.value if hasattr(user.role, 'value') else user.role
        # Rotate refresh token (revoke old, issue new)
        revoke_refresh_token(token_request.refresh_token)
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)}, user_id=str(user.id))
        # Issue new access token
        access_token = create_access_token(data={"sub": str(user.id), "username": username, "role": role})
        logger.info("Token refreshed", user_id=user.id)
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": 3600,
            "user_id": user.id,
            "username": username,
            "role": role
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Refresh token failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Refresh token failed"
        )


@router.post("/logout", response_model=dict)
async def logout(
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds))
):
    """
    User logout endpoint
    """
    try:
        # TODO: Invalidate refresh tokens in database
        # await invalidate_user_tokens(db, current_user)
        
        logger.info("User logged out", user_id=current_user)
        
        return {
            "success": True,
            "message": "Logged out successfully"
        }
        
    except Exception as e:
        logger.error("Logout failed", user_id=current_user, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.post("/change-password", response_model=dict)
async def change_password(
    password_data: PasswordChangeRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds))
):
    """
    Change user password
    """
    try:
        logger.info("Password change request", user_id=current_user)
        
        # TODO: Implement actual database logic
        # user = await get_user_by_id(db, current_user)
        # if not user or not verify_password(password_data.current_password, user.hashed_password):
        #     raise AuthenticationException("Invalid current password")
        
        # Validate new password
        if len(password_data.new_password) < 8:
            raise ValidationException("New password must be at least 8 characters long")
        
        # Hash new password
        new_hashed_password = get_password_hash(password_data.new_password)
        
        # TODO: Update password in database
        # await update_user_password(db, current_user, new_hashed_password)
        
        logger.info("Password changed successfully", user_id=current_user)
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }
        
    except (ValidationException, AuthenticationException):
        raise
    except Exception as e:
        logger.error("Password change failed", user_id=current_user, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.get("/me", response_model=dict)
async def get_current_user_info(
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds))
):
    """
    Get current user information
    """
    try:
        # TODO: Implement actual database logic
        # user = await get_user_by_id(db, current_user)
        # if not user:
        #     raise NotFoundException("User not found")
        
        # Mock user data
        user_info = {
            "id": int(current_user),
            "username": "admin",
            "email": "admin@company.com",
            "full_name": "System Administrator",
            "role": "ADMIN",
            "status": "ACTIVE",
            "is_active": True,
            "is_verified": True,
            "last_login": "2024-01-15T09:00:00Z",
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        return user_info
        
    except Exception as e:
        logger.error("Failed to get user info", user_id=current_user, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )