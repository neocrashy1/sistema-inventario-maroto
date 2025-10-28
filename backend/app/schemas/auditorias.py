"""
Pydantic schemas for Auditorias (Audits) API
Data validation and serialization models
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AuditoriaBase(BaseModel):
    """Base schema for Auditoria"""
    tipo: str = Field(..., description="Tipo de auditoria")
    nome: str = Field(..., min_length=1, max_length=200, description="Nome da auditoria")
    descricao: Optional[str] = Field(None, max_length=1000, description="Descrição da auditoria")
    data_inicio_planejada: Optional[datetime] = Field(None, description="Data planejada para início")
    data_fim_planejada: Optional[datetime] = Field(None, description="Data planejada para fim")
    equipe_auditoria: Optional[str] = Field(None, max_length=500, description="Equipe responsável")
    tamanho_amostra: Optional[int] = Field(None, ge=1, description="Tamanho da amostra (para auditoria por amostragem)")


class AuditoriaCreate(AuditoriaBase):
    """Schema for creating Auditoria"""
    escopo_setores: Optional[List[int]] = Field(None, description="IDs dos setores no escopo")
    escopo_locais: Optional[List[int]] = Field(None, description="IDs dos locais no escopo")


class AuditoriaUpdate(BaseModel):
    """Schema for updating Auditoria"""
    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=1000)
    data_inicio_planejada: Optional[datetime] = Field(None)
    data_fim_planejada: Optional[datetime] = Field(None)
    equipe_auditoria: Optional[str] = Field(None, max_length=500)
    observacoes_finais: Optional[str] = Field(None, max_length=1000)


class AuditoriaResponse(AuditoriaBase):
    """Schema for Auditoria response"""
    id: int
    status: str
    escopo_setores: Optional[str] = None
    escopo_locais: Optional[str] = None
    total_itens: Optional[int] = None
    itens_conformes: Optional[int] = None
    itens_divergentes: Optional[int] = None
    itens_nao_encontrados: Optional[int] = None
    itens_extras: Optional[int] = None
    data_inicio: Optional[datetime] = None
    data_fim: Optional[datetime] = None
    data_reconciliacao: Optional[datetime] = None
    data_finalizacao: Optional[datetime] = None
    criado_por: Optional[int] = None
    finalizado_por: Optional[int] = None
    observacoes_finais: Optional[str] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


class AuditoriaList(BaseModel):
    """Schema for paginated Auditoria list"""
    items: List[AuditoriaResponse]
    total: int
    skip: int
    limit: int


class AuditoriaItemBase(BaseModel):
    """Base schema for AuditoriaItem"""
    auditoria_id: int
    ativo_id: int
    local_esperado_id: Optional[int] = None
    responsavel_esperado_id: Optional[int] = None
    estado_esperado: Optional[str] = None
    observacoes_esperadas: Optional[str] = Field(None, max_length=500)


class AuditoriaItemCreate(AuditoriaItemBase):
    """Schema for creating AuditoriaItem"""
    pass


class AuditoriaItemResponse(AuditoriaItemBase):
    """Schema for AuditoriaItem response"""
    id: int
    codigo_lido: Optional[str] = None
    local_encontrado_id: Optional[int] = None
    estado_encontrado: Optional[str] = None
    resultado: Optional[str] = None
    divergencias: Optional[str] = None
    observacoes_coleta: Optional[str] = None
    foto_evidencia_url: Optional[str] = None
    data_coleta: Optional[datetime] = None
    coletado_por: Optional[int] = None
    reconciliado: bool = False
    data_reconciliacao: Optional[datetime] = None
    reconciliado_por: Optional[int] = None
    observacoes_reconciliacao: Optional[str] = None

    class Config:
        from_attributes = True


class AuditoriaItemList(BaseModel):
    """Schema for paginated AuditoriaItem list"""
    items: List[AuditoriaItemResponse]
    total: int
    skip: int
    limit: int


class ListaContagem(BaseModel):
    """Schema for audit counting list"""
    auditoria_id: int
    total_itens: int
    filtros: Dict[str, Any]
    itens: List[Dict[str, Any]]


class ColetaLeitura(BaseModel):
    """Schema for audit reading collection"""
    item_id: int
    codigo_lido: Optional[str] = Field(None, description="Código lido via QR/NFC")
    local_encontrado_id: Optional[int] = Field(None, description="ID do local onde foi encontrado")
    estado_encontrado: Optional[str] = Field(None, description="Estado físico encontrado")
    observacoes: Optional[str] = Field(None, max_length=500, description="Observações da coleta")
    foto_url: Optional[str] = Field(None, description="URL da foto de evidência")


class RelatorioReconciliacao(BaseModel):
    """Schema for reconciliation report"""
    auditoria_id: int
    tipo: str
    status: str
    data_inicio: Optional[str] = None
    data_reconciliacao: Optional[str] = None
    resumo: Dict[str, Any]
    itens: Dict[str, List[Dict[str, Any]]]


class AuditoriaMetricas(BaseModel):
    """Schema for audit metrics"""
    auditorias_ativas: int
    auditorias_pendentes: int
    itens_divergentes_abertos: int
    percentual_conformidade_media: float
    ativos_sem_auditoria_6_meses: int


class DivergenciaAuditoria(BaseModel):
    """Schema for audit divergence"""
    item_id: int
    ativo_id: int
    codigo: str
    patrimonio: Optional[str] = None
    descricao: str
    tipo_divergencia: List[str]
    local_esperado: Optional[str] = None
    local_encontrado: Optional[str] = None
    estado_esperado: Optional[str] = None
    estado_encontrado: Optional[str] = None
    observacoes: Optional[str] = None
    data_coleta: Optional[str] = None
    status_reconciliacao: str = "pendente"