"""
Movimentacao model for Levitiis inventory system
Asset movement and custody chain tracking
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.core.database import Base


class TipoMovimentacao(str, Enum):
    """Tipos de movimentação"""
    TRANSFERENCIA = "transferencia"
    ALOCACAO = "alocacao"
    DEVOLUCAO = "devolucao"
    MANUTENCAO = "manutencao"
    BAIXA = "baixa"


class StatusMovimentacao(str, Enum):
    """Status da movimentação"""
    PENDENTE = "pendente"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"
    CONCLUIDA = "concluida"


class Movimentacao(Base):
    """
    Movimentacao (Asset Movement) model
    Tracks asset movements and maintains custody chain
    """
    __tablename__ = "movimentacoes"

    id = Column(Integer, primary_key=True, index=True)
    
    # Asset and movement type
    ativo_id = Column(Integer, ForeignKey("ativos.id"), nullable=False)
    tipo = Column(String(20), nullable=False, default=TipoMovimentacao.TRANSFERENCIA)
    motivo = Column(String(200), nullable=False)
    
    # Origin and destination locations
    de_local_id = Column(Integer, ForeignKey("locais.id"), nullable=True)
    para_local_id = Column(Integer, ForeignKey("locais.id"), nullable=True)
    
    # Origin and destination responsible persons
    de_responsavel_id = Column(Integer, ForeignKey("responsaveis.id"), nullable=True)
    para_responsavel_id = Column(Integer, ForeignKey("responsaveis.id"), nullable=True)
    
    # Movement control
    status = Column(String(20), nullable=False, default=StatusMovimentacao.PENDENTE)
    data_solicitacao = Column(DateTime(timezone=True), server_default=func.now())
    data_aprovacao = Column(DateTime(timezone=True), nullable=True)
    data_conclusao = Column(DateTime(timezone=True), nullable=True)
    
    # Approval workflow
    solicitado_por = Column(Integer, ForeignKey("users.id"), nullable=False)
    aprovado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    executado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Digital custody term
    termo_responsabilidade_url = Column(String(500), nullable=True)
    termo_assinado_em = Column(DateTime(timezone=True), nullable=True)
    
    # Additional information
    observacoes = Column(Text, nullable=True)
    valor_limite_aprovacao = Column(Integer, default=5000)  # Valor em reais para aprovação automática
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    ativo = relationship("Ativo", back_populates="movimentacoes")
    local_origem = relationship("Local", foreign_keys=[de_local_id], back_populates="movimentacoes_origem")
    local_destino = relationship("Local", foreign_keys=[para_local_id], back_populates="movimentacoes_destino")
    responsavel_origem = relationship("Responsavel", foreign_keys=[de_responsavel_id], back_populates="movimentacoes_origem")
    responsavel_destino = relationship("Responsavel", foreign_keys=[para_responsavel_id], back_populates="movimentacoes_destino")
    
    solicitante = relationship("User", foreign_keys=[solicitado_por])
    aprovador = relationship("User", foreign_keys=[aprovado_por])
    executor = relationship("User", foreign_keys=[executado_por])

    def __repr__(self):
        return f"<Movimentacao(id={self.id}, ativo_id={self.ativo_id}, tipo='{self.tipo}', status='{self.status}')>"