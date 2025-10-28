"""
User management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel, EmailStr
import structlog

from app.core.database import get_async_session
from app.core.security import get_current_user_id, security, get_password_hash
from app.core.exceptions import NotFoundException, ValidationException

logger = structlog.get_logger()

router = APIRouter()


# Pydantic models
class UserCreate(BaseModel):
    """User creation request"""
    username: str
    email: EmailStr
    full_name: str
    role: str = "USER"
    department: Optional[str] = None
    phone: Optional[str] = None
    location_id: Optional[int] = None
    manager_id: Optional[int] = None
    is_active: bool = True


class UserUpdate(BaseModel):
    """User update request"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    location_id: Optional[int] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = None
    status: Optional[str] = None


class UserResponse(BaseModel):
    """User response model"""
    id: int
    username: str
    email: str
    full_name: str
    role: str
    status: str
    department: Optional[str]
    phone: Optional[str]
    location_id: Optional[int]
    location_name: Optional[str]
    manager_id: Optional[int]
    manager_name: Optional[str]
    is_active: bool
    is_verified: bool
    last_login: Optional[str]
    created_at: str
    updated_at: Optional[str]


class PasswordReset(BaseModel):
    """Password reset request"""
    user_id: int
    new_password: str


@router.post("/", response_model=dict)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds))
):
    """
    Create a new user (Admin only)
    """
    try:
        logger.info(
            "User creation request",
            username=user_data.username,
            email=user_data.email,
            role=user_data.role,
            admin_user_id=current_user
        )
        
        # Validate role
        if user_data.role not in ["USER", "MANAGER", "TECHNICIAN", "AUDITOR", "ADMIN"]:
            raise ValidationException("Invalid role")
        
        # TODO: Check permissions - only admins can create users
        # current_user_obj = await get_user_by_id(db, current_user)
        # if current_user_obj.role != "ADMIN":
        #     raise AuthorizationException("Only administrators can create users")
        
        # TODO: Check if username/email already exists
        # existing_user = await get_user_by_username_or_email(db, user_data.username, user_data.email)
        # if existing_user:
        #     raise ValidationException("Username or email already exists")
        
        # Generate temporary password
        temp_password = "TempPass123!"  # In real implementation, generate random password
        hashed_password = get_password_hash(temp_password)
        
        # TODO: Implement actual database logic
        # user = await create_user_record(db, user_data, hashed_password, current_user)
        
        user_id = 4  # Mock ID
        
        # TODO: Send welcome email with temporary password
        # await send_welcome_email(user_data.email, user_data.username, temp_password)
        
        logger.info(
            "User created successfully",
            user_id=user_id,
            username=user_data.username
        )
        
        return {
            "success": True,
            "message": "User created successfully",
            "user_id": user_id,
            "username": user_data.username,
            "temporary_password": temp_password  # Remove in production
        }
        
    except ValidationException:
        raise
    except Exception as e:
        logger.error("User creation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds))
):
    """
    Get user details by ID
    """
    try:
        # TODO: Implement actual database logic
        # user = await get_user_by_id(db, user_id)
        # if not user:
        #     raise NotFoundException(f"User with ID {user_id} not found")
        
        # TODO: Check permissions - users can only see their own data unless admin
        # if str(user_id) != current_user and current_user_obj.role not in ["ADMIN", "MANAGER"]:
        #     raise AuthorizationException("Access denied")
        
        # Mock response
        return {
            "id": user_id,
            "username": "john.doe",
            "email": "john.doe@company.com",
            "full_name": "John Doe",
            "role": "USER",
            "status": "ACTIVE",
            "department": "IT",
            "phone": "+1-555-0123",
            "location_id": 1,
            "location_name": "Floor 1 - Room 101",
            "manager_id": 2,
            "manager_name": "Jane Smith",
            "is_active": True,
            "is_verified": True,
            "last_login": "2024-01-15T09:00:00Z",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2024-01-15T08:00:00Z"
        }
        
    except Exception as e:
        logger.error("Failed to get user", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )


