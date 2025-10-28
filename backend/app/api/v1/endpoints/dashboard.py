from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from functools import lru_cache
import random
import time

from app.core.database import get_async_session
from app.core.security import get_current_user_id, security

router = APIRouter()

# Cache para dados estáticos que não mudam frequentemente
@lru_cache(maxsize=128)
def get_cached_static_data():
    """Cache para dados estáticos do sistema"""
    return {
        "system_info": {
            "version": "1.0.0",
            "build": "2024.01.15",
            "environment": "production"
        },
        "default_thresholds": {
            "cpu_warning": 80,
            "cpu_critical": 95,
            "memory_warning": 85,
            "memory_critical": 95,
            "disk_warning": 80,
            "disk_critical": 90
        }
    }

@lru_cache(maxsize=64)
def get_cached_dashboard_base_stats(cache_key: str):
    """Cache para estatísticas base do dashboard (atualizado a cada 5 minutos)"""
    # Simulando estatísticas realistas
    total_assets = 150
    active_assets = 142
    total_machines = 85
    online_machines = 78
    offline_machines = 7
    total_tickets = 324
    open_tickets = 45
    closed_tickets = 279
    recent_tickets = 67
    total_alerts = 89
    active_alerts = 12
    critical_alerts = 3
    recent_alerts = 23
    total_users = 25
    active_users = 23
    
    # Cálculo de percentuais
    machine_uptime = (online_machines / total_machines * 100) if total_machines > 0 else 0
    asset_utilization = (active_assets / total_assets * 100) if total_assets > 0 else 0
    ticket_resolution_rate = (closed_tickets / total_tickets * 100) if total_tickets > 0 else 0
    
    return {
        "overview": {
            "total_assets": total_assets,
            "total_machines": total_machines,
            "total_tickets": total_tickets,
            "total_alerts": total_alerts,
            "total_users": total_users
        },
        "assets": {
            "total": total_assets,
            "active": active_assets,
            "utilization_rate": round(asset_utilization, 2)
        },
        "machines": {
            "total": total_machines,
            "online": online_machines,
            "offline": offline_machines,
            "uptime_percentage": round(machine_uptime, 2)
        },
        "tickets": {
            "total": total_tickets,
            "open": open_tickets,
            "closed": closed_tickets,
            "recent_30_days": recent_tickets,
            "resolution_rate": round(ticket_resolution_rate, 2)
        },
        "alerts": {
            "total": total_alerts,
            "active": active_alerts,
            "critical": critical_alerts,
            "recent_7_days": recent_alerts
        },
        "users": {
            "total": total_users,
            "active": active_users
        }
    }

def get_cache_key_for_stats():
    """Gera chave de cache que muda a cada 5 minutos"""
    current_time = int(time.time())
    # Cache válido por 5 minutos (300 segundos)
    cache_interval = current_time // 300
    return f"dashboard_stats_{cache_interval}"

@router.get("/stats", response_model=Dict[str, Any])
async def get_dashboard_stats(
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds)),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get comprehensive dashboard statistics and KPIs
    """
    try:
        now = datetime.utcnow()
        
        # Usar cache para dados base (atualizado a cada 5 minutos)
        cache_key = get_cache_key_for_stats()
        cached_stats = get_cached_dashboard_base_stats(cache_key)
        
        # Adicionar timestamp atual
        cached_stats["last_updated"] = now.isoformat()
        
        # Adicionar dados estáticos do sistema
        static_data = get_cached_static_data()
        cached_stats["system"] = static_data
        
        return cached_stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar estatísticas do dashboard: {str(e)}"
        )


@router.get("/metrics", response_model=Dict[str, Any])
async def get_dashboard_metrics(
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds)),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get detailed metrics for dashboard charts and graphs
    """
    try:
        now = datetime.utcnow()
        
        # Métricas de tickets por dia (últimos 30 dias) - dados mock
        tickets_by_day = []
        for i in range(30):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            count = random.randint(0, 8)  # Simulando variação de tickets por dia
            
            tickets_by_day.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "count": count
            })
        
        # Distribuição de tickets por prioridade - dados mock
        priority_distribution = [
            {"priority": "low", "count": 45},
            {"priority": "medium", "count": 78},
            {"priority": "high", "count": 32},
            {"priority": "critical", "count": 12}
        ]
        
        # Distribuição de alertas por severidade - dados mock
        severity_distribution = [
            {"severity": "info", "count": 25},
            {"severity": "warning", "count": 18},
            {"severity": "error", "count": 8},
            {"severity": "critical", "count": 3}
        ]
        
        # Status das máquinas - dados mock
        machine_status_distribution = [
            {"status": "online", "count": 78},
            {"status": "offline", "count": 7},
            {"status": "maintenance", "count": 3},
            {"status": "error", "count": 2}
        ]
        
        return {
            "tickets_timeline": list(reversed(tickets_by_day)),
            "ticket_priorities": priority_distribution,
            "alert_severities": severity_distribution,
            "machine_statuses": machine_status_distribution,
            "generated_at": now.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar métricas do dashboard: {str(e)}"
        )


