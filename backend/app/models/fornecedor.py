"""
Fornecedor model for Levitiis inventory system
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Fornecedor(Base):
    """
    Fornecedor (Supplier) model
    Represents suppliers and vendors for asset procurement
    """
    __tablename__ = "fornecedores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False, index=True)
    razao_social = Column(String(200), nullable=True)
    cnpj = Column(String(18), nullable=True, unique=True, index=True)  # Format: XX.XXX.XXX/XXXX-XX
    cpf = Column(String(14), nullable=True, unique=True, index=True)   # Format: XXX.XXX.XXX-XX
    
    # Contact information
    contato_nome = Column(String(100), nullable=True)
    contato_email = Column(String(150), nullable=True)
    contato_telefone = Column(String(20), nullable=True)
    contato_celular = Column(String(20), nullable=True)
    
    # Address
    endereco = Column(String(300), nullable=True)
    cidade = Column(String(100), nullable=True)
    estado = Column(String(2), nullable=True)  # UF
    cep = Column(String(9), nullable=True)     # Format: XXXXX-XXX
    
    # Business information
    categoria = Column(String(100), nullable=True)  # Hardware, Software, Serviços, etc.
    site = Column(String(200), nullable=True)
    observacoes = Column(Text)
    
    # Status
    ativo = Column(Integer, default=1)  # 1=ativo, 0=inativo
    
    # Timestamps
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    ativos = relationship("Ativo", back_populates="fornecedor")

    def __repr__(self):
        return f"<Fornecedor(id={self.id}, nome='{self.nome}', cnpj='{self.cnpj}')>"