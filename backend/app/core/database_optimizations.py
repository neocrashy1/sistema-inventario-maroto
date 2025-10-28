"""
Database Performance Optimizations
Implementa otimizações de performance para o banco de dados
"""

from sqlalchemy import Index, text
from sqlalchemy.orm import Session
from app.core.database import engine
import logging

logger = logging.getLogger(__name__)

# Detecta dialeto para evitar comandos incompatíveis
_def_dialect = (getattr(engine, 'dialect', None).name if getattr(engine, 'dialect', None) else '').lower()
_is_pg = _def_dialect == 'postgresql'


def create_performance_indexes():
    """
    Cria índices otimizados para melhorar performance das queries mais frequentes
    """
    
    # Índices compostos para queries frequentes
    indexes = [
        # Assets - queries por status e localização
        Index('idx_assets_status_location', 'assets.status', 'assets.location_id'),
        Index('idx_assets_type_status', 'assets.asset_type', 'assets.status'),
        Index('idx_assets_assigned_status', 'assets.assigned_to', 'assets.status'),
        Index('idx_assets_created_at', 'assets.created_at'),
        Index('idx_assets_updated_at', 'assets.updated_at'),
        
        # Users - autenticação e busca
        Index('idx_users_email_active', 'users.email', 'users.is_active'),
        Index('idx_users_role_active', 'users.role', 'users.is_active'),
        
        # Locations - hierarquia e busca
        Index('idx_locations_parent_active', 'locations.parent_id', 'locations.is_active'),
        Index('idx_locations_level_active', 'locations.level', 'locations.is_active'),
        
        # Alerts - dashboard e notificações
        Index('idx_alerts_severity_status', 'alerts.severity', 'alerts.status'),
        Index('idx_alerts_asset_created', 'alerts.asset_id', 'alerts.created_at'),
        Index('idx_alerts_created_at', 'alerts.created_at'),
        
        # Tickets - gestão de chamados
        Index('idx_tickets_status_priority', 'tickets.status', 'tickets.priority'),
        Index('idx_tickets_assigned_status', 'tickets.assigned_to', 'tickets.status'),
        Index('idx_tickets_asset_status', 'tickets.asset_id', 'tickets.status'),
        
        # Movements - auditoria e rastreamento
        Index('idx_movements_asset_date', 'movements.asset_id', 'movements.movement_date'),
        Index('idx_movements_type_date', 'movements.movement_type', 'movements.movement_date'),
    ]
    
    try:
        with engine.connect() as conn:
            for index in indexes:
                try:
                    index.create(conn, checkfirst=True)
                    logger.info(f"Índice criado: {index.name}")
                except Exception as e:
                    logger.warning(f"Erro ao criar índice {index.name}: {e}")
                    
        logger.info("Otimizações de índices aplicadas com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao aplicar otimizações de índices: {e}")


def optimize_database_settings():
    """
    Aplica configurações de otimização específicas do PostgreSQL
    """
    
    # Evita erro em dialetos não-PostgreSQL (ex.: SQLite)
    if not _is_pg:
        logger.info("Pulando otimizações de configurações (SET): dialeto não-PostgreSQL detectado")
        return
    
    optimizations = [
        # Configurações de memória
        "SET shared_buffers = '256MB'",
        "SET effective_cache_size = '1GB'",
        "SET work_mem = '4MB'",
        "SET maintenance_work_mem = '64MB'",
        
        # Configurações de checkpoint
        "SET checkpoint_completion_target = 0.9",
        "SET wal_buffers = '16MB'",
        
        # Configurações de query planner
        "SET random_page_cost = 1.1",
        "SET effective_io_concurrency = 200",
        
        # Configurações de logging (apenas para desenvolvimento)
        "SET log_min_duration_statement = 1000",  # Log queries > 1s
        "SET log_statement = 'mod'",  # Log modificações
    ]
    
    try:
        with engine.connect() as conn:
            for optimization in optimizations:
                try:
                    conn.execute(text(optimization))
                    logger.info(f"Configuração aplicada: {optimization}")
                except Exception as e:
                    logger.warning(f"Erro ao aplicar configuração: {e}")
                    
        logger.info("Configurações de otimização aplicadas")
        
    except Exception as e:
        logger.error(f"Erro ao aplicar configurações de otimização: {e}")


def analyze_table_statistics():
    """
    Atualiza estatísticas das tabelas para otimizar o query planner
    """
    
    tables = [
        'assets', 'users', 'locations', 'alerts', 
        'tickets', 'movements', 'asset_audits'
    ]
    
    try:
        with engine.connect() as conn:
            for table in tables:
                try:
                    conn.execute(text(f"ANALYZE {table}"))
                    logger.info(f"Estatísticas atualizadas para tabela: {table}")
                except Exception as e:
                    logger.warning(f"Erro ao analisar tabela {table}: {e}")
                    
        logger.info("Análise de estatísticas concluída")
        
    except Exception as e:
        logger.error(f"Erro ao analisar estatísticas: {e}")


def setup_connection_pooling():
    """
    Configurações otimizadas para pool de conexões
    """
    
    # Configurações já aplicadas no engine principal
    # Documentação das configurações utilizadas
    pool_config = {
        'pool_size': 10,           # Conexões ativas no pool
        'max_overflow': 20,        # Conexões extras quando necessário
        'pool_timeout': 30,        # Timeout para obter conexão
        'pool_recycle': 3600,      # Reciclar conexões a cada hora
        'pool_pre_ping': True,     # Verificar conexões antes de usar
    }
    
    logger.info(f"Pool de conexões configurado: {pool_config}")
    return pool_config


def get_query_performance_tips():
    """
    Retorna dicas de performance para queries
    """
    
    tips = {
        'eager_loading': 'Use joinedload() para relacionamentos 1:1 e selectinload() para 1:N',
        'pagination': 'Sempre use LIMIT/OFFSET para grandes datasets',
        'filtering': 'Aplique filtros antes de joins quando possível',
        'indexing': 'Crie índices compostos para queries com múltiplas condições WHERE',
        'caching': 'Use cache para queries frequentes e dados estáticos',
        'batch_operations': 'Use bulk_insert_mappings() para inserções em lote',
        'select_specific': 'Selecione apenas colunas necessárias com query.options(load_only())',
        'avoid_n_plus_1': 'Use eager loading para evitar problema N+1',
    }
    
    return tips


def run_all_optimizations():
    """
    Executa todas as otimizações de banco de dados
    """
    
    logger.info("Iniciando otimizações de banco de dados...")
    
    # Quando não PostgreSQL, aplicar apenas otimizações seguras
    if not _is_pg:
        try:
            analyze_table_statistics()
        except Exception as e:
            logger.warning(f"Falha ao analisar estatísticas em dialeto {_def_dialect}: {e}")
        setup_connection_pooling()
        logger.info("Otimizações básicas de banco de dados concluídas!")
        return
    
    # Criar índices de performance
    create_performance_indexes()
    
    # Aplicar configurações de otimização
    optimize_database_settings()
    
    # Atualizar estatísticas
    analyze_table_statistics()
    
    # Configurar pool de conexões
    setup_connection_pooling()
    
    logger.info("Otimizações de banco de dados concluídas!")


if __name__ == "__main__":
    # Executar otimizações se chamado diretamente
    run_all_optimizations()