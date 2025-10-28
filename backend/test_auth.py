"""
Test authentication functionality
"""

import asyncio
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_async_session, async_engine
from app.models.user import User
from app.core.security import verify_password


async def test_auth():
    """Test authentication"""
    try:
        # Create session
        async with AsyncSession(async_engine) as db:
            # Find user
            result = await db.execute(
                select(User).where(User.email == "admin@levitiis.com")
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print("❌ User not found")
                return
            
            print(f"✅ User found: {user.email}")
            print(f"   Username: {user.username}")
            print(f"   Role: {user.role}")
            print(f"   Active: {user.is_active}")
            print(f"   Hashed password: {user.hashed_password[:50]}...")
            
            # Test password verification
            password = "admin123"
            print(f"\n🔐 Testing password: {password}")
            
            # Test with bcrypt directly
            try:
                is_valid_bcrypt = bcrypt.checkpw(
                    password.encode('utf-8'), 
                    user.hashed_password.encode('utf-8')
                )
                print(f"   Bcrypt direct: {is_valid_bcrypt}")
            except Exception as e:
                print(f"   Bcrypt direct error: {e}")
            
            # Test with verify_password function
            try:
                is_valid_func = verify_password(password, user.hashed_password)
                print(f"   verify_password function: {is_valid_func}")
            except Exception as e:
                print(f"   verify_password error: {e}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_auth())