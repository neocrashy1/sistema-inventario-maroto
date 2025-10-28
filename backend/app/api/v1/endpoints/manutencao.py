"""
API endpoints for Manutencao (Maintenance) management
Handles CRUD operations, SLA tracking, evaluations and reports
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models import Manutencao, Ativo, User, Fornecedor
from app.schemas.manutencao import (
    ManutencaoCreate, ManutencaoUpdate, ManutencaoResponse, ManutencaoList,
    ManutencaoFilter, ManutencaoMetricas, ManutencaoDistribuicao,
    HistoricoManutencao, AvaliacaoManutencao, RelatorioManutencao, AlertaSLA
)

router = APIRouter()


@router.post("/", response_model=ManutencaoResponse)
async def criar_manutencao(
    manutencao: ManutencaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar nova solicitação de manutenção"""
    
    # Verificar se o ativo existe
    ativo = db.query(Ativo).filter(Ativo.id == manutencao.ativo_id).first()
    if not ativo:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    
    # Verificar se o usuário atribuído existe (se informado)
    if manutencao.atribuido_para:
        user = db.query(User).filter(User.id == manutencao.atribuido_para).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário para atribuição não encontrado")
    
    # Verificar se o fornecedor existe (se informado)
    if manutencao.fornecedor_externo_id:
        fornecedor = db.query(Fornecedor).filter(Fornecedor.id == manutencao.fornecedor_externo_id).first()
        if not fornecedor:
            raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    
    # Gerar número do ticket
    ultimo_numero = db.query(func.max(Manutencao.id)).scalar() or 0
    numero_ticket = f"MNT{datetime.now().year}{(ultimo_numero + 1):06d}"
    
    # Calcular SLA baseado na categoria do ativo e tipo de manutenção
    sla_horas = calcular_sla(ativo.categoria, manutencao.tipo, manutencao.prioridade)
    
    # Criar registro de manutenção
    db_manutencao = Manutencao(
        **manutencao.dict(),
        numero_ticket=numero_ticket,
        sla_horas=sla_horas,
        data_vencimento_sla=datetime.now() + timedelta(hours=sla_horas) if sla_horas else None,
        criado_por=current_user.id,
        criado_em=datetime.now()
    )
    
    db.add(db_manutencao)
    db.commit()
    db.refresh(db_manutencao)
    
    # Enviar notificação (implementar webhook/email)
    # await enviar_notificacao_nova_manutencao(db_manutencao)
    
    return db_manutencao


@router.get("/", response_model=ManutencaoList)
async def listar_manutencoes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    filtros: ManutencaoFilter = Depends(),
    ordenar_por: str = Query("criado_em", description="Campo para ordenação"),
    ordem: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar manutenções com filtros avançados"""
    
    query = db.query(Manutencao)
    
    # Aplicar filtros
    if filtros.ativo_id:
        query = query.filter(Manutencao.ativo_id == filtros.ativo_id)
    
    if filtros.tipo:
        query = query.filter(Manutencao.tipo == filtros.tipo)
    
    if filtros.status:
        query = query.filter(Manutencao.status == filtros.status)
    
    if filtros.prioridade:
        query = query.filter(Manutencao.prioridade == filtros.prioridade)
    
    if filtros.categoria:
        query = query.filter(Manutencao.categoria == filtros.categoria)
    
    if filtros.atribuido_para:
        query = query.filter(Manutencao.atribuido_para == filtros.atribuido_para)
    
    if filtros.fornecedor_externo_id:
        query = query.filter(Manutencao.fornecedor_externo_id == filtros.fornecedor_externo_id)
    
    if filtros.data_inicio:
        query = query.filter(Manutencao.criado_em >= filtros.data_inicio)
    
    if filtros.data_fim:
        query = query.filter(Manutencao.criado_em <= filtros.data_fim)
    
    if filtros.sla_vencido is not None:
        if filtros.sla_vencido:
            query = query.filter(
                and_(
                    Manutencao.data_vencimento_sla.isnot(None),
                    Manutencao.data_vencimento_sla < datetime.now(),
                    Manutencao.status.in_(["aberta", "em_andamento"])
                )
            )
        else:
            query = query.filter(
                or_(
                    Manutencao.data_vencimento_sla.is_(None),
                    Manutencao.data_vencimento_sla >= datetime.now(),
                    Manutencao.status.in_(["finalizada", "cancelada"])
                )
            )
    
    if filtros.texto:
        texto_busca = f"%{filtros.texto}%"
        query = query.filter(
            or_(
                Manutencao.titulo.ilike(texto_busca),
                Manutencao.descricao.ilike(texto_busca),
                Manutencao.numero_ticket.ilike(texto_busca)
            )
        )
    
    # Aplicar ordenação
    if hasattr(Manutencao, ordenar_por):
        if ordem == "desc":
            query = query.order_by(desc(getattr(Manutencao, ordenar_por)))
        else:
            query = query.order_by(asc(getattr(Manutencao, ordenar_por)))
    
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    return ManutencaoList(items=items, total=total, skip=skip, limit=limit)


@router.get("/{manutencao_id}", response_model=ManutencaoResponse)
async def obter_manutencao(
    manutencao_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter manutenção por ID"""
    
    manutencao = db.query(Manutencao).filter(Manutencao.id == manutencao_id).first()
    if not manutencao:
        raise HTTPException(status_code=404, detail="Manutenção não encontrada")
    
    return manutencao


