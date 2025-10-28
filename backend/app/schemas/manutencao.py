"""
Pydantic schemas for Manutencao (Maintenance) API
Data validation and serialization models
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, validator


class ManutencaoBase(BaseModel):
    """Base schema for Manutencao"""
    ativo_id: int = Field(..., description="ID do ativo")
    tipo: str = Field(..., description="Tipo de manutenção")
    prioridade: str = Field(..., description="Prioridade da manutenção")
    titulo: str = Field(..., min_length=1, max_length=200, description="Título da solicitação")
    descricao: str = Field(..., min_length=1, max_length=2000, description="Descrição detalhada")
    categoria: Optional[str] = Field(None, max_length=100, description="Categoria da manutenção")
    subcategoria: Optional[str] = Field(None, max_length=100, description="Subcategoria da manutenção")
    data_solicitacao: Optional[datetime] = Field(None, description="Data da solicitação")
    data_prevista_inicio: Optional[datetime] = Field(None, description="Data prevista para início")
    data_prevista_fim: Optional[datetime] = Field(None, description="Data prevista para fim")


class ManutencaoCreate(ManutencaoBase):
    """Schema for creating Manutencao"""
    atribuido_para: Optional[int] = Field(None, description="ID do usuário responsável")
    fornecedor_externo_id: Optional[int] = Field(None, description="ID do fornecedor externo")


class ManutencaoUpdate(BaseModel):
    """Schema for updating Manutencao"""
    titulo: Optional[str] = Field(None, min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, min_length=1, max_length=2000)
    prioridade: Optional[str] = Field(None)
    categoria: Optional[str] = Field(None, max_length=100)
    subcategoria: Optional[str] = Field(None, max_length=100)
    data_prevista_inicio: Optional[datetime] = Field(None)
    data_prevista_fim: Optional[datetime] = Field(None)
    atribuido_para: Optional[int] = Field(None)
    fornecedor_externo_id: Optional[int] = Field(None)
    status: Optional[str] = Field(None)
    progresso_percentual: Optional[int] = Field(None, ge=0, le=100)
    observacoes_tecnicas: Optional[str] = Field(None, max_length=2000)
    custo_estimado: Optional[Decimal] = Field(None, ge=0)
    custo_real: Optional[Decimal] = Field(None, ge=0)
    tempo_inatividade_horas: Optional[Decimal] = Field(None, ge=0)
    pecas_utilizadas: Optional[str] = Field(None, max_length=1000)
    servicos_realizados: Optional[str] = Field(None, max_length=2000)
    observacoes_resolucao: Optional[str] = Field(None, max_length=2000)


class ManutencaoResponse(ManutencaoBase):
    """Schema for Manutencao response"""
    id: int
    numero_ticket: str
    status: str
    classificacao: Optional[str] = None
    sla_horas: Optional[int] = None
    data_vencimento_sla: Optional[datetime] = None
    atribuido_para: Optional[int] = None
    fornecedor_externo_id: Optional[int] = None
    progresso_percentual: int = 0
    observacoes_tecnicas: Optional[str] = None
    custo_estimado: Optional[Decimal] = None
    custo_real: Optional[Decimal] = None
    tempo_inatividade_horas: Optional[Decimal] = None
    pecas_utilizadas: Optional[str] = None
    servicos_realizados: Optional[str] = None
    data_inicio_real: Optional[datetime] = None
    data_fim_real: Optional[datetime] = None
    observacoes_resolucao: Optional[str] = None
    avaliacao_qualidade: Optional[int] = None
    comentarios_avaliacao: Optional[str] = None
    fornecedor_externo: Optional[str] = None
    criado_por: Optional[int] = None
    finalizado_por: Optional[int] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    
    # Propriedades calculadas
    sla_vencido: bool = False
    tempo_resolucao_horas: Optional[float] = None
    percentual_sla_utilizado: Optional[float] = None

    class Config:
        from_attributes = True


class ManutencaoList(BaseModel):
    """Schema for paginated Manutencao list"""
    items: List[ManutencaoResponse]
    total: int
    skip: int
    limit: int


class ManutencaoFilter(BaseModel):
    """Schema for Manutencao filtering"""
    ativo_id: Optional[int] = None
    tipo: Optional[str] = None
    status: Optional[str] = None
    prioridade: Optional[str] = None
    categoria: Optional[str] = None
    atribuido_para: Optional[int] = None
    fornecedor_externo_id: Optional[int] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    sla_vencido: Optional[bool] = None
    texto: Optional[str] = Field(None, description="Busca em título e descrição")


class ManutencaoMetricas(BaseModel):
    """Schema for maintenance metrics"""
    total_abertas: int
    total_em_andamento: int
    total_vencidas: int
    total_finalizadas_mes: int
    tempo_medio_resolucao_horas: float
    percentual_sla_cumprido: float
    custo_total_mes: Decimal
    ativos_em_manutencao: int


class ManutencaoDistribuicao(BaseModel):
    """Schema for maintenance distribution"""
    por_tipo: Dict[str, int]
    por_status: Dict[str, int]
    por_prioridade: Dict[str, int]
    por_categoria: Dict[str, int]


class HistoricoManutencao(BaseModel):
    """Schema for maintenance history"""
    ativo_id: int
    manutencoes: List[ManutencaoResponse]
    total_manutencoes: int
    custo_total: Decimal
    tempo_inatividade_total: Decimal
    ultima_manutencao: Optional[datetime] = None


class AvaliacaoManutencao(BaseModel):
    """Schema for maintenance evaluation"""
    manutencao_id: int
    avaliacao_qualidade: int = Field(..., ge=1, le=5, description="Avaliação de 1 a 5")
    comentarios: Optional[str] = Field(None, max_length=1000, description="Comentários da avaliação")
    
    @validator('avaliacao_qualidade')
    def validate_avaliacao(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Avaliação deve ser entre 1 e 5')
        return v


class RelatorioManutencao(BaseModel):
    """Schema for maintenance report"""
    periodo_inicio: datetime
    periodo_fim: datetime
    total_solicitacoes: int
    total_finalizadas: int
    percentual_conclusao: float
    tempo_medio_resolucao: float
    custo_total: Decimal
    distribuicao: ManutencaoDistribuicao
    top_ativos_manutencao: List[Dict[str, Any]]
    sla_performance: Dict[str, Any]


class AlertaSLA(BaseModel):
    """Schema for SLA alerts"""
    manutencao_id: int
    numero_ticket: str
    ativo_codigo: str
    titulo: str
    sla_horas: int
    horas_restantes: float
    percentual_utilizado: float
    status: str
    atribuido_para: Optional[str] = None