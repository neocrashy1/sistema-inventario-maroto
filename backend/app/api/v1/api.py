"""
API v1 router
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, machines, tickets, alerts, assets, users, dashboard, websocket,
    ativos, movimentacoes, auditorias, manutencao
)
from app.api import auth_advanced, monitoring, machine_monitoring

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(auth_advanced.router, prefix="/auth", tags=["authentication-advanced"])
api_router.include_router(machines.router, prefix="/machines", tags=["machines"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(websocket.router, tags=["websocket"])
api_router.include_router(monitoring.router, tags=["monitoring"])
api_router.include_router(machine_monitoring.router, tags=["machine-monitoring"])

# Sistema de Inventário - Novas rotas
api_router.include_router(ativos.router, prefix="/ativos", tags=["ativos"])
api_router.include_router(movimentacoes.router, prefix="/movimentacoes", tags=["movimentacoes"])
api_router.include_router(auditorias.router, prefix="/auditorias", tags=["auditorias"])
api_router.include_router(manutencao.router, prefix="/manutencao", tags=["manutencao"])