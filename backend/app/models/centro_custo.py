"""
Centro de Custo model for Levitiis inventory system
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class CentroCusto(Base):
    """
    Centro de Custo (Cost Center) model
    Represents cost centers for asset allocation and financial tracking
    """
    __tablename__ = "centros_custo"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, nullable=False, index=True)
    nome = Column(String(100), nullable=False, index=True)
    descricao = Column(Text)
    orcamento_anual = Column(Numeric(15, 2), nullable=True)
    responsavel_financeiro = Column(String(100), nullable=True)
    ativo = Column(Integer, default=1)  # 1=ativo, 0=inativo
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    setores = relationship("Setor", back_populates="centro_custo")
    ativos = relationship("Ativo", back_populates="centro_custo")

    def __repr__(self):
        return f"<CentroCusto(id={self.id}, codigo='{self.codigo}', nome='{self.nome}')>"