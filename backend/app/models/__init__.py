# Database models package for Levitiis Inventory System

# Import models in the correct order to avoid circular dependencies
from .user import User, UserRole, UserStatus
from .centro_custo import CentroCusto
from .setor import Setor
from .location import Local, Location
from .responsavel import Responsavel
from .fornecedor import Fornecedor
from .asset import Ativo, EstadoAtivo, StatusAtivo, CategoriaAtivo
from .movimentacao import Movimentacao, TipoMovimentacao, StatusMovimentacao
from .auditoria import Auditoria, AuditoriaItem, TipoAuditoria, StatusAuditoria, ResultadoItem
from .manutencao import Manutencao, TipoManutencao, StatusManutencao, PrioridadeManutencao

# Legacy models (keeping for backward compatibility)
from .machine import Machine, MachineStatus, MachineType
from .movement import Movement, MovementType, MovementStatus
from .alert import Alert, AlertType, AlertStatus
from .ticket import Ticket, TicketStatus, TicketPriority, TicketCategory

__all__ = [
    # Core user management
    "User", "UserRole", "UserStatus",
    
    # Levitiis Inventory System models
    "CentroCusto",
    "Setor", 
    "Local", "Location",
    "Responsavel",
    "Fornecedor",
    "Ativo", "EstadoAtivo", "StatusAtivo", "CategoriaAtivo",
    "Movimentacao", "TipoMovimentacao", "StatusMovimentacao",
    "Auditoria", "AuditoriaItem", "TipoAuditoria", "StatusAuditoria", "ResultadoItem",
    "Manutencao", "TipoManutencao", "StatusManutencao", "PrioridadeManutencao",
    
    # Legacy models (backward compatibility)
    "Machine", "MachineStatus", "MachineType",
    "Movement", "MovementType", "MovementStatus",
    "Alert", "AlertType", "AlertStatus",
    "Ticket", "TicketStatus", "TicketPriority", "TicketCategory"
]