"""
Setor model for Levitiis inventory system
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Setor(Base):
    """
    Setor (Department) model
    Represents organizational departments within the company
    """
    __tablename__ = "setores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, index=True)
    codigo = Column(String(20), unique=True, nullable=False, index=True)
    descricao = Column(Text)
    gestor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    centro_custo_id = Column(Integer, ForeignKey("centros_custo.id"), nullable=True)
    ativo = Column(Integer, default=1)  # 1=ativo, 0=inativo
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    gestor = relationship("User", back_populates="setores_gerenciados")
    centro_custo = relationship("CentroCusto", back_populates="setores")
    locais = relationship("Local", back_populates="setor")
    ativos = relationship("Ativo", back_populates="setor")
    responsaveis = relationship("Responsavel", back_populates="setor")

    def __repr__(self):
        return f"<Setor(id={self.id}, nome='{self.nome}', codigo='{self.codigo}')>"