"""
Local model for Levitiis inventory system
Enhanced location model following the organizational structure:
Empresa > Unidade/Filial > Andar > Sala/Área > Posição
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Local(Base):
    """
    Local (Location) model
    Represents physical locations within the organizational structure
    """
    __tablename__ = "locais"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, nullable=False, index=True)
    
    # Hierarchical structure: Empresa > Unidade > Andar > Sala > Posição
    empresa = Column(String(100), nullable=False, default="Levitiis")
    unidade = Column(String(100), nullable=False)  # Filial/Unidade
    andar = Column(String(20), nullable=True)      # Andar/Piso
    sala = Column(String(50), nullable=True)       # Sala/Área
    posicao = Column(String(50), nullable=True)    # Posição específica
    
    # Additional details
    descricao = Column(Text)
    capacidade_ativos = Column(Integer, nullable=True)
    setor_id = Column(Integer, ForeignKey("setores.id"), nullable=True)
    responsavel_local = Column(String(100), nullable=True)
    ativo = Column(Integer, default=1)  # 1=ativo, 0=inativo
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    setor = relationship("Setor", back_populates="locais")
    ativos = relationship("Ativo", back_populates="local")
    movimentacoes_origem = relationship("Movimentacao", foreign_keys="Movimentacao.de_local_id", back_populates="local_origem")
    movimentacoes_destino = relationship("Movimentacao", foreign_keys="Movimentacao.para_local_id", back_populates="local_destino")

    @property
    def endereco_completo(self):
        """Returns the complete address string"""
        parts = [self.empresa, self.unidade]
        if self.andar:
            parts.append(f"Andar {self.andar}")
        if self.sala:
            parts.append(self.sala)
        if self.posicao:
            parts.append(self.posicao)
        return " - ".join(parts)

    def __repr__(self):
        return f"<Local(id={self.id}, codigo='{self.codigo}', endereco='{self.endereco_completo}')>"


# Additional English-compatible Location model to satisfy relationships expecting "Location"
class Location(Base):
    """Location model (English) used by relationships such as Machine.location
    This co-exists with the existing Local model (Portuguese) and maps to the
    'locations' table expected by various relationships.
    """
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, index=True)
    description = Column(Text, nullable=True)

    # Optional self-referential hierarchy
    parent_id = Column(Integer, ForeignKey("locations.id"), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    parent = relationship("Location", remote_side=[id], back_populates="children")
    children = relationship("Location", back_populates="parent")

    # Back-populate with machines (Machine.location)
    machines = relationship("Machine", back_populates="location")

    # Movements (English)
    movements_from = relationship("Movement", foreign_keys="Movement.from_location_id", back_populates="from_location")
    movements_to = relationship("Movement", foreign_keys="Movement.to_location_id", back_populates="to_location")

    # Tickets and Alerts (English)
    tickets = relationship("Ticket", back_populates="location")
    alerts = relationship("Alert", back_populates="location")

    # Assets (English)
    assets = relationship("Asset", back_populates="location")

    def __repr__(self):
        return f"<Location(id={self.id}, name='{self.name}', code='{self.code}')>"