@router.put("/{user_id}", response_model=dict)
async def update_user(
    user_id: int,
    update_data: UserUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds))
):
    """
    Update user information
    """
    try:
        logger.info(
            "User update request",
            user_id=user_id,
            admin_user_id=current_user
        )
        
        # TODO: Implement actual database logic
        # user = await get_user_by_id(db, user_id)
        # if not user:
        #     raise NotFoundException(f"User with ID {user_id} not found")
        
        # TODO: Check permissions
        # if str(user_id) != current_user and current_user_obj.role not in ["ADMIN", "MANAGER"]:
        #     raise AuthorizationException("Access denied")
        
        # Update user
        # updated_user = await update_user_record(db, user_id, update_data, current_user)
        
        logger.info(
            "User updated successfully",
            user_id=user_id
        )
        
        return {
            "success": True,
            "message": "User updated successfully",
            "user_id": user_id
        }
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error("User update failed", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[str] = None,
    status: Optional[str] = None,
    department: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds))
):
    """
    List users with optional filtering and search
    """
    try:
        # TODO: Check permissions - only admins and managers can list users
        # current_user_obj = await get_user_by_id(db, current_user)
        # if current_user_obj.role not in ["ADMIN", "MANAGER"]:
        #     raise AuthorizationException("Access denied")
        
        # TODO: Implement actual database logic
        # users = await get_users(db, skip=skip, limit=limit, filters={...})
        
        # Mock response
        users = [
            {
                "id": 1,
                "username": "admin",
                "email": "admin@company.com",
                "full_name": "System Administrator",
                "role": "ADMIN",
                "status": "ACTIVE",
                "department": "IT",
                "phone": "+1-555-0100",
                "location_id": 1,
                "location_name": "Floor 1 - IT Office",
                "manager_id": None,
                "manager_name": None,
                "is_active": True,
                "is_verified": True,
                "last_login": "2024-01-15T09:00:00Z",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2024-01-15T08:00:00Z"
            },
            {
                "id": 2,
                "username": "john.doe",
                "email": "john.doe@company.com",
                "full_name": "John Doe",
                "role": "USER",
                "status": "ACTIVE",
                "department": "Sales",
                "phone": "+1-555-0123",
                "location_id": 2,
                "location_name": "Floor 2 - Sales",
                "manager_id": 3,
                "manager_name": "Jane Smith",
                "is_active": True,
                "is_verified": True,
                "last_login": "2024-01-15T08:30:00Z",
                "created_at": "2023-02-01T00:00:00Z",
                "updated_at": "2024-01-15T07:00:00Z"
            }
        ]
        
        return users
        
    except Exception as e:
        logger.error("Failed to list users", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds))
):
    """
    Delete user (Admin only)
    """
    try:
        logger.info(
            "User deletion request",
            user_id=user_id,
            admin_user_id=current_user
        )
        
        # TODO: Check permissions - only admins can delete users
        # current_user_obj = await get_user_by_id(db, current_user)
        # if current_user_obj.role != "ADMIN":
        #     raise AuthorizationException("Only administrators can delete users")
        
        # TODO: Implement actual database logic
        # user = await get_user_by_id(db, user_id)
        # if not user:
        #     raise NotFoundException(f"User with ID {user_id} not found")
        
        # Soft delete user
        # await soft_delete_user(db, user_id, current_user)
        
        logger.info(
            "User deleted successfully",
            user_id=user_id
        )
        
        return {
            "success": True,
            "message": "User deleted successfully",
            "user_id": user_id
        }
        
    except NotFoundException:
        raise
    except Exception as e:
        logger.error("User deletion failed", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )


@router.post("/{user_id}/reset-password", response_model=dict)
async def reset_user_password(
    user_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds))
):
    """
    Reset user password (Admin only)
    """
    try:
        logger.info(
            "Password reset request",
            user_id=user_id,
            admin_user_id=current_user
        )
        
        # TODO: Check permissions - only admins can reset passwords
        # current_user_obj = await get_user_by_id(db, current_user)
        # if current_user_obj.role != "ADMIN":
        #     raise AuthorizationException("Only administrators can reset passwords")
        
        # Generate new temporary password
        temp_password = "NewPass123!"  # In real implementation, generate random password
        hashed_password = get_password_hash(temp_password)
        
        # TODO: Implement actual database logic
        # await update_user_password(db, user_id, hashed_password)
        
        # TODO: Send email with new password
        # user = await get_user_by_id(db, user_id)
        # await send_password_reset_email(user.email, user.username, temp_password)
        
        logger.info(
            "Password reset successfully",
            user_id=user_id
        )
        
        return {
            "success": True,
            "message": "Password reset successfully",
            "user_id": user_id,
            "temporary_password": temp_password  # Remove in production
        }
        
    except Exception as e:
        logger.error("Password reset failed", user_id=user_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )


@router.get("/dashboard/summary", response_model=dict)
async def get_user_dashboard_summary(
    db: AsyncSession = Depends(get_async_session),
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds))
):
    """
    Get user summary for dashboard
    """
    try:
        # TODO: Implement actual database logic
        # summary = await get_user_summary(db)
        
        # Mock response
        summary = {
            "total_users": 245,
            "active": 220,
            "inactive": 15,
            "suspended": 10,
            "by_role": {
                "USER": 180,
                "TECHNICIAN": 35,
                "MANAGER": 25,
                "AUDITOR": 3,
                "ADMIN": 2
            },
            "by_department": {
                "IT": 45,
                "Sales": 65,
                "Marketing": 35,
                "Finance": 25,
                "HR": 15,
                "Operations": 55
            },
            "recent_activity": {
                "new_users_this_month": 8,
                "active_sessions": 156,
                "password_resets_this_week": 3
            },
            "login_stats": {
                "daily_avg": 198,
                "peak_concurrent": 145,
                "failed_attempts_today": 12
            }
        }
        
        return summary
        
    except Exception as e:
        logger.error("Failed to get user summary", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user summary"
        )