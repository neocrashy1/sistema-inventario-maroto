"""
Ativo model for Levitiis inventory system
Complete asset management model following Brazilian standards
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
from decimal import Decimal
from datetime import datetime, timedelta

from app.core.database import Base


class EstadoAtivo(str, Enum):
    """Estado do ativo"""
    NOVO = "novo"
    USO = "uso"
    OBSOLETO = "obsoleto"
    SUCATA = "sucata"


class StatusAtivo(str, Enum):
    """Status operacional do ativo"""
    ATIVO = "ativo"
    ALOCADO = "alocado"
    MANUTENCAO = "em_manutencao"
    BAIXADO = "baixado"


class CategoriaAtivo(str, Enum):
    """Categorias principais de ativos"""
    HARDWARE = "hardware"
    SOFTWARE = "software"
    MOBILIARIO = "mobiliario"
    VEICULO = "veiculo"
    EQUIPAMENTO = "equipamento"
    OUTRO = "outro"


class Ativo(Base):
    """
    Ativo (Asset) model
    Complete asset management following Levitiis specifications
    """
    __tablename__ = "ativos"

    id = Column(Integer, primary_key=True, index=True)
    
    # Identificação principal
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    patrimonio = Column(String(50), unique=True, nullable=True, index=True)
    descricao = Column(String(500), nullable=False)
    
    # Classificação
    categoria = Column(String(50), nullable=False, default=CategoriaAtivo.HARDWARE)
    subcategoria = Column(String(100), nullable=True)
    
    # Informações técnicas
    marca = Column(String(100), nullable=True)
    modelo = Column(String(100), nullable=True)
    ns_serie = Column(String(100), nullable=True, unique=True, index=True)
    
    # Estado e status
    estado = Column(String(20), nullable=False, default=EstadoAtivo.NOVO)
    status = Column(String(20), nullable=False, default=StatusAtivo.ATIVO)
    
    # Informações financeiras
    valor_aquisicao = Column(Numeric(15, 2), nullable=True)
    data_compra = Column(DateTime, nullable=True)
    nota_fiscal = Column(String(100), nullable=True)
    vida_util_meses = Column(Integer, nullable=True, default=60)  # 5 anos padrão
    deprec_linear = Column(Numeric(15, 2), nullable=True)  # Depreciação mensal
    
    # Localização e responsabilidade
    centro_custo_id = Column(Integer, ForeignKey("centros_custo.id"), nullable=True)
    setor_id = Column(Integer, ForeignKey("setores.id"), nullable=True)
    local_id = Column(Integer, ForeignKey("locais.id"), nullable=True)
    responsavel_id = Column(Integer, ForeignKey("responsaveis.id"), nullable=True)
    
    # Garantia e fornecedor
    garantia_ate = Column(DateTime, nullable=True)
    fornecedor_id = Column(Integer, ForeignKey("fornecedores.id"), nullable=True)
    
    # Metadados e observações
    tags = Column(JSON, nullable=True)  # Array de tags para busca
    observacoes = Column(Text, nullable=True)
    fotos = Column(JSON, nullable=True)  # Array de URLs das fotos
    
    # QR/NFC
    qr_code = Column(String(200), nullable=True, unique=True)
    nfc_tag = Column(String(100), nullable=True, unique=True)
    etiqueta_impressa = Column(Integer, default=0)  # 0=não, 1=sim
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
    criado_por = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    centro_custo = relationship("CentroCusto", back_populates="ativos")
    setor = relationship("Setor", back_populates="ativos")
    local = relationship("Local", back_populates="ativos")
    responsavel = relationship("Responsavel", back_populates="ativos")
    fornecedor = relationship("Fornecedor", back_populates="ativos")
    criador = relationship("User", foreign_keys=[criado_por])
    
    # Asset lifecycle relationships
    movimentacoes = relationship("Movimentacao", back_populates="ativo")
    auditorias_itens = relationship("AuditoriaItem", back_populates="ativo")
    manutencoes = relationship("Manutencao", back_populates="ativo")

    @property
    def valor_atual(self):
        """Calcula o valor atual considerando depreciação linear"""
        if not self.valor_aquisicao or not self.data_compra or not self.vida_util_meses:
            return self.valor_aquisicao or Decimal('0.00')
        
        meses_uso = (datetime.now() - self.data_compra).days // 30
        if meses_uso >= self.vida_util_meses:
            return Decimal('0.00')
        
        deprec_total = (self.valor_aquisicao / self.vida_util_meses) * meses_uso
        return max(Decimal('0.00'), self.valor_aquisicao - deprec_total)

    @property
    def deprec_acumulada(self):
        """Calcula a depreciação acumulada"""
        if not self.valor_aquisicao:
            return Decimal('0.00')
        return self.valor_aquisicao - self.valor_atual

    @property
    def garantia_ativa(self):
        """Verifica se a garantia ainda está ativa"""
        if not self.garantia_ate:
            return False
        return datetime.now() < self.garantia_ate

    def __repr__(self):
        return f"<Ativo(id={self.id}, codigo='{self.codigo}', descricao='{self.descricao[:50]}')>"


class Asset(Base):
    """
    Asset model (English) to satisfy relationships expecting 'assets' table
    Coexists with Ativo (Portuguese) which maps to 'ativos'
    """
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)

    # Identification
    asset_tag = Column(String(100), unique=True, nullable=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Status and metadata
    status = Column(String(20), default="active", nullable=False, index=True)
    category = Column(String(50), nullable=True)
    subcategory = Column(String(100), nullable=True)

    # Location
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True, index=True)

    # Additional data
    tags = Column(JSON, nullable=True)

    # Audit fields
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    movements = relationship("Movement", back_populates="asset")
    tickets = relationship("Ticket", back_populates="asset")
    alerts = relationship("Alert", back_populates="asset")
    location = relationship("Location", back_populates="assets")
    creator = relationship("User", foreign_keys=[created_by])
    audit_logs = relationship("AssetAudit", back_populates="asset")

    def __repr__(self):
        return f"<Asset(id={self.id}, name='{self.name}', status='{self.status}')>"