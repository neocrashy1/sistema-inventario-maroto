"""
Auditorias API endpoints for Levitiis inventory system
Physical inventory audit and reconciliation management
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.security import require_roles, compute_audit_record_hash, compute_audit_signature
from app.models import (
    User, Ativo, Auditoria, AuditoriaItem, Local, Setor, 
    TipoAuditoria, StatusAuditoria, ResultadoItem
)
from app.models.movement import AssetAudit
from app.schemas.auditorias import (
    AuditoriaCreate, AuditoriaUpdate, AuditoriaResponse, AuditoriaList,
    AuditoriaItemCreate, AuditoriaItemResponse, AuditoriaItemList,
    ListaContagem, ColetaLeitura, RelatorioReconciliacao
)

router = APIRouter()


@router.post("/", response_model=AuditoriaResponse, dependencies=[Depends(require_roles(["admin", "gestor", "auditor"]))])
def criar_auditoria(
    auditoria: AuditoriaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar nova auditoria"""
    
    # Validar escopo da auditoria
    if auditoria.escopo_setores:
        setores = db.query(Setor).filter(Setor.id.in_(auditoria.escopo_setores)).all()
        if len(setores) != len(auditoria.escopo_setores):
            raise HTTPException(status_code=400, detail="Um ou mais setores não encontrados")
    
    if auditoria.escopo_locais:
        locais = db.query(Local).filter(Local.id.in_(auditoria.escopo_locais)).all()
        if len(locais) != len(auditoria.escopo_locais):
            raise HTTPException(status_code=400, detail="Um ou mais locais não encontrados")
    
    # Criar auditoria
    db_auditoria = Auditoria(
        **auditoria.dict(exclude={"escopo_setores", "escopo_locais"}),
        criado_por=current_user.id,
        status=StatusAuditoria.PLANEJADA
    )
    
    # Converter listas para strings JSON
    if auditoria.escopo_setores:
        db_auditoria.escopo_setores = ",".join(map(str, auditoria.escopo_setores))
    if auditoria.escopo_locais:
        db_auditoria.escopo_locais = ",".join(map(str, auditoria.escopo_locais))
    
    db.add(db_auditoria)
    db.commit()
    db.refresh(db_auditoria)
    
    # Gerar itens de auditoria baseado no escopo
    _gerar_itens_auditoria(db_auditoria, db)
    
    return db_auditoria