@router.get("/recent-activity", response_model=Dict[str, List[Dict[str, Any]]])
async def get_recent_activity(
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds)),
    db: AsyncSession = Depends(get_async_session),
    limit: int = 10
):
    """
    Get recent activity across the system
    """
    try:
        now = datetime.utcnow()
        
        # Tickets recentes - dados mock
        tickets_data = [
            {
                "id": f"TK-{1000 + i}",
                "title": f"Problema no servidor {i+1}",
                "priority": ["low", "medium", "high", "critical"][i % 4],
                "status": ["open", "in_progress", "closed"][i % 3],
                "created_at": (now - timedelta(hours=i*2)).isoformat(),
                "type": "ticket"
            }
            for i in range(min(limit, 8))
        ]
        
        # Alertas recentes - dados mock
        alerts_data = [
            {
                "id": f"AL-{2000 + i}",
                "title": f"Alerta de sistema {i+1}",
                "severity": ["info", "warning", "error", "critical"][i % 4],
                "status": ["active", "resolved"][i % 2],
                "created_at": (now - timedelta(hours=i*3)).isoformat(),
                "type": "alert"
            }
            for i in range(min(limit, 6))
        ]
        
        return {
            "recent_tickets": tickets_data,
            "recent_alerts": alerts_data
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar atividade recente: {str(e)}"
        )


@router.get("/health-check", response_model=Dict[str, Any])
async def dashboard_health_check(
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds)),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Perform system health check for dashboard
    """
    try:
        # Verificações básicas de saúde do sistema
        db_status = "healthy"
        try:
            await db.execute("SELECT 1")
        except Exception:
            db_status = "unhealthy"
        
        # Dados mock para demonstração
        critical_alerts = 3
        offline_machines = 7
        overdue_tickets = 5
        
        # Determinação do status geral
        overall_status = "healthy"
        issues = []
        
        if db_status != "healthy":
            overall_status = "critical"
            issues.append("Database connection issues")
        
        if critical_alerts > 0:
            overall_status = "warning" if overall_status == "healthy" else overall_status
            issues.append(f"{critical_alerts} critical alerts active")
        
        if offline_machines > 0:
            overall_status = "warning" if overall_status == "healthy" else overall_status
            issues.append(f"{offline_machines} machines offline")
        
        if overdue_tickets > 0:
            overall_status = "warning" if overall_status == "healthy" else overall_status
            issues.append(f"{overdue_tickets} overdue tickets")
        
        return {
            "overall_status": overall_status,
            "database_status": db_status,
            "critical_alerts": critical_alerts,
            "offline_machines": offline_machines,
            "overdue_tickets": overdue_tickets,
            "issues": issues,
            "checked_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao verificar saúde do sistema: {str(e)}"
        )


@router.get("/alerts", response_model=Dict[str, Any])
async def get_dashboard_alerts(
    current_user: str = Depends(lambda creds=Depends(security): get_current_user_id(creds)),
    db: AsyncSession = Depends(get_async_session),
    status_filter: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 20
):
    """
    Get alerts list for dashboard widgets
    """
    try:
        now = datetime.utcnow()
        # Dados mock de alertas (substituir por consulta ao banco futuramente)
        all_alerts = [
            {
                "id": f"AL-{2000 + i}",
                "title": f"Alerta de sistema {i+1}",
                "severity": ["info", "warning", "error", "critical"][i % 4],
                "status": ["active", "resolved"][i % 2],
                "created_at": (now - timedelta(hours=i * 2)).isoformat(),
                "source": ["machine", "agent", "service"][i % 3],
                "machine_id": f"MCH-{100 + i}",
                "description": "Evento detectado pelo monitoramento",
            }
            for i in range(30)
        ]

        # Filtros opcionais
        if status_filter:
            all_alerts = [a for a in all_alerts if a["status"] == status_filter]
        if severity:
            all_alerts = [a for a in all_alerts if a["severity"] == severity]

        alerts = all_alerts[: max(1, min(limit, 50))]

        # Agregados para cards/resumos
        severity_counts = {
            "info": sum(1 for a in all_alerts if a["severity"] == "info"),
            "warning": sum(1 for a in all_alerts if a["severity"] == "warning"),
            "error": sum(1 for a in all_alerts if a["severity"] == "error"),
            "critical": sum(1 for a in all_alerts if a["severity"] == "critical"),
        }
        status_counts = {
            "active": sum(1 for a in all_alerts if a["status"] == "active"),
            "resolved": sum(1 for a in all_alerts if a["status"] == "resolved"),
        }

        return {
            "items": alerts,
            "count": len(alerts),
            "total": len(all_alerts),
            "severity_counts": severity_counts,
            "status_counts": status_counts,
            "generated_at": now.isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar alertas do dashboard: {str(e)}",
        )