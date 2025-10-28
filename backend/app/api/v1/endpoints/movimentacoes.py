"""
Movimentacoes API endpoints for Levitiis inventory system
Asset movement and custody chain management
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models import User, Ativo, Movimentacao, Local, Responsavel
from app.schemas.movimentacoes import (
    MovimentacaoCreate, MovimentacaoUpdate, MovimentacaoResponse, 
    MovimentacaoList, TermoResponsabilidade
)

router = APIRouter()


@router.post("/", response_model=MovimentacaoResponse)
def criar_movimentacao(
    movimentacao: MovimentacaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar nova movimentação de ativo"""
    
    # Verificar se ativo existe
    ativo = db.query(Ativo).filter(Ativo.id == movimentacao.ativo_id).first()
    if not ativo:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    
    # Verificar se ativo está disponível para movimentação
    if ativo.status in ["baixado", "em_manutencao"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Ativo não pode ser movimentado. Status atual: {ativo.status}"
        )
    
    # Verificar se locais existem
    if movimentacao.local_origem_id:
        local_origem = db.query(Local).filter(Local.id == movimentacao.local_origem_id).first()
        if not local_origem:
            raise HTTPException(status_code=404, detail="Local de origem não encontrado")
    
    if movimentacao.local_destino_id:
        local_destino = db.query(Local).filter(Local.id == movimentacao.local_destino_id).first()
        if not local_destino:
            raise HTTPException(status_code=404, detail="Local de destino não encontrado")
    
    # Verificar se responsáveis existem
    if movimentacao.responsavel_origem_id:
        resp_origem = db.query(Responsavel).filter(Responsavel.id == movimentacao.responsavel_origem_id).first()
        if not resp_origem:
            raise HTTPException(status_code=404, detail="Responsável de origem não encontrado")
    
    if movimentacao.responsavel_destino_id:
        resp_destino = db.query(Responsavel).filter(Responsavel.id == movimentacao.responsavel_destino_id).first()
        if not resp_destino:
            raise HTTPException(status_code=404, detail="Responsável de destino não encontrado")
    
    # Verificar regras de negócio para aprovação
    valor_limite_aprovacao = 5000.0  # Configurável
    requer_aprovacao = (
        ativo.valor_aquisicao and 
        ativo.valor_aquisicao > valor_limite_aprovacao and
        movimentacao.tipo in ["transferencia", "alocacao"]
    )
    
    # Criar movimentação
    db_movimentacao = Movimentacao(
        **movimentacao.dict(),
        solicitado_por=current_user.id,
        status="pendente_aprovacao" if requer_aprovacao else "aprovada",
        requer_aprovacao=requer_aprovacao
    )
    
    db.add(db_movimentacao)
    db.commit()
    db.refresh(db_movimentacao)
    
    # Se não requer aprovação, executar movimentação automaticamente
    if not requer_aprovacao:
        _executar_movimentacao(db_movimentacao, ativo, db)
    
    return db_movimentacao


@router.get("/", response_model=MovimentacaoList)
def listar_movimentacoes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    ativo_id: Optional[int] = Query(None),
    tipo: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    local_origem_id: Optional[int] = Query(None),
    local_destino_id: Optional[int] = Query(None),
    responsavel_origem_id: Optional[int] = Query(None),
    responsavel_destino_id: Optional[int] = Query(None),
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar movimentações com filtros"""
    
    query = db.query(Movimentacao)
    
    # Aplicar filtros
    if ativo_id:
        query = query.filter(Movimentacao.ativo_id == ativo_id)
    if tipo:
        query = query.filter(Movimentacao.tipo == tipo)
    if status:
        query = query.filter(Movimentacao.status == status)
    if local_origem_id:
        query = query.filter(Movimentacao.local_origem_id == local_origem_id)
    if local_destino_id:
        query = query.filter(Movimentacao.local_destino_id == local_destino_id)
    if responsavel_origem_id:
        query = query.filter(Movimentacao.responsavel_origem_id == responsavel_origem_id)
    if responsavel_destino_id:
        query = query.filter(Movimentacao.responsavel_destino_id == responsavel_destino_id)
    
    # Filtros de data
    if data_inicio:
        query = query.filter(Movimentacao.data_solicitacao >= data_inicio)
    if data_fim:
        query = query.filter(Movimentacao.data_solicitacao <= data_fim)
    
    # Contar total
    total = query.count()
    
    # Aplicar paginação e ordenação
    movimentacoes = query.order_by(Movimentacao.data_solicitacao.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": movimentacoes,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{movimentacao_id}", response_model=MovimentacaoResponse)
def obter_movimentacao(
    movimentacao_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter movimentação por ID"""
    movimentacao = db.query(Movimentacao).filter(Movimentacao.id == movimentacao_id).first()
    if not movimentacao:
        raise HTTPException(status_code=404, detail="Movimentação não encontrada")
    return movimentacao