@router.get("/", response_model=AuditoriaList, dependencies=[Depends(require_roles(["admin", "gestor", "auditor"]))])
def listar_auditorias(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    tipo: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    criado_por: Optional[int] = Query(None),
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar auditorias com filtros"""
    
    query = db.query(Auditoria)
    
    # Aplicar filtros
    if tipo:
        query = query.filter(Auditoria.tipo == tipo)
    if status:
        query = query.filter(Auditoria.status == status)
    if criado_por:
        query = query.filter(Auditoria.criado_por == criado_por)
    if data_inicio:
        query = query.filter(Auditoria.data_inicio >= data_inicio)
    if data_fim:
        query = query.filter(Auditoria.data_fim <= data_fim)
    
    # Contar total
    total = query.count()
    
    # Aplicar paginação e ordenação
    auditorias = query.order_by(Auditoria.criado_em.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": auditorias,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{auditoria_id}", response_model=AuditoriaResponse, dependencies=[Depends(require_roles(["admin", "gestor", "auditor"]))])
def obter_auditoria(
    auditoria_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter auditoria por ID"""
    auditoria = db.query(Auditoria).filter(Auditoria.id == auditoria_id).first()
    if not auditoria:
        raise HTTPException(status_code=404, detail="Auditoria não encontrada")
    return auditoria


@router.put("/{auditoria_id}/iniciar", dependencies=[Depends(require_roles(["admin", "gestor", "auditor"]))])
def iniciar_auditoria(
    auditoria_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Iniciar auditoria planejada"""
    
    auditoria = db.query(Auditoria).filter(Auditoria.id == auditoria_id).first()
    if not auditoria:
        raise HTTPException(status_code=404, detail="Auditoria não encontrada")
    
    if auditoria.status != StatusAuditoria.PLANEJADA:
        raise HTTPException(
            status_code=400, 
            detail=f"Auditoria não pode ser iniciada. Status atual: {auditoria.status}"
        )
    
    # Iniciar auditoria
    auditoria.status = StatusAuditoria.EM_ANDAMENTO
    auditoria.data_inicio = datetime.now()
    
    db.commit()
    
    return {"message": "Auditoria iniciada com sucesso"}


@router.get("/{auditoria_id}/lista-contagem", response_model=ListaContagem, dependencies=[Depends(require_roles(["admin", "gestor", "auditor"]))])
def gerar_lista_contagem(
    auditoria_id: int,
    setor_id: Optional[int] = Query(None, description="Filtrar por setor específico"),
    local_id: Optional[int] = Query(None, description="Filtrar por local específico"),
    priorizar_por: str = Query("valor", regex="^(valor|risco|tempo_sem_auditoria)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Gerar lista de contagem para auditoria"""
    
    auditoria = db.query(Auditoria).filter(Auditoria.id == auditoria_id).first()
    if not auditoria:
        raise HTTPException(status_code=404, detail="Auditoria não encontrada")
    
    if auditoria.status not in [StatusAuditoria.PLANEJADA, StatusAuditoria.EM_ANDAMENTO]:
        raise HTTPException(
            status_code=400, 
            detail="Lista de contagem só pode ser gerada para auditorias planejadas ou em andamento"
        )
    
    # Buscar itens de auditoria
    query = db.query(AuditoriaItem).filter(AuditoriaItem.auditoria_id == auditoria_id)
    
    if setor_id:
        query = query.join(Ativo).filter(Ativo.setor_id == setor_id)
    if local_id:
        query = query.join(Ativo).filter(Ativo.local_id == local_id)
    
    # Aplicar priorização
    if priorizar_por == "valor":
        query = query.join(Ativo).order_by(Ativo.valor_aquisicao.desc())
    elif priorizar_por == "tempo_sem_auditoria":
        query = query.join(Ativo).order_by(Ativo.ultima_auditoria.asc().nullsfirst())
    else:  # risco - heurística simples
        query = query.join(Ativo).order_by(
            (Ativo.valor_aquisicao * func.coalesce(Ativo.historico_divergencias, 0)).desc()
        )
    
    itens = query.all()
    
    # Preparar lista de contagem
    lista_contagem = []
    for item in itens:
        ativo = item.ativo
        lista_contagem.append({
            "item_id": item.id,
            "ativo_id": ativo.id,
            "codigo": ativo.codigo,
            "patrimonio": ativo.patrimonio,
            "descricao": ativo.descricao,
            "categoria": ativo.categoria,
            "local_esperado": ativo.local.nome if ativo.local else None,
            "responsavel_esperado": ativo.responsavel.nome if ativo.responsavel else None,
            "valor": float(ativo.valor_aquisicao) if ativo.valor_aquisicao else None,
            "ultima_auditoria": ativo.ultima_auditoria.isoformat() if ativo.ultima_auditoria else None,
            "codigo_qr": ativo.codigo_qr,
            "observacoes_esperadas": item.observacoes_esperadas
        })
    
    return {
        "auditoria_id": auditoria_id,
        "total_itens": len(lista_contagem),
        "filtros": {
            "setor_id": setor_id,
            "local_id": local_id,
            "priorizar_por": priorizar_por
        },
        "itens": lista_contagem
    }


@router.post("/{auditoria_id}/coletas", response_model=Dict[str, Any], dependencies=[Depends(require_roles(["admin", "gestor", "auditor"]))])
def registrar_coleta(
    auditoria_id: int,
    coletas: List[ColetaLeitura],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Registrar leituras de auditoria (modo online/offline)"""
    
    auditoria = db.query(Auditoria).filter(Auditoria.id == auditoria_id).first()
    if not auditoria:
        raise HTTPException(status_code=404, detail="Auditoria não encontrada")
    
    if auditoria.status != StatusAuditoria.EM_ANDAMENTO:
        raise HTTPException(
            status_code=400, 
            detail="Coletas só podem ser registradas em auditorias em andamento"
        )
    
    resultados = {
        "sucessos": 0,
        "erros": 0,
        "detalhes": []
    }
    
    for coleta in coletas:
        try:
            # Buscar item de auditoria
            item = db.query(AuditoriaItem).filter(
                and_(
                    AuditoriaItem.auditoria_id == auditoria_id,
                    AuditoriaItem.id == coleta.item_id
                )
            ).first()
            
            if not item:
                # Verificar se é um ativo extra (não cadastrado na auditoria)
                ativo = db.query(Ativo).filter(Ativo.codigo == coleta.codigo_lido).first()
                if ativo:
                    # Criar item extra
                    item = AuditoriaItem(
                        auditoria_id=auditoria_id,
                        ativo_id=ativo.id,
                        resultado=ResultadoItem.EXTRA
                    )
                    db.add(item)
                    db.flush()
                else:
                    raise ValueError(f"Código {coleta.codigo_lido} não encontrado")
            
            # Atualizar item com dados da coleta
            item.codigo_lido = coleta.codigo_lido
            item.local_encontrado_id = coleta.local_encontrado_id
            item.estado_encontrado = coleta.estado_encontrado
            item.observacoes_coleta = coleta.observacoes
            item.foto_evidencia_url = coleta.foto_url
            item.coletado_por = current_user.id
            item.data_coleta = datetime.now()
            
            # Determinar resultado da verificação
            ativo = item.ativo
            resultado = _determinar_resultado_verificacao(item, ativo, coleta)
            item.resultado = resultado
            
            # Registrar divergências se houver
            if resultado in [ResultadoItem.DIVERGENTE, ResultadoItem.NAO_ENCONTRADO]:
                divergencias = _identificar_divergencias(item, ativo, coleta)
                item.divergencias = ",".join(divergencias)
            
            # Assinar trilha de auditoria da coleta
            audit_payload = {
                "asset_id": ativo.id,
                "auditoria_id": auditoria_id,
                "auditoria_status": auditoria.status,
                "action": "AUDIT_READ",
                "table_name": "auditoria_itens",
                "record_id": item.id,
                "collector_user_id": current_user.id,
                "codigo_lido": coleta.codigo_lido,
                "local_encontrado_id": coleta.local_encontrado_id,
                "estado_encontrado": coleta.estado_encontrado,
                "resultado": resultado,
                "divergencias": item.divergencias.split(",") if item.divergencias else []
            }
            prev_audit = db.query(AssetAudit).filter(AssetAudit.asset_id == ativo.id).order_by(AssetAudit.created_at.desc()).first()
            prev_hash = prev_audit.record_hash if prev_audit and prev_audit.record_hash else None
            record_hash = compute_audit_record_hash(audit_payload)
            signature = compute_audit_signature(record_hash)
            db.add(AssetAudit(
                asset_id=ativo.id,
                action="AUDIT_READ",
                table_name="auditoria_itens",
                record_id=item.id,
                field_name=None,
                old_value=None,
                new_value=None,
                reason="audit_collection",
                ip_address=None,
                user_agent=None,
                custom_metadata=audit_payload,
                prev_hash=prev_hash,
                record_hash=record_hash,
                signature=signature,
                created_by=current_user.id
            ))
            
            db.commit()
            resultados["sucessos"] += 1
            resultados["detalhes"].append({
                "item_id": item.id,
                "codigo": coleta.codigo_lido,
                "resultado": resultado,
                "status": "sucesso"
            })
            
        except Exception as e:
            resultados["erros"] += 1
            resultados["detalhes"].append({
                "item_id": coleta.item_id,
                "codigo": coleta.codigo_lido,
                "erro": str(e),
                "status": "erro"
            })
            db.rollback()
    
    return resultados


@router.put("/{auditoria_id}/reconciliar", dependencies=[Depends(require_roles(["admin", "gestor", "auditor"]))])
def iniciar_reconciliacao(
    auditoria_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Iniciar processo de reconciliação"""
    
    auditoria = db.query(Auditoria).filter(Auditoria.id == auditoria_id).first()
    if not auditoria:
        raise HTTPException(status_code=404, detail="Auditoria não encontrada")
    
    if auditoria.status != StatusAuditoria.EM_ANDAMENTO:
        raise HTTPException(
            status_code=400, 
            detail="Reconciliação só pode ser iniciada em auditorias em andamento"
        )
    
    # Verificar se há itens coletados
    itens_coletados = db.query(AuditoriaItem).filter(
        and_(
            AuditoriaItem.auditoria_id == auditoria_id,
            AuditoriaItem.data_coleta.isnot(None)
        )
    ).count()
    
    if itens_coletados == 0:
        raise HTTPException(
            status_code=400, 
            detail="Não há itens coletados para reconciliação"
        )
    
    # Iniciar reconciliação
    auditoria.status = StatusAuditoria.RECONCILIACAO
    auditoria.data_reconciliacao = datetime.now()
    
    # Gerar resumo de resultados
    resumo = _gerar_resumo_auditoria(auditoria_id, db)
    auditoria.total_itens = resumo["total_itens"]
    auditoria.itens_conformes = resumo["conformes"]
    auditoria.itens_divergentes = resumo["divergentes"]
    auditoria.itens_nao_encontrados = resumo["nao_encontrados"]
    auditoria.itens_extras = resumo["extras"]
    
    db.commit()
    
    return {
        "message": "Reconciliação iniciada com sucesso",
        "resumo": resumo
    }


@router.get("/{auditoria_id}/relatorio-reconciliacao", response_model=RelatorioReconciliacao, dependencies=[Depends(require_roles(["admin", "gestor", "auditor"]))])
def gerar_relatorio_reconciliacao(
    auditoria_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Gerar relatório de reconciliação"""
    
    auditoria = db.query(Auditoria).filter(Auditoria.id == auditoria_id).first()
    if not auditoria:
        raise HTTPException(status_code=404, detail="Auditoria não encontrada")
    
    if auditoria.status not in [StatusAuditoria.RECONCILIACAO, StatusAuditoria.FINALIZADA]:
        raise HTTPException(
            status_code=400, 
            detail="Relatório só pode ser gerado em auditorias em reconciliação ou finalizadas"
        )
    
    # Buscar todos os itens da auditoria
    itens = db.query(AuditoriaItem).filter(AuditoriaItem.auditoria_id == auditoria_id).all()
    
    # Agrupar por resultado
    itens_por_resultado = {
        "conformes": [],
        "divergentes": [],
        "nao_encontrados": [],
        "extras": []
    }
    
    for item in itens:
        ativo = item.ativo
        item_data = {
            "item_id": item.id,
            "ativo_id": ativo.id,
            "codigo": ativo.codigo,
            "patrimonio": ativo.patrimonio,
            "descricao": ativo.descricao,
            "local_esperado": ativo.local.nome if ativo.local else None,
            "local_encontrado": item.local_encontrado.nome if item.local_encontrado else None,
            "responsavel": ativo.responsavel.nome if ativo.responsavel else None,
            "divergencias": item.divergencias.split(",") if item.divergencias else [],
            "observacoes": item.observacoes_coleta,
            "coletado_por": item.coletor.name if item.coletor else None,
            "data_coleta": item.data_coleta.isoformat() if item.data_coleta else None
        }
        
        if item.resultado == ResultadoItem.CONFORME:
            itens_por_resultado["conformes"].append(item_data)
        elif item.resultado == ResultadoItem.DIVERGENTE:
            itens_por_resultado["divergentes"].append(item_data)
        elif item.resultado == ResultadoItem.NAO_ENCONTRADO:
            itens_por_resultado["nao_encontrados"].append(item_data)
        elif item.resultado == ResultadoItem.EXTRA:
            itens_por_resultado["extras"].append(item_data)
    
    return {
        "auditoria_id": auditoria_id,
        "tipo": auditoria.tipo,
        "status": auditoria.status,
        "data_inicio": auditoria.data_inicio.isoformat() if auditoria.data_inicio else None,
        "data_reconciliacao": auditoria.data_reconciliacao.isoformat() if auditoria.data_reconciliacao else None,
        "resumo": {
            "total_itens": auditoria.total_itens or 0,
            "conformes": auditoria.itens_conformes or 0,
            "divergentes": auditoria.itens_divergentes or 0,
            "nao_encontrados": auditoria.itens_nao_encontrados or 0,
            "extras": auditoria.itens_extras or 0,
            "percentual_conformidade": round(
                (auditoria.itens_conformes or 0) / max(auditoria.total_itens or 1, 1) * 100, 2
            )
        },
        "itens": itens_por_resultado
    }


@router.put("/{auditoria_id}/finalizar", dependencies=[Depends(require_roles(["admin", "gestor", "auditor"]))])
def finalizar_auditoria(
    auditoria_id: int,
    observacoes_finais: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Finalizar auditoria após reconciliação"""
    
    auditoria = db.query(Auditoria).filter(Auditoria.id == auditoria_id).first()
    if not auditoria:
        raise HTTPException(status_code=404, detail="Auditoria não encontrada")
    
    if auditoria.status != StatusAuditoria.RECONCILIACAO:
        raise HTTPException(
            status_code=400, 
            detail="Auditoria só pode ser finalizada após reconciliação"
        )
    
    # Finalizar auditoria
    auditoria.status = StatusAuditoria.FINALIZADA
    auditoria.data_finalizacao = datetime.now()
    auditoria.finalizado_por = current_user.id
    auditoria.observacoes_finais = observacoes_finais
    
    # Atualizar data de última auditoria nos ativos
    itens_conformes = db.query(AuditoriaItem).filter(
        and_(
            AuditoriaItem.auditoria_id == auditoria_id,
            AuditoriaItem.resultado == ResultadoItem.CONFORME
        )
    ).all()
    
    for item in itens_conformes:
        item.ativo.ultima_auditoria = datetime.now()
    
    db.commit()
    
    return {"message": "Auditoria finalizada com sucesso"}


def _gerar_itens_auditoria(auditoria: Auditoria, db: Session):
    """Gerar itens de auditoria baseado no escopo"""
    
    query = db.query(Ativo).filter(Ativo.ativo == True)
    
    # Filtrar por escopo
    if auditoria.escopo_setores:
        setores_ids = [int(x) for x in auditoria.escopo_setores.split(",")]
        query = query.filter(Ativo.setor_id.in_(setores_ids))
    
    if auditoria.escopo_locais:
        locais_ids = [int(x) for x in auditoria.escopo_locais.split(",")]
        query = query.filter(Ativo.local_id.in_(locais_ids))
    
    # Aplicar filtros específicos por tipo de auditoria
    if auditoria.tipo == TipoAuditoria.AMOSTRAGEM:
        # Para amostragem, priorizar ativos de alto valor
        query = query.order_by(Ativo.valor_aquisicao.desc()).limit(auditoria.tamanho_amostra or 100)
    elif auditoria.tipo == TipoAuditoria.CICLICA:
        # Para cíclica, focar em ativos sem auditoria recente
        data_limite = datetime.now() - timedelta(days=180)  # 6 meses
        query = query.filter(
            or_(
                Ativo.ultima_auditoria.is_(None),
                Ativo.ultima_auditoria < data_limite
            )
        )
    
    ativos = query.all()
    
    # Criar itens de auditoria
    for ativo in ativos:
        item = AuditoriaItem(
            auditoria_id=auditoria.id,
            ativo_id=ativo.id,
            local_esperado_id=ativo.local_id,
            responsavel_esperado_id=ativo.responsavel_id,
            estado_esperado=ativo.estado
        )
        db.add(item)
    
    db.commit()


def _determinar_resultado_verificacao(item: AuditoriaItem, ativo: Ativo, coleta: ColetaLeitura) -> str:
    """Determinar resultado da verificação baseado na coleta"""
    
    if not coleta.codigo_lido:
        return ResultadoItem.NAO_ENCONTRADO
    
    # Verificar se há divergências
    divergencias = _identificar_divergencias(item, ativo, coleta)
    
    if not divergencias:
        return ResultadoItem.CONFORME
    else:
        return ResultadoItem.DIVERGENTE


def _identificar_divergencias(item: AuditoriaItem, ativo: Ativo, coleta: ColetaLeitura) -> List[str]:
    """Identificar divergências entre esperado e encontrado"""
    
    divergencias = []
    
    # Verificar local
    if item.local_esperado_id != coleta.local_encontrado_id:
        divergencias.append("local")
    
    # Verificar estado
    if item.estado_esperado != coleta.estado_encontrado:
        divergencias.append("estado")
    
    # Verificar se tem etiqueta
    if not coleta.codigo_lido or coleta.codigo_lido != ativo.codigo:
        divergencias.append("etiqueta")
    
    return divergencias


def _gerar_resumo_auditoria(auditoria_id: int, db: Session) -> Dict[str, int]:
    """Gerar resumo de resultados da auditoria"""
    
    resumo = db.query(
        func.count(AuditoriaItem.id).label('total'),
        func.sum(func.case([(AuditoriaItem.resultado == ResultadoItem.CONFORME, 1)], else_=0)).label('conformes'),
        func.sum(func.case([(AuditoriaItem.resultado == ResultadoItem.DIVERGENTE, 1)], else_=0)).label('divergentes'),
        func.sum(func.case([(AuditoriaItem.resultado == ResultadoItem.NAO_ENCONTRADO, 1)], else_=0)).label('nao_encontrados'),
        func.sum(func.case([(AuditoriaItem.resultado == ResultadoItem.EXTRA, 1)], else_=0)).label('extras')
    ).filter(AuditoriaItem.auditoria_id == auditoria_id).first()
    
    return {
        "total_itens": resumo.total or 0,
        "conformes": resumo.conformes or 0,
        "divergentes": resumo.divergentes or 0,
        "nao_encontrados": resumo.nao_encontrados or 0,
        "extras": resumo.extras or 0
    }