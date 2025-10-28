#!/usr/bin/env python3
"""
Endpoint de teste temporário para debug
"""

from fastapi import FastAPI, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from app.crud.user import authenticate_user
from app.core.security import create_access_token, create_refresh_token
import uvicorn

app = FastAPI(title="Test Login Debug")

@app.post("/test-login")
async def test_login(
    request: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """Endpoint de teste sem middlewares"""
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return {"error": "username and password required"}
        
        # Autenticar usuário
        user = await authenticate_user(db, username, password)
        
        if not user:
            return {"error": "Invalid credentials"}
        
        if not user.is_active:
            return {"error": "Account disabled"}
        
        # Criar tokens
        role = user.role.value if hasattr(user.role, 'value') else user.role
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": role}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id)}, user_id=str(user.id)
        )
        
        return {
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "role": role
        }
        
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)