@router.put("/{movimentacao_id}/aprovar")
def aprovar_movimentacao(
    movimentacao_id: int,
    observacoes_aprovacao: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Aprovar movimentação pendente"""
    
    movimentacao = db.query(Movimentacao).filter(Movimentacao.id == movimentacao_id).first()
    if not movimentacao:
        raise HTTPException(status_code=404, detail="Movimentação não encontrada")
    
    if movimentacao.status != "pendente_aprovacao":
        raise HTTPException(
            status_code=400, 
            detail=f"Movimentação não pode ser aprovada. Status atual: {movimentacao.status}"
        )
    
    # Verificar permissões (gestor de setor ou admin)
    # TODO: Implementar verificação de permissões baseada em RBAC
    
    # Aprovar movimentação
    movimentacao.status = "aprovada"
    movimentacao.aprovado_por = current_user.id
    movimentacao.data_aprovacao = func.now()
    movimentacao.observacoes_aprovacao = observacoes_aprovacao
    
    # Executar movimentação
    ativo = db.query(Ativo).filter(Ativo.id == movimentacao.ativo_id).first()
    _executar_movimentacao(movimentacao, ativo, db)
    
    db.commit()
    
    return {"message": "Movimentação aprovada e executada com sucesso"}


@router.put("/{movimentacao_id}/rejeitar")
def rejeitar_movimentacao(
    movimentacao_id: int,
    motivo_rejeicao: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Rejeitar movimentação pendente"""
    
    movimentacao = db.query(Movimentacao).filter(Movimentacao.id == movimentacao_id).first()
    if not movimentacao:
        raise HTTPException(status_code=404, detail="Movimentação não encontrada")
    
    if movimentacao.status != "pendente_aprovacao":
        raise HTTPException(
            status_code=400, 
            detail=f"Movimentação não pode ser rejeitada. Status atual: {movimentacao.status}"
        )
    
    # Rejeitar movimentação
    movimentacao.status = "rejeitada"
    movimentacao.aprovado_por = current_user.id
    movimentacao.data_aprovacao = func.now()
    movimentacao.observacoes_aprovacao = motivo_rejeicao
    
    db.commit()
    
    return {"message": "Movimentação rejeitada com sucesso"}


@router.post("/{movimentacao_id}/termo-responsabilidade", response_model=TermoResponsabilidade)
def gerar_termo_responsabilidade(
    movimentacao_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Gerar termo de responsabilidade digital"""
    
    movimentacao = db.query(Movimentacao).filter(Movimentacao.id == movimentacao_id).first()
    if not movimentacao:
        raise HTTPException(status_code=404, detail="Movimentação não encontrada")
    
    if movimentacao.status != "executada":
        raise HTTPException(
            status_code=400, 
            detail="Termo só pode ser gerado para movimentações executadas"
        )
    
    # Buscar dados relacionados
    ativo = db.query(Ativo).filter(Ativo.id == movimentacao.ativo_id).first()
    responsavel_origem = None
    responsavel_destino = None
    
    if movimentacao.responsavel_origem_id:
        responsavel_origem = db.query(Responsavel).filter(
            Responsavel.id == movimentacao.responsavel_origem_id
        ).first()
    
    if movimentacao.responsavel_destino_id:
        responsavel_destino = db.query(Responsavel).filter(
            Responsavel.id == movimentacao.responsavel_destino_id
        ).first()
    
    # Gerar termo de responsabilidade
    termo = {
        "movimentacao_id": movimentacao.id,
        "ativo": {
            "codigo": ativo.codigo,
            "patrimonio": ativo.patrimonio,
            "descricao": ativo.descricao,
            "valor": float(ativo.valor_aquisicao) if ativo.valor_aquisicao else None
        },
        "tipo_movimentacao": movimentacao.tipo,
        "data_movimentacao": movimentacao.data_execucao.isoformat() if movimentacao.data_execucao else None,
        "responsavel_origem": {
            "nome": responsavel_origem.nome if responsavel_origem else None,
            "email": responsavel_origem.email if responsavel_origem else None,
            "cargo": responsavel_origem.cargo if responsavel_origem else None
        } if responsavel_origem else None,
        "responsavel_destino": {
            "nome": responsavel_destino.nome if responsavel_destino else None,
            "email": responsavel_destino.email if responsavel_destino else None,
            "cargo": responsavel_destino.cargo if responsavel_destino else None
        } if responsavel_destino else None,
        "observacoes": movimentacao.observacoes,
        "hash_integridade": _gerar_hash_termo(movimentacao, ativo)
    }
    
    # Salvar URL do termo na movimentação
    termo_url = f"/api/v1/movimentacoes/{movimentacao.id}/termo-responsabilidade"
    movimentacao.termo_responsabilidade_url = termo_url
    db.commit()
    
    return termo


@router.get("/{movimentacao_id}/historico")
def obter_historico_ativo(
    movimentacao_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter histórico completo de movimentações do ativo"""
    
    movimentacao = db.query(Movimentacao).filter(Movimentacao.id == movimentacao_id).first()
    if not movimentacao:
        raise HTTPException(status_code=404, detail="Movimentação não encontrada")
    
    # Buscar todas as movimentações do ativo
    historico = db.query(Movimentacao).filter(
        Movimentacao.ativo_id == movimentacao.ativo_id
    ).order_by(Movimentacao.data_solicitacao.desc()).all()
    
    return {
        "ativo_id": movimentacao.ativo_id,
        "total_movimentacoes": len(historico),
        "movimentacoes": historico
    }


def _executar_movimentacao(movimentacao: Movimentacao, ativo: Ativo, db: Session):
    """Executar movimentação aprovada"""
    
    # Atualizar localização e responsável do ativo
    if movimentacao.local_destino_id:
        ativo.local_id = movimentacao.local_destino_id
    
    if movimentacao.responsavel_destino_id:
        ativo.responsavel_id = movimentacao.responsavel_destino_id
    
    # Atualizar status do ativo baseado no tipo de movimentação
    if movimentacao.tipo == "alocacao":
        ativo.status = "alocado"
    elif movimentacao.tipo == "devolucao":
        ativo.status = "ativo"
    elif movimentacao.tipo == "manutencao":
        ativo.status = "em_manutencao"
    elif movimentacao.tipo == "baixa":
        ativo.status = "baixado"
        ativo.ativo = False
    
    # Atualizar movimentação
    movimentacao.status = "executada"
    movimentacao.data_execucao = func.now()
    
    # Atualizar timestamp de última movimentação do ativo
    ativo.ultima_movimentacao = func.now()


def _gerar_hash_termo(movimentacao: Movimentacao, ativo: Ativo) -> str:
    """Gerar hash de integridade para o termo de responsabilidade"""
    import hashlib
    
    dados = f"{movimentacao.id}{ativo.codigo}{movimentacao.tipo}{movimentacao.data_execucao}"
    return hashlib.sha256(dados.encode()).hexdigest()


@router.get("/pendentes/aprovacao")
def listar_movimentacoes_pendentes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar movimentações pendentes de aprovação"""
    
    movimentacoes = db.query(Movimentacao).filter(
        Movimentacao.status == "pendente_aprovacao"
    ).order_by(Movimentacao.data_solicitacao.asc()).all()
    
    return {
        "total": len(movimentacoes),
        "movimentacoes": movimentacoes
    }


@router.get("/relatorios/cadeia-custodia/{ativo_id}")
def relatorio_cadeia_custodia(
    ativo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Relatório de cadeia de custódia de um ativo"""
    
    ativo = db.query(Ativo).filter(Ativo.id == ativo_id).first()
    if not ativo:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    
    movimentacoes = db.query(Movimentacao).filter(
        Movimentacao.ativo_id == ativo_id
    ).order_by(Movimentacao.data_solicitacao.asc()).all()
    
    return {
        "ativo": {
            "id": ativo.id,
            "codigo": ativo.codigo,
            "patrimonio": ativo.patrimonio,
            "descricao": ativo.descricao
        },
        "cadeia_custodia": [
            {
                "data": mov.data_execucao or mov.data_solicitacao,
                "tipo": mov.tipo,
                "status": mov.status,
                "local_origem": mov.local_origem.nome if mov.local_origem else None,
                "local_destino": mov.local_destino.nome if mov.local_destino else None,
                "responsavel_origem": mov.responsavel_origem.nome if mov.responsavel_origem else None,
                "responsavel_destino": mov.responsavel_destino.nome if mov.responsavel_destino else None,
                "solicitado_por": mov.solicitante.name if mov.solicitante else None,
                "observacoes": mov.observacoes
            }
            for mov in movimentacoes
        ]
    }