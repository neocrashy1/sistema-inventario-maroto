"""
Auditoria models for Levitiis inventory system
Physical inventory audit and reconciliation
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.core.database import Base


class TipoAuditoria(str, Enum):
    """Tipos de auditoria"""
    TOTAL = "total"
    CICLICA = "ciclica"
    AMOSTRAGEM = "amostragem"
    AD_HOC = "ad_hoc"


class StatusAuditoria(str, Enum):
    """Status da auditoria"""
    PLANEJADA = "planejada"
    EM_ANDAMENTO = "em_andamento"
    RECONCILIACAO = "reconciliacao"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"


class ResultadoItem(str, Enum):
    """Resultado da verificação do item"""
    CONFORME = "encontrado_conforme"
    DIVERGENTE = "encontrado_divergente"
    NAO_ENCONTRADO = "nao_encontrado"
    EXTRA = "extra_nao_cadastrado"


class Auditoria(Base):
    """
    Auditoria (Inventory Audit) model
    Manages physical inventory audits and reconciliation
    """
    __tablename__ = "auditorias"

    id = Column(Integer, primary_key=True, index=True)
    
    # Audit identification
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    nome = Column(String(200), nullable=False)
    tipo = Column(String(20), nullable=False, default=TipoAuditoria.CICLICA)
    
    # Scope definition
    escopo = Column(JSON, nullable=True)  # Setores, locais, categorias incluídas
    criterios_priorizacao = Column(JSON, nullable=True)  # Critérios de risco/valor
    # Compatibilidade com API: listas serializadas
    escopo_setores = Column(String(500), nullable=True)
    escopo_locais = Column(String(500), nullable=True)
    
    # Status and timeline
    status = Column(String(20), nullable=False, default=StatusAuditoria.PLANEJADA)
    # Planejamento
    data_inicio_planejada = Column(DateTime(timezone=True), nullable=True)
    data_fim_planejada = Column(DateTime(timezone=True), nullable=True)
    # Execução
    data_inicio = Column(DateTime(timezone=True), nullable=True)
    data_fim = Column(DateTime(timezone=True), nullable=True)
    data_fim_prevista = Column(DateTime(timezone=True), nullable=True)
    data_fim_real = Column(DateTime(timezone=True), nullable=True)
    # Reconciliação e finalização
    data_reconciliacao = Column(DateTime(timezone=True), nullable=True)
    data_finalizacao = Column(DateTime(timezone=True), nullable=True)
    
    # Audit team
    criado_por = Column(Integer, ForeignKey("users.id"), nullable=False)
    responsavel_auditoria = Column(Integer, ForeignKey("users.id"), nullable=True)
    equipe_auditores = Column(JSON, nullable=True)  # Array de user IDs
    finalizado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Results summary
    total_itens_esperados = Column(Integer, default=0)
    total_itens_verificados = Column(Integer, default=0)
    total_conformes = Column(Integer, default=0)
    total_divergentes = Column(Integer, default=0)
    total_nao_encontrados = Column(Integer, default=0)
    total_extras = Column(Integer, default=0)
    # Compatibilidade com respostas
    total_itens = Column(Integer, default=0)
    itens_conformes = Column(Integer, default=0)
    itens_divergentes = Column(Integer, default=0)
    itens_nao_encontrados = Column(Integer, default=0)
    itens_extras = Column(Integer, default=0)
    
    # Metadata
    observacoes = Column(Text, nullable=True)
    observacoes_finais = Column(Text, nullable=True)
    hash_auditoria = Column(String(64), nullable=True)  # Hash para trilha de auditoria
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    criador = relationship("User", foreign_keys=[criado_por])
    responsavel = relationship("User", foreign_keys=[responsavel_auditoria])
    finalizador = relationship("User", foreign_keys=[finalizado_por])
    itens = relationship("AuditoriaItem", back_populates="auditoria", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Auditoria(id={self.id}, codigo='{self.codigo}', tipo='{self.tipo}', status='{self.status}')>"


class AuditoriaItem(Base):
    """
    AuditoriaItem (Audit Item) model
    Individual asset verification within an audit
    """
    __tablename__ = "auditoria_itens"

    id = Column(Integer, primary_key=True, index=True)
    
    # Audit and asset reference
    auditoria_id = Column(Integer, ForeignKey("auditorias.id"), nullable=False)
    ativo_id = Column(Integer, ForeignKey("ativos.id"), nullable=True)  # Null para extras
    
    # Reading information
    leitura_codigo = Column(String(100), nullable=True)  # Código lido via QR/NFC
    leitura_manual = Column(String(100), nullable=True)  # Código digitado manualmente
    codigo_lido = Column(String(100), nullable=True)
    
    # Verification result
    resultado = Column(String(30), nullable=False, default=ResultadoItem.CONFORME)
    divergencias = Column(Text, nullable=True)  # Detalhes das divergências encontradas (CSV)
    
    # Location verification
    local_esperado_id = Column(Integer, ForeignKey("locais.id"), nullable=True)
    local_encontrado_id = Column(Integer, ForeignKey("locais.id"), nullable=True)
    responsavel_esperado_id = Column(Integer, ForeignKey("responsaveis.id"), nullable=True)
    
    # Evidence and observations
    observacao = Column(Text, nullable=True)
    foto_url = Column(String(500), nullable=True)
    evidencias = Column(JSON, nullable=True)  # URLs de fotos/documentos
    estado_encontrado = Column(String(30), nullable=True)
    observacoes_esperadas = Column(Text, nullable=True)
    observacoes_coleta = Column(Text, nullable=True)
    foto_evidencia_url = Column(String(500), nullable=True)
    data_coleta = Column(DateTime(timezone=True), nullable=True)
    
    # Audit trail
    verificado_por = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp_verificacao = Column(DateTime(timezone=True), server_default=func.now())
    coordenadas_gps = Column(String(50), nullable=True)  # lat,lng
    coletado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Reconciliation
    aprovado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    data_aprovacao = Column(DateTime(timezone=True), nullable=True)
    acao_corretiva = Column(Text, nullable=True)
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    auditoria = relationship("Auditoria", back_populates="itens")
    ativo = relationship("Ativo", back_populates="auditorias_itens")
    local_esperado = relationship("Local", foreign_keys=[local_esperado_id])
    local_encontrado = relationship("Local", foreign_keys=[local_encontrado_id])
    verificador = relationship("User", foreign_keys=[verificado_por])
    aprovador = relationship("User", foreign_keys=[aprovado_por])
    coletor = relationship("User", foreign_keys=[coletado_por])
    responsavel_esperado = relationship("Responsavel", foreign_keys=[responsavel_esperado_id])

    def __repr__(self):
        return f"<AuditoriaItem(id={self.id}, auditoria_id={self.auditoria_id}, resultado='{self.resultado}')>"