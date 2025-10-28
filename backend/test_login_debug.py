#!/usr/bin/env python3
"""
Script de debug para testar o login isoladamente
"""

import asyncio
import sys
import os

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_async_session
from app.crud.user import authenticate_user
from app.core.security import create_access_token, create_refresh_token

async def test_login():
    """Teste isolado do login"""
    print("=== Teste de Login Debug ===")
    
    try:
        # Obter sessão do banco
        async for db in get_async_session():
            print("✓ Conexão com banco estabelecida")
            
            # Testar autenticação
            username = "admin"
            password = "admin123"
            
            print(f"Testando login com: {username} / {password}")
            
            user = await authenticate_user(db, username, password)
            
            if user:
                print(f"✓ Usuário autenticado: {user.username} (ID: {user.id})")
                print(f"  - Email: {user.email}")
                print(f"  - Role: {user.role}")
                print(f"  - Ativo: {user.is_active}")
                
                # Testar criação de tokens
                try:
                    role = user.role.value if hasattr(user.role, 'value') else user.role
                    access_token = create_access_token(
                        data={"sub": str(user.id), "username": user.username, "role": role}
                    )
                    refresh_token = create_refresh_token(
                        data={"sub": str(user.id)}, user_id=str(user.id)
                    )
                    
                    print("✓ Tokens criados com sucesso")
                    print(f"  - Access token: {access_token[:50]}...")
                    print(f"  - Refresh token: {refresh_token[:50]}...")
                    
                except Exception as e:
                    print(f"✗ Erro ao criar tokens: {e}")
                    import traceback
                    traceback.print_exc()
                    
            else:
                print("✗ Falha na autenticação")
                
            break
            
    except Exception as e:
        print(f"✗ Erro geral: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_login())