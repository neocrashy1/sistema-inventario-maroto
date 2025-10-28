"""
Pydantic schemas for Ativos (Assets) API
Data validation and serialization models
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, validator


class AtivoBase(BaseModel):
    """Base schema for Ativo"""
    codigo: str = Field(..., min_length=1, max_length=50, description="Código único do ativo")
    patrimonio: Optional[str] = Field(None, max_length=50, description="Número de patrimônio")
    categoria: str = Field(..., max_length=100, description="Categoria do ativo")
    subcategoria: Optional[str] = Field(None, max_length=100, description="Subcategoria do ativo")
    descricao: str = Field(..., min_length=1, max_length=500, description="Descrição do ativo")
    marca: Optional[str] = Field(None, max_length=100, description="Marca do ativo")
    modelo: Optional[str] = Field(None, max_length=100, description="Modelo do ativo")
    numero_serie: Optional[str] = Field(None, max_length=100, description="Número de série")
    estado: str = Field(default="novo", description="Estado físico do ativo")
    valor_aquisicao: Optional[Decimal] = Field(None, ge=0, description="Valor de aquisição")
    data_compra: Optional[date] = Field(None, description="Data da compra")
    nota_fiscal: Optional[str] = Field(None, max_length=100, description="Número da nota fiscal")
    vida_util_meses: Optional[int] = Field(None, ge=1, description="Vida útil em meses")
    centro_custo_id: Optional[int] = Field(None, description="ID do centro de custo")
    setor_id: Optional[int] = Field(None, description="ID do setor")
    local_id: Optional[int] = Field(None, description="ID do local")
    responsavel_id: Optional[int] = Field(None, description="ID do responsável")
    status: str = Field(default="ativo", description="Status do ativo")
    garantia_ate: Optional[date] = Field(None, description="Data de vencimento da garantia")
    fornecedor_id: Optional[int] = Field(None, description="ID do fornecedor")
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações")
    tags: Optional[str] = Field(None, max_length=500, description="Tags separadas por vírgula")


class AtivoCreate(AtivoBase):
    """Schema for creating Ativo"""
    pass


class AtivoUpdate(BaseModel):
    """Schema for updating Ativo"""
    codigo: Optional[str] = Field(None, min_length=1, max_length=50)
    patrimonio: Optional[str] = Field(None, max_length=50)
    categoria: Optional[str] = Field(None, max_length=100)
    subcategoria: Optional[str] = Field(None, max_length=100)
    descricao: Optional[str] = Field(None, min_length=1, max_length=500)
    marca: Optional[str] = Field(None, max_length=100)
    modelo: Optional[str] = Field(None, max_length=100)
    numero_serie: Optional[str] = Field(None, max_length=100)
    estado: Optional[str] = Field(None)
    valor_aquisicao: Optional[Decimal] = Field(None, ge=0)
    data_compra: Optional[date] = Field(None)
    nota_fiscal: Optional[str] = Field(None, max_length=100)
    vida_util_meses: Optional[int] = Field(None, ge=1)
    centro_custo_id: Optional[int] = Field(None)
    setor_id: Optional[int] = Field(None)
    local_id: Optional[int] = Field(None)
    responsavel_id: Optional[int] = Field(None)
    status: Optional[str] = Field(None)
    garantia_ate: Optional[date] = Field(None)
    fornecedor_id: Optional[int] = Field(None)
    observacoes: Optional[str] = Field(None, max_length=1000)
    tags: Optional[str] = Field(None, max_length=500)


class AtivoResponse(AtivoBase):
    """Schema for Ativo response"""
    id: int
    valor_contabil_atual: Optional[Decimal] = None
    valor_depreciado_acumulado: Optional[Decimal] = None
    percentual_depreciacao: Optional[float] = None
    etiqueta_gerada: bool = False
    codigo_qr: Optional[str] = None
    codigo_nfc: Optional[str] = None
    url_foto: Optional[str] = None
    ultima_auditoria: Optional[datetime] = None
    ultima_movimentacao: Optional[datetime] = None
    ativo: bool = True
    criado_em: datetime
    atualizado_em: Optional[datetime] = None
    criado_por: Optional[int] = None
    atualizado_por: Optional[int] = None

    class Config:
        from_attributes = True


class AtivoList(BaseModel):
    """Schema for paginated Ativo list"""
    items: List[AtivoResponse]
    total: int
    skip: int
    limit: int


class AtivoFilter(BaseModel):
    """Schema for Ativo filtering"""
    query: Optional[str] = None
    categoria: Optional[str] = None
    subcategoria: Optional[str] = None
    setor_id: Optional[int] = None
    local_id: Optional[int] = None
    responsavel_id: Optional[int] = None
    status: Optional[str] = None
    estado: Optional[str] = None
    centro_custo_id: Optional[int] = None
    fornecedor_id: Optional[int] = None
    valor_min: Optional[float] = None
    valor_max: Optional[float] = None
    data_compra_inicio: Optional[date] = None
    data_compra_fim: Optional[date] = None
    sem_auditoria_dias: Optional[int] = None


class AtivoImport(BaseModel):
    """Schema for bulk Ativo import"""
    codigo: str
    patrimonio: Optional[str] = None
    categoria: str
    subcategoria: Optional[str] = None
    descricao: str
    marca: Optional[str] = None
    modelo: Optional[str] = None
    numero_serie: Optional[str] = None
    estado: Optional[str] = "novo"
    valor_aquisicao: Optional[float] = None
    data_compra: Optional[str] = None
    nota_fiscal: Optional[str] = None
    vida_util_meses: Optional[int] = None
    centro_custo_codigo: Optional[str] = None
    setor_nome: Optional[str] = None
    fornecedor_nome: Optional[str] = None
    observacoes: Optional[str] = None
    tags: Optional[str] = None


class EtiquetaQR(BaseModel):
    """Schema for QR/NFC label generation"""
    ativo_id: int
    codigo_qr: str
    qr_data: Dict[str, Any]


class AtivoMetricas(BaseModel):
    """Schema for asset metrics"""
    total_ativos: int
    ativos_ativos: int
    ativos_alocados: int
    ativos_manutencao: int
    ativos_sem_auditoria: int
    valor_total_aquisicao: float
    valor_contabil_atual: float
    depreciacao_acumulada: float


class AtivoDistribuicao(BaseModel):
    """Schema for asset distribution"""
    categoria: str
    quantidade: int
    valor_total: Optional[float] = None


class SetorBase(BaseModel):
    """Base schema for Setor"""
    nome: str = Field(..., min_length=1, max_length=100)
    codigo: Optional[str] = Field(None, max_length=20)
    descricao: Optional[str] = Field(None, max_length=500)
    gestor_id: Optional[int] = None
    centro_custo_id: Optional[int] = None


class SetorCreate(SetorBase):
    """Schema for creating Setor"""
    pass


class SetorResponse(SetorBase):
    """Schema for Setor response"""
    id: int
    ativo: bool = True
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


class LocalBase(BaseModel):
    """Base schema for Local"""
    codigo: str = Field(..., min_length=1, max_length=50)
    tipo: str = Field(..., description="Tipo do local (empresa, unidade, andar, sala, posicao)")
    nome: str = Field(..., min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=500)
    local_pai_id: Optional[int] = Field(None, description="ID do local pai na hierarquia")
    endereco: Optional[str] = Field(None, max_length=500)
    capacidade_ativos: Optional[int] = Field(None, ge=0)
    setor_id: Optional[int] = None
    responsavel_local: Optional[str] = Field(None, max_length=200)


class LocalCreate(LocalBase):
    """Schema for creating Local"""
    pass


class LocalResponse(LocalBase):
    """Schema for Local response"""
    id: int
    endereco_completo: Optional[str] = None
    ativo: bool = True
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


class ResponsavelBase(BaseModel):
    """Base schema for Responsavel"""
    nome: str = Field(..., min_length=1, max_length=200)
    email: str = Field(..., max_length=200)
    telefone: Optional[str] = Field(None, max_length=20)
    cargo: Optional[str] = Field(None, max_length=100)
    matricula: Optional[str] = Field(None, max_length=50)
    setor_id: Optional[int] = None
    gestor_id: Optional[int] = None


class ResponsavelCreate(ResponsavelBase):
    """Schema for creating Responsavel"""
    pass


class ResponsavelResponse(ResponsavelBase):
    """Schema for Responsavel response"""
    id: int
    ativo: bool = True
    observacoes: Optional[str] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


class CentroCustoBase(BaseModel):
    """Base schema for CentroCusto"""
    codigo: str = Field(..., min_length=1, max_length=20)
    nome: str = Field(..., min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=500)
    orcamento_anual: Optional[Decimal] = Field(None, ge=0)
    responsavel_financeiro: Optional[str] = Field(None, max_length=200)


class CentroCustoCreate(CentroCustoBase):
    """Schema for creating CentroCusto"""
    pass


class CentroCustoResponse(CentroCustoBase):
    """Schema for CentroCusto response"""
    id: int
    ativo: bool = True
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


class FornecedorBase(BaseModel):
    """Base schema for Fornecedor"""
    nome: str = Field(..., min_length=1, max_length=200)
    razao_social: Optional[str] = Field(None, max_length=200)
    cnpj: Optional[str] = Field(None, max_length=18)
    cpf: Optional[str] = Field(None, max_length=14)
    email: Optional[str] = Field(None, max_length=200)
    telefone: Optional[str] = Field(None, max_length=20)
    endereco: Optional[str] = Field(None, max_length=500)
    categoria: Optional[str] = Field(None, max_length=100)
    site: Optional[str] = Field(None, max_length=200)


class FornecedorCreate(FornecedorBase):
    """Schema for creating Fornecedor"""
    pass


class FornecedorResponse(FornecedorBase):
    """Schema for Fornecedor response"""
    id: int
    ativo: bool = True
    observacoes: Optional[str] = None
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    class Config:
        from_attributes = True