"""
User CRUD operations
"""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.core.security import get_password_hash, verify_password


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """Get user by username"""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username_or_email(db: AsyncSession, username: str, email: str) -> Optional[User]:
    """Get user by username or email"""
    result = await db.execute(
        select(User).where(
            or_(User.username == username, User.email == email)
        )
    )
    return result.scalar_one_or_none()


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """Authenticate user with username/email and password"""
    # Try to find user by username or email
    result = await db.execute(
        select(User).where(
            or_(User.username == username, User.email == username)
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    return user


async def create_user(
    db: AsyncSession,
    username: str,
    email: str,
    full_name: str,
    password: str,
    role: str = "USER",
    **kwargs
) -> User:
    """Create new user"""
    hashed_password = get_password_hash(password)
    
    user = User(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
        role=role,
        **kwargs
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


async def update_user(db: AsyncSession, user_id: int, **kwargs) -> Optional[User]:
    """Update user"""
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    await db.commit()
    await db.refresh(user)
    
    return user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """Delete user"""
    user = await get_user_by_id(db, user_id)
    if not user:
        return False
    
    await db.delete(user)
    await db.commit()
    
    return True


async def get_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[dict] = None
) -> List[User]:
    """Get users with pagination and filters"""
    query = select(User)
    
    if filters:
        if "role" in filters:
            query = query.where(User.role == filters["role"])
        if "is_active" in filters:
            query = query.where(User.is_active == filters["is_active"])
        if "department" in filters:
            query = query.where(User.department == filters["department"])
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    
    return result.scalars().all()