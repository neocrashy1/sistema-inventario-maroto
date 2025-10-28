"""
Manutencao model for Levitiis inventory system
Asset maintenance and support ticket management
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from datetime import datetime, timedelta
from app.core.database import Base


class TipoManutencao(str, Enum):
    """Tipos de manutenção"""
    PREVENTIVA = "preventiva"
    CORRETIVA = "corretiva"
    GARANTIA = "garantia"
    UPGRADE = "upgrade"


class StatusManutencao(str, Enum):
    """Status da manutenção"""
    ABERTO = "aberto"
    EM_ANDAMENTO = "em_andamento"
    AGUARDANDO_PECA = "aguardando_peca"
    AGUARDANDO_APROVACAO = "aguardando_aprovacao"
    RESOLVIDO = "resolvido"
    FECHADO = "fechado"
    CANCELADO = "cancelado"


class PrioridadeManutencao(str, Enum):
    """Prioridade da manutenção"""
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"


class Manutencao(Base):
    """
    Manutencao (Maintenance) model
    Manages asset maintenance requests and service tickets
    """
    __tablename__ = "manutencoes"

    id = Column(Integer, primary_key=True, index=True)
    
    # Identification
    numero_chamado = Column(String(50), unique=True, nullable=False, index=True)
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=False)
    
    # Asset and classification
    ativo_id = Column(Integer, ForeignKey("ativos.id"), nullable=False)
    tipo = Column(String(20), nullable=False, default=TipoManutencao.CORRETIVA)
    prioridade = Column(String(10), nullable=False, default=PrioridadeManutencao.MEDIA)
    categoria_problema = Column(String(100), nullable=True)
    
    # Status and timeline
    status = Column(String(30), nullable=False, default=StatusManutencao.ABERTO)
    data_abertura = Column(DateTime(timezone=True), server_default=func.now())
    data_inicio_atendimento = Column(DateTime(timezone=True), nullable=True)
    data_resolucao = Column(DateTime(timezone=True), nullable=True)
    data_fechamento = Column(DateTime(timezone=True), nullable=True)
    
    # SLA management
    sla_horas = Column(Integer, nullable=True)  # SLA em horas baseado na categoria
    data_vencimento_sla = Column(DateTime(timezone=True), nullable=True)
    sla_pausado = Column(Integer, default=0)  # 0=não, 1=sim
    tempo_pausado_minutos = Column(Integer, default=0)
    
    # Assignment and responsibility
    aberto_por = Column(Integer, ForeignKey("users.id"), nullable=False)
    atribuido_para = Column(Integer, ForeignKey("users.id"), nullable=True)
    aprovado_por = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Financial information
    custo_estimado = Column(Numeric(10, 2), nullable=True)
    custo_real = Column(Numeric(10, 2), nullable=True)
    custo_pecas = Column(Numeric(10, 2), nullable=True)
    custo_mao_obra = Column(Numeric(10, 2), nullable=True)
    
    # Downtime tracking
    tempo_downtime_minutos = Column(Integer, default=0)
    impacto_operacional = Column(String(20), nullable=True)  # baixo, medio, alto, critico
    
    # Resolution information
    solucao = Column(Text, nullable=True)
    causa_raiz = Column(Text, nullable=True)
    pecas_utilizadas = Column(Text, nullable=True)
    
    # External service
    fornecedor_servico = Column(String(150), nullable=True)
    numero_os_externa = Column(String(100), nullable=True)
    
    # Metadata
    observacoes = Column(Text, nullable=True)
    satisfacao_usuario = Column(Integer, nullable=True)  # 1-5 estrelas
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    ativo = relationship("Ativo", back_populates="manutencoes")
    solicitante = relationship("User", foreign_keys=[aberto_por])
    tecnico = relationship("User", foreign_keys=[atribuido_para])
    aprovador = relationship("User", foreign_keys=[aprovado_por])

    @property
    def sla_vencido(self):
        """Verifica se o SLA foi vencido"""
        if not self.data_vencimento_sla:
            return False
        return datetime.now() > self.data_vencimento_sla and self.status not in [StatusManutencao.RESOLVIDO, StatusManutencao.FECHADO]

    @property
    def tempo_resolucao_horas(self):
        """Calcula o tempo de resolução em horas"""
        if not self.data_resolucao or not self.data_abertura:
            return None
        delta = self.data_resolucao - self.data_abertura
        return round(delta.total_seconds() / 3600, 2)

    @property
    def percentual_sla(self):
        """Calcula o percentual do SLA utilizado"""
        if not self.sla_horas or not self.data_vencimento_sla:
            return None
        
        tempo_decorrido = datetime.now() - self.data_abertura
        tempo_total_sla = timedelta(hours=self.sla_horas)
        
        return min(100, round((tempo_decorrido.total_seconds() / tempo_total_sla.total_seconds()) * 100, 1))

    def __repr__(self):
        return f"<Manutencao(id={self.id}, numero='{self.numero_chamado}', tipo='{self.tipo}', status='{self.status}')>"