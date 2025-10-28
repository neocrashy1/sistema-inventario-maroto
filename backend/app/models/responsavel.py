"""
Responsavel model for Levitiis inventory system
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Responsavel(Base):
    """
    Responsavel (Asset Responsible) model
    Represents people responsible for assets within the organization
    """
    __tablename__ = "responsaveis"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, index=True)
    email = Column(String(150), nullable=False, unique=True, index=True)
    telefone = Column(String(20), nullable=True)
    cargo = Column(String(100), nullable=True)
    matricula = Column(String(50), nullable=True, unique=True, index=True)
    
    # Organizational relationships
    setor_id = Column(Integer, ForeignKey("setores.id"), nullable=False)
    gestor_id = Column(Integer, ForeignKey("responsaveis.id"), nullable=True)
    
    # Status and metadata
    ativo = Column(Integer, default=1)  # 1=ativo, 0=inativo
    observacoes = Column(Text)
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    setor = relationship("Setor", back_populates="responsaveis")
    gestor = relationship("Responsavel", remote_side=[id], back_populates="subordinados")
    subordinados = relationship("Responsavel", back_populates="gestor")
    
    # Asset relationships
    ativos = relationship("Ativo", back_populates="responsavel")
    movimentacoes_origem = relationship("Movimentacao", foreign_keys="Movimentacao.de_responsavel_id", back_populates="responsavel_origem")
    movimentacoes_destino = relationship("Movimentacao", foreign_keys="Movimentacao.para_responsavel_id", back_populates="responsavel_destino")

    def __repr__(self):
        return f"<Responsavel(id={self.id}, nome='{self.nome}', email='{self.email}')>"