@router.put("/{manutencao_id}", response_model=ManutencaoResponse)
async def atualizar_manutencao(
    manutencao_id: int,
    manutencao_update: ManutencaoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar manutenção"""
    
    manutencao = db.query(Manutencao).filter(Manutencao.id == manutencao_id).first()
    if not manutencao:
        raise HTTPException(status_code=404, detail="Manutenção não encontrada")
    
    # Verificar permissões (implementar RBAC)
    
    # Atualizar campos
    update_data = manutencao_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(manutencao, field, value)
    
    manutencao.atualizado_em = datetime.now()
    
    # Se status mudou para finalizada, registrar data de fim
    if manutencao_update.status == "finalizada" and manutencao.data_fim_real is None:
        manutencao.data_fim_real = datetime.now()
        manutencao.finalizado_por = current_user.id
    
    # Se status mudou para em_andamento, registrar data de início
    if manutencao_update.status == "em_andamento" and manutencao.data_inicio_real is None:
        manutencao.data_inicio_real = datetime.now()
    
    db.commit()
    db.refresh(manutencao)
    
    return manutencao


@router.delete("/{manutencao_id}")
async def cancelar_manutencao(
    manutencao_id: int,
    motivo: str = Query(..., description="Motivo do cancelamento"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancelar manutenção"""
    
    manutencao = db.query(Manutencao).filter(Manutencao.id == manutencao_id).first()
    if not manutencao:
        raise HTTPException(status_code=404, detail="Manutenção não encontrada")
    
    if manutencao.status in ["finalizada", "cancelada"]:
        raise HTTPException(status_code=400, detail="Manutenção já finalizada ou cancelada")
    
    manutencao.status = "cancelada"
    manutencao.observacoes_resolucao = f"Cancelada: {motivo}"
    manutencao.finalizado_por = current_user.id
    manutencao.data_fim_real = datetime.now()
    manutencao.atualizado_em = datetime.now()
    
    db.commit()
    
    return {"message": "Manutenção cancelada com sucesso"}


@router.post("/{manutencao_id}/avaliar")
async def avaliar_manutencao(
    manutencao_id: int,
    avaliacao: AvaliacaoManutencao,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Avaliar qualidade da manutenção"""
    
    manutencao = db.query(Manutencao).filter(Manutencao.id == manutencao_id).first()
    if not manutencao:
        raise HTTPException(status_code=404, detail="Manutenção não encontrada")
    
    if manutencao.status != "finalizada":
        raise HTTPException(status_code=400, detail="Só é possível avaliar manutenções finalizadas")
    
    manutencao.avaliacao_qualidade = avaliacao.avaliacao_qualidade
    manutencao.comentarios_avaliacao = avaliacao.comentarios
    manutencao.atualizado_em = datetime.now()
    
    db.commit()
    
    return {"message": "Avaliação registrada com sucesso"}


@router.get("/ativo/{ativo_id}/historico", response_model=HistoricoManutencao)
async def obter_historico_manutencao(
    ativo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter histórico de manutenções de um ativo"""
    
    ativo = db.query(Ativo).filter(Ativo.id == ativo_id).first()
    if not ativo:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    
    manutencoes = db.query(Manutencao).filter(
        Manutencao.ativo_id == ativo_id
    ).order_by(desc(Manutencao.criado_em)).all()
    
    # Calcular métricas
    total_manutencoes = len(manutencoes)
    custo_total = sum(m.custo_real or 0 for m in manutencoes)
    tempo_inatividade_total = sum(m.tempo_inatividade_horas or 0 for m in manutencoes)
    ultima_manutencao = manutencoes[0].criado_em if manutencoes else None
    
    return HistoricoManutencao(
        ativo_id=ativo_id,
        manutencoes=manutencoes,
        total_manutencoes=total_manutencoes,
        custo_total=custo_total,
        tempo_inatividade_total=tempo_inatividade_total,
        ultima_manutencao=ultima_manutencao
    )


@router.get("/metricas/dashboard", response_model=ManutencaoMetricas)
async def obter_metricas_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter métricas para dashboard de manutenção"""
    
    # Manutenções abertas
    total_abertas = db.query(Manutencao).filter(
        Manutencao.status == "aberta"
    ).count()
    
    # Manutenções em andamento
    total_em_andamento = db.query(Manutencao).filter(
        Manutencao.status == "em_andamento"
    ).count()
    
    # Manutenções vencidas
    total_vencidas = db.query(Manutencao).filter(
        and_(
            Manutencao.data_vencimento_sla < datetime.now(),
            Manutencao.status.in_(["aberta", "em_andamento"])
        )
    ).count()
    
    # Manutenções finalizadas no mês
    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total_finalizadas_mes = db.query(Manutencao).filter(
        and_(
            Manutencao.status == "finalizada",
            Manutencao.data_fim_real >= inicio_mes
        )
    ).count()
    
    # Tempo médio de resolução
    manutencoes_finalizadas = db.query(Manutencao).filter(
        and_(
            Manutencao.status == "finalizada",
            Manutencao.data_inicio_real.isnot(None),
            Manutencao.data_fim_real.isnot(None)
        )
    ).all()
    
    if manutencoes_finalizadas:
        tempos_resolucao = [
            (m.data_fim_real - m.data_inicio_real).total_seconds() / 3600
            for m in manutencoes_finalizadas
        ]
        tempo_medio_resolucao_horas = sum(tempos_resolucao) / len(tempos_resolucao)
    else:
        tempo_medio_resolucao_horas = 0
    
    # Percentual de SLA cumprido
    manutencoes_com_sla = db.query(Manutencao).filter(
        and_(
            Manutencao.status == "finalizada",
            Manutencao.sla_horas.isnot(None)
        )
    ).all()
    
    if manutencoes_com_sla:
        sla_cumprido = sum(1 for m in manutencoes_com_sla if not m.sla_vencido)
        percentual_sla_cumprido = (sla_cumprido / len(manutencoes_com_sla)) * 100
    else:
        percentual_sla_cumprido = 100
    
    # Custo total do mês
    custo_total_mes = db.query(func.sum(Manutencao.custo_real)).filter(
        and_(
            Manutencao.criado_em >= inicio_mes,
            Manutencao.custo_real.isnot(None)
        )
    ).scalar() or 0
    
    # Ativos em manutenção
    ativos_em_manutencao = db.query(Manutencao.ativo_id).filter(
        Manutencao.status.in_(["aberta", "em_andamento"])
    ).distinct().count()
    
    return ManutencaoMetricas(
        total_abertas=total_abertas,
        total_em_andamento=total_em_andamento,
        total_vencidas=total_vencidas,
        total_finalizadas_mes=total_finalizadas_mes,
        tempo_medio_resolucao_horas=tempo_medio_resolucao_horas,
        percentual_sla_cumprido=percentual_sla_cumprido,
        custo_total_mes=custo_total_mes,
        ativos_em_manutencao=ativos_em_manutencao
    )


@router.get("/alertas/sla", response_model=List[AlertaSLA])
async def obter_alertas_sla(
    horas_antecedencia: int = Query(24, description="Horas de antecedência para alerta"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter alertas de SLA próximo ao vencimento"""
    
    limite_alerta = datetime.now() + timedelta(hours=horas_antecedencia)
    
    manutencoes = db.query(Manutencao).join(Ativo).filter(
        and_(
            Manutencao.status.in_(["aberta", "em_andamento"]),
            Manutencao.data_vencimento_sla.isnot(None),
            Manutencao.data_vencimento_sla <= limite_alerta
        )
    ).all()
    
    alertas = []
    for m in manutencoes:
        horas_restantes = (m.data_vencimento_sla - datetime.now()).total_seconds() / 3600
        percentual_utilizado = ((m.sla_horas * 3600 - (m.data_vencimento_sla - datetime.now()).total_seconds()) / (m.sla_horas * 3600)) * 100
        
        alertas.append(AlertaSLA(
            manutencao_id=m.id,
            numero_ticket=m.numero_ticket,
            ativo_codigo=m.ativo.codigo,
            titulo=m.titulo,
            sla_horas=m.sla_horas,
            horas_restantes=max(0, horas_restantes),
            percentual_utilizado=min(100, max(0, percentual_utilizado)),
            status=m.status,
            atribuido_para=m.atribuido_para_user.nome if m.atribuido_para else None
        ))
    
    return alertas


def calcular_sla(categoria: str, tipo: str, prioridade: str) -> int:
    """Calcular SLA em horas baseado na categoria, tipo e prioridade"""
    
    # Matriz de SLA (em horas)
    sla_matrix = {
        "critica": {"preventiva": 24, "corretiva": 4, "garantia": 8},
        "alta": {"preventiva": 48, "corretiva": 8, "garantia": 16},
        "media": {"preventiva": 72, "corretiva": 24, "garantia": 48},
        "baixa": {"preventiva": 168, "corretiva": 72, "garantia": 96}
    }
    
    # Ajuste por prioridade
    multiplicador_prioridade = {
        "critica": 0.5,
        "alta": 0.75,
        "media": 1.0,
        "baixa": 1.5
    }
    
    sla_base = sla_matrix.get(prioridade.lower(), sla_matrix["media"])
    sla_tipo = sla_base.get(tipo.lower(), sla_base["corretiva"])
    
    return int(sla_tipo * multiplicador_prioridade.get(prioridade.lower(), 1.0))