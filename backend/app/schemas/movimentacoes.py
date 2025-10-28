"""
Pydantic schemas for Movimentacoes (Asset Movements) API
Data validation and serialization models
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class MovimentacaoBase(BaseModel):
    """Base schema for Movimentacao"""
    ativo_id: int = Field(..., description="ID do ativo")
    tipo: str = Field(..., description="Tipo de movimentação")
    local_origem_id: Optional[int] = Field(None, description="ID do local de origem")
    local_destino_id: Optional[int] = Field(None, description="ID do local de destino")
    responsavel_origem_id: Optional[int] = Field(None, description="ID do responsável de origem")
    responsavel_destino_id: Optional[int] = Field(None, description="ID do responsável de destino")
    motivo: str = Field(..., min_length=1, max_length=500, description="Motivo da movimentação")
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações")
    data_prevista: Optional[datetime] = Field(None, description="Data prevista para execução")


class MovimentacaoCreate(MovimentacaoBase):
    """Schema for creating Movimentacao"""
    pass


class MovimentacaoUpdate(BaseModel):
    """Schema for updating Movimentacao"""
    local_destino_id: Optional[int] = Field(None)
    responsavel_destino_id: Optional[int] = Field(None)
    motivo: Optional[str] = Field(None, min_length=1, max_length=500)
    observacoes: Optional[str] = Field(None, max_length=1000)
    data_prevista: Optional[datetime] = Field(None)


class MovimentacaoResponse(MovimentacaoBase):
    """Schema for Movimentacao response"""
    id: int
    status: str
    requer_aprovacao: bool = False
    solicitado_por: Optional[int] = None
    aprovado_por: Optional[int] = None
    data_solicitacao: datetime
    data_aprovacao: Optional[datetime] = None
    data_execucao: Optional[datetime] = None
    observacoes_aprovacao: Optional[str] = None
    termo_responsabilidade_url: Optional[str] = None
    hash_integridade: Optional[str] = None

    class Config:
        from_attributes = True


class MovimentacaoList(BaseModel):
    """Schema for paginated Movimentacao list"""
    items: List[MovimentacaoResponse]
    total: int
    skip: int
    limit: int


class TermoResponsabilidade(BaseModel):
    """Schema for responsibility term"""
    movimentacao_id: int
    ativo: Dict[str, Any]
    tipo_movimentacao: str
    data_movimentacao: Optional[str] = None
    responsavel_origem: Optional[Dict[str, Any]] = None
    responsavel_destino: Optional[Dict[str, Any]] = None
    observacoes: Optional[str] = None
    hash_integridade: str


class CadeiaCustodia(BaseModel):
    """Schema for custody chain"""
    ativo: Dict[str, Any]
    cadeia_custodia: List[Dict[str, Any]]


class MovimentacaoPendente(BaseModel):
    """Schema for pending movements"""
    total: int
    movimentacoes: List[MovimentacaoResponse]