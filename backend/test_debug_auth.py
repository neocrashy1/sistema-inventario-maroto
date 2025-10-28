#!/usr/bin/env python3
"""
Teste de debug para verificar problema de autenticação
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import get_current_user_id, security, verify_token
import uvicorn

app = FastAPI(title="Debug Auth Test")

@app.get("/test-no-auth")
async def test_no_auth():
    """Teste sem autenticação"""
    return {"message": "OK - sem autenticação"}

@app.get("/test-with-auth")
async def test_with_auth(
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds))
):
    """Teste com autenticação"""
    return {"message": "OK - com autenticação", "user_id": current_user}

@app.get("/test-token-direct")
async def test_token_direct(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Teste direto do token"""
    try:
        print(f"Token recebido: {credentials.credentials[:50]}...")
        token = credentials.credentials
        payload = verify_token(token, "access")
        print(f"Payload verificado: {payload}")
        
        if payload is None:
            print("Payload é None - token inválido")
            raise HTTPException(status_code=401, detail="Token inválido")
        
        return {"message": "OK - token direto", "payload": payload}
    except Exception as e:
        print(f"Erro no teste direto: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@app.get("/test-verify-only")
async def test_verify_only(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Teste apenas da verificação do token"""
    try:
        from app.core.config import settings
        import jwt
        
        token = credentials.credentials
        print(f"Token: {token[:50]}...")
        print(f"Secret Key: {settings.SECRET_KEY}")
        print(f"Algorithm: {settings.ALGORITHM}")
        
        # Teste direto do JWT
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                leeway=60,
                options={"verify_iat": False}
            )
            print(f"JWT decode success: {payload}")
            return {"message": "JWT decode OK", "payload": payload}
        except Exception as jwt_error:
            print(f"JWT decode error: {jwt_error}")
            return {"message": "JWT decode failed", "error": str(jwt_error)}
            
    except Exception as e:
        print(f"Erro geral: {e}")
        return {"message": "Erro geral", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="debug")