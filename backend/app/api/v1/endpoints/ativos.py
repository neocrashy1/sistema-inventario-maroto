"""
Ativos API endpoints for Levitiis inventory system
Asset management CRUD operations and business logic
"""

from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models import User, Ativo, Local, Responsavel, Setor, CentroCusto, Fornecedor
from app.schemas.ativos import (
    AtivoCreate, AtivoUpdate, AtivoResponse, AtivoList, 
    AtivoFilter, AtivoImport, EtiquetaQR
)

router = APIRouter()


@router.post("/", response_model=AtivoResponse)
def criar_ativo(
    ativo: AtivoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Criar novo ativo"""
    
    # Verificar se código já existe
    if db.query(Ativo).filter(Ativo.codigo == ativo.codigo).first():
        raise HTTPException(status_code=400, detail="Código do ativo já existe")
    
    # Verificar se patrimônio já existe (se fornecido)
    if ativo.patrimonio and db.query(Ativo).filter(Ativo.patrimonio == ativo.patrimonio).first():
        raise HTTPException(status_code=400, detail="Número de patrimônio já existe")
    
    # Verificar se número de série já existe (se fornecido)
    if ativo.numero_serie and db.query(Ativo).filter(Ativo.numero_serie == ativo.numero_serie).first():
        raise HTTPException(status_code=400, detail="Número de série já existe")
    
    # Criar ativo
    db_ativo = Ativo(**ativo.dict(), criado_por=current_user.id)
    db.add(db_ativo)
    db.commit()
    db.refresh(db_ativo)
    
    return db_ativo


@router.get("/", response_model=AtivoList)
def listar_ativos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    query: Optional[str] = Query(None, description="Busca por código, patrimônio, descrição ou número de série"),
    categoria: Optional[str] = Query(None),
    subcategoria: Optional[str] = Query(None),
    setor_id: Optional[int] = Query(None),
    local_id: Optional[int] = Query(None),
    responsavel_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    centro_custo_id: Optional[int] = Query(None),
    fornecedor_id: Optional[int] = Query(None),
    valor_min: Optional[float] = Query(None),
    valor_max: Optional[float] = Query(None),
    data_compra_inicio: Optional[str] = Query(None),
    data_compra_fim: Optional[str] = Query(None),
    sem_auditoria_dias: Optional[int] = Query(None, description="Ativos sem auditoria há X dias"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Listar ativos com filtros avançados"""
    
    query_obj = db.query(Ativo)
    
    # Filtro de busca textual
    if query:
        search_filter = or_(
            Ativo.codigo.ilike(f"%{query}%"),
            Ativo.patrimonio.ilike(f"%{query}%"),
            Ativo.descricao.ilike(f"%{query}%"),
            Ativo.numero_serie.ilike(f"%{query}%"),
            Ativo.marca.ilike(f"%{query}%"),
            Ativo.modelo.ilike(f"%{query}%")
        )
        query_obj = query_obj.filter(search_filter)
    
    # Filtros específicos
    if categoria:
        query_obj = query_obj.filter(Ativo.categoria == categoria)
    if subcategoria:
        query_obj = query_obj.filter(Ativo.subcategoria == subcategoria)
    if setor_id:
        query_obj = query_obj.filter(Ativo.setor_id == setor_id)
    if local_id:
        query_obj = query_obj.filter(Ativo.local_id == local_id)
    if responsavel_id:
        query_obj = query_obj.filter(Ativo.responsavel_id == responsavel_id)
    if status:
        query_obj = query_obj.filter(Ativo.status == status)
    if estado:
        query_obj = query_obj.filter(Ativo.estado == estado)
    if centro_custo_id:
        query_obj = query_obj.filter(Ativo.centro_custo_id == centro_custo_id)
    if fornecedor_id:
        query_obj = query_obj.filter(Ativo.fornecedor_id == fornecedor_id)
    
    # Filtros de valor
    if valor_min is not None:
        query_obj = query_obj.filter(Ativo.valor_aquisicao >= valor_min)
    if valor_max is not None:
        query_obj = query_obj.filter(Ativo.valor_aquisicao <= valor_max)
    
    # Filtros de data
    if data_compra_inicio:
        query_obj = query_obj.filter(Ativo.data_compra >= data_compra_inicio)
    if data_compra_fim:
        query_obj = query_obj.filter(Ativo.data_compra <= data_compra_fim)
    
    # Filtro de auditoria
    if sem_auditoria_dias:
        from datetime import datetime, timedelta
        data_limite = datetime.now() - timedelta(days=sem_auditoria_dias)
        query_obj = query_obj.filter(
            or_(
                Ativo.ultima_auditoria.is_(None),
                Ativo.ultima_auditoria < data_limite
            )
        )
    
    # Contar total
    total = query_obj.count()
    
    # Aplicar paginação e ordenação
    ativos = query_obj.order_by(Ativo.codigo).offset(skip).limit(limit).all()
    
    return {
        "items": ativos,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{ativo_id}", response_model=AtivoResponse)
def obter_ativo(
    ativo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obter ativo por ID"""
    ativo = db.query(Ativo).filter(Ativo.id == ativo_id).first()
    if not ativo:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    return ativo


@router.put("/{ativo_id}", response_model=AtivoResponse)
def atualizar_ativo(
    ativo_id: int,
    ativo_update: AtivoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualizar ativo"""
    ativo = db.query(Ativo).filter(Ativo.id == ativo_id).first()
    if not ativo:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    
    # Verificar duplicatas se campos únicos foram alterados
    update_data = ativo_update.dict(exclude_unset=True)
    
    if "codigo" in update_data and update_data["codigo"] != ativo.codigo:
        if db.query(Ativo).filter(Ativo.codigo == update_data["codigo"]).first():
            raise HTTPException(status_code=400, detail="Código do ativo já existe")
    
    if "patrimonio" in update_data and update_data["patrimonio"] != ativo.patrimonio:
        if db.query(Ativo).filter(Ativo.patrimonio == update_data["patrimonio"]).first():
            raise HTTPException(status_code=400, detail="Número de patrimônio já existe")
    
    if "numero_serie" in update_data and update_data["numero_serie"] != ativo.numero_serie:
        if db.query(Ativo).filter(Ativo.numero_serie == update_data["numero_serie"]).first():
            raise HTTPException(status_code=400, detail="Número de série já existe")
    
    # Atualizar campos
    for field, value in update_data.items():
        setattr(ativo, field, value)
    
    ativo.atualizado_por = current_user.id
    db.commit()
    db.refresh(ativo)
    
    return ativo


@router.delete("/{ativo_id}")
def excluir_ativo(
    ativo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Excluir ativo (soft delete)"""
    ativo = db.query(Ativo).filter(Ativo.id == ativo_id).first()
    if not ativo:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    
    # Verificar se ativo pode ser excluído (regras de negócio)
    if ativo.status in ["alocado", "em_manutencao"]:
        raise HTTPException(
            status_code=400, 
            detail="Não é possível excluir ativo alocado ou em manutenção"
        )
    
    # Soft delete
    ativo.ativo = False
    ativo.atualizado_por = current_user.id
    db.commit()
    
    return {"message": "Ativo excluído com sucesso"}


@router.post("/{ativo_id}/etiqueta", response_model=EtiquetaQR)
def gerar_etiqueta_qr(
    ativo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Gerar etiqueta QR/NFC para ativo"""
    ativo = db.query(Ativo).filter(Ativo.id == ativo_id).first()
    if not ativo:
        raise HTTPException(status_code=404, detail="Ativo não encontrado")
    
    # Gerar código QR
    import qrcode
    import io
    import base64
    
    qr_data = {
        "id": ativo.id,
        "codigo": ativo.codigo,
        "patrimonio": ativo.patrimonio,
        "tipo": "ativo_levitiis"
    }
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(str(qr_data))
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Converter para base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    # Atualizar ativo com código QR
    ativo.codigo_qr = f"data:image/png;base64,{img_str}"
    ativo.etiqueta_gerada = True
    db.commit()
    
    return {
        "ativo_id": ativo.id,
        "codigo_qr": ativo.codigo_qr,
        "qr_data": qr_data
    }


@router.post("/importar")
def importar_ativos_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Importar ativos via CSV"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser CSV")
    
    import csv
    import io
    
    # Ler arquivo CSV
    content = file.file.read()
    csv_data = io.StringIO(content.decode('utf-8'))
    reader = csv.DictReader(csv_data)
    
    resultados = {
        "sucessos": 0,
        "erros": 0,
        "detalhes": []
    }
    
    for row_num, row in enumerate(reader, start=2):
        try:
            # Validar campos obrigatórios
            if not row.get('codigo'):
                raise ValueError("Código é obrigatório")
            
            # Verificar duplicatas
            if db.query(Ativo).filter(Ativo.codigo == row['codigo']).first():
                raise ValueError(f"Código {row['codigo']} já existe")
            
            # Criar ativo
            ativo_data = {
                'codigo': row['codigo'],
                'patrimonio': row.get('patrimonio'),
                'categoria': row.get('categoria'),
                'subcategoria': row.get('subcategoria'),
                'descricao': row.get('descricao'),
                'marca': row.get('marca'),
                'modelo': row.get('modelo'),
                'numero_serie': row.get('numero_serie'),
                'valor_aquisicao': float(row['valor_aquisicao']) if row.get('valor_aquisicao') else None,
                'data_compra': row.get('data_compra'),
                'criado_por': current_user.id
            }
            
            ativo = Ativo(**{k: v for k, v in ativo_data.items() if v is not None})
            db.add(ativo)
            db.commit()
            
            resultados["sucessos"] += 1
            resultados["detalhes"].append({
                "linha": row_num,
                "codigo": row['codigo'],
                "status": "sucesso"
            })
            
        except Exception as e:
            resultados["erros"] += 1
            resultados["detalhes"].append({
                "linha": row_num,
                "codigo": row.get('codigo', 'N/A'),
                "status": "erro",
                "erro": str(e)
            })
            db.rollback()
    
    return resultados


@router.get("/relatorios/patrimonio")
def relatorio_patrimonio(
    formato: str = Query("json", regex="^(json|csv|xlsx)$"),
    setor_id: Optional[int] = Query(None),
    centro_custo_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Relatório de patrimônio por centro de custo"""
    
    query = db.query(
        Ativo.centro_custo_id,
        CentroCusto.nome.label('centro_custo_nome'),
        func.count(Ativo.id).label('quantidade_ativos'),
        func.sum(Ativo.valor_aquisicao).label('valor_total'),
        func.sum(Ativo.valor_depreciado_acumulado).label('depreciacao_total'),
        func.sum(Ativo.valor_contabil_atual).label('valor_contabil_total')
    ).join(CentroCusto).group_by(Ativo.centro_custo_id, CentroCusto.nome)
    
    if setor_id:
        query = query.filter(Ativo.setor_id == setor_id)
    if centro_custo_id:
        query = query.filter(Ativo.centro_custo_id == centro_custo_id)
    
    resultados = query.all()
    
    if formato == "json":
        return [dict(r._mapping) for r in resultados]
    
    # TODO: Implementar exportação CSV/XLSX
    return {"message": "Exportação CSV/XLSX será implementada"}


@router.get("/dashboard/metricas")
def metricas_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Métricas para dashboard executivo"""
    
    # Contadores básicos
    total_ativos = db.query(func.count(Ativo.id)).scalar()
    ativos_ativos = db.query(func.count(Ativo.id)).filter(Ativo.status == "ativo").scalar()
    ativos_alocados = db.query(func.count(Ativo.id)).filter(Ativo.status == "alocado").scalar()
    ativos_manutencao = db.query(func.count(Ativo.id)).filter(Ativo.status == "em_manutencao").scalar()
    
    # Valores financeiros
    valor_total = db.query(func.sum(Ativo.valor_aquisicao)).scalar() or 0
    valor_contabil = db.query(func.sum(Ativo.valor_contabil_atual)).scalar() or 0
    depreciacao_total = db.query(func.sum(Ativo.valor_depreciado_acumulado)).scalar() or 0
    
    # Ativos por categoria
    ativos_por_categoria = db.query(
        Ativo.categoria,
        func.count(Ativo.id).label('quantidade')
    ).group_by(Ativo.categoria).all()
    
    # Ativos por setor
    ativos_por_setor = db.query(
        Setor.nome,
        func.count(Ativo.id).label('quantidade')
    ).join(Setor).group_by(Setor.nome).all()
    
    # Ativos sem auditoria recente (últimos 6 meses)
    from datetime import datetime, timedelta
    data_limite = datetime.now() - timedelta(days=180)
    ativos_sem_auditoria = db.query(func.count(Ativo.id)).filter(
        or_(
            Ativo.ultima_auditoria.is_(None),
            Ativo.ultima_auditoria < data_limite
        )
    ).scalar()
    
    return {
        "contadores": {
            "total_ativos": total_ativos,
            "ativos_ativos": ativos_ativos,
            "ativos_alocados": ativos_alocados,
            "ativos_manutencao": ativos_manutencao,
            "ativos_sem_auditoria": ativos_sem_auditoria
        },
        "financeiro": {
            "valor_total_aquisicao": float(valor_total),
            "valor_contabil_atual": float(valor_contabil),
            "depreciacao_acumulada": float(depreciacao_total)
        },
        "distribuicao": {
            "por_categoria": [{"categoria": r.categoria, "quantidade": r.quantidade} for r in ativos_por_categoria],
            "por_setor": [{"setor": r.nome, "quantidade": r.quantidade} for r in ativos_por_setor]
        }
    }