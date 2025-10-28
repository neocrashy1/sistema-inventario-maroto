"""
Script para inicializar o banco de dados
"""

import asyncio
from sqlalchemy import create_engine
from app.core.database import Base, sync_engine
from app.core.config import settings
from app.models import user, asset, machine, ticket, alert, location, movement

def create_tables():
    """Criar todas as tabelas"""
    print("Criando tabelas do banco de dados...")
    Base.metadata.create_all(bind=sync_engine)
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    create_tables()