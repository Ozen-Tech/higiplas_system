"""
Rotas para sistema de visitas de vendedores.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from ..db.connection import get_db
from ..dependencies import get_current_user, get_current_vendedor
from ..db import models
from ..schemas import visitas as schemas
from ..crud import visitas as crud_visitas

router = APIRouter(
    prefix="/visitas",
    tags=["Visitas de Vendedores"]
)


@router.post(
    "/",
    response_model=schemas.VisitaVendedorResponse,
    summary="Registra uma nova visita",
    description="Registra uma nova visita de vendedor com localização GPS."
)
def criar_visita(
    visita: schemas.VisitaVendedorCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria uma nova visita de vendedor."""
    # Validar que é vendedor ou admin
    perfil_upper = current_user.perfil.upper() if current_user.perfil else ""
    if not ("VENDEDOR" in perfil_upper or perfil_upper in ["ADMIN", "GESTOR"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas vendedores podem registrar visitas"
        )
    
    # Se não fornecido, usar vendedor logado
    if not visita.vendedor_id:
        visita.vendedor_id = current_user.id
    
    # Se não fornecido, usar empresa do usuário
    if not visita.empresa_id:
        visita.empresa_id = current_user.empresa_id
    
    # Validar que o vendedor pertence à mesma empresa
    if visita.vendedor_id != current_user.id:
        vendedor = db.query(models.Usuario).filter(
            models.Usuario.id == visita.vendedor_id,
            models.Usuario.empresa_id == current_user.empresa_id
        ).first()
        if not vendedor:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vendedor não encontrado ou não pertence à mesma empresa"
            )
    
    # Validar cliente se fornecido
    if visita.cliente_id:
        cliente = db.query(models.Cliente).filter(
            models.Cliente.id == visita.cliente_id,
            models.Cliente.empresa_id == current_user.empresa_id
        ).first()
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado"
            )
    
    try:
        db_visita = crud_visitas.create_visita(db=db, visita=visita)
        
        # Carregar relacionamentos para resposta
        db.refresh(db_visita)
        if db_visita.vendedor:
            vendedor_nome = db_visita.vendedor.nome
        else:
            vendedor_nome = None
        
        if db_visita.cliente:
            cliente_nome = db_visita.cliente.razao_social
        else:
            cliente_nome = None
        
        if db_visita.empresa:
            empresa_nome = db_visita.empresa.nome
        else:
            empresa_nome = None
        
        response = schemas.VisitaVendedorResponse.model_validate(db_visita)
        response.vendedor_nome = vendedor_nome
        response.cliente_nome = cliente_nome
        response.empresa_nome = empresa_nome
        
        return response
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar visita: {str(e)}"
        )


@router.get(
    "/",
    response_model=List[schemas.VisitaVendedorResponse],
    summary="Lista visitas",
    description="Lista visitas do vendedor logado ou de todos os vendedores (se admin)."
)
def listar_visitas(
    vendedor_id: Optional[int] = Query(None, description="ID do vendedor (apenas admin)"),
    confirmada: Optional[bool] = Query(None, description="Filtrar por status de confirmação"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista visitas."""
    perfil_upper = current_user.perfil.upper() if current_user.perfil else ""
    
    # Vendedores só veem suas próprias visitas
    if "VENDEDOR" in perfil_upper and perfil_upper not in ["ADMIN", "GESTOR"]:
        vendedor_id = current_user.id
    
    # Admin pode ver visitas de todos ou filtrar por vendedor
    visitas = crud_visitas.get_visitas_by_vendedor(
        db=db,
        vendedor_id=vendedor_id or current_user.id,
        empresa_id=current_user.empresa_id,
        confirmada=confirmada,
        limit=limit,
        offset=offset
    )
    
    # Enriquecer com nomes
    result = []
    for visita in visitas:
        response = schemas.VisitaVendedorResponse.model_validate(visita)
        if visita.vendedor:
            response.vendedor_nome = visita.vendedor.nome
        if visita.cliente:
            response.cliente_nome = visita.cliente.razao_social
        if visita.empresa:
            response.empresa_nome = visita.empresa.nome
        result.append(response)
    
    return result


@router.get(
    "/mapa",
    response_model=List[schemas.VisitaVendedorResponse],
    summary="Lista visitas confirmadas para mapa",
    description="Lista apenas visitas confirmadas para exibir no mapa com filtros."
)
def listar_visitas_mapa(
    vendedor_id: Optional[int] = Query(None),
    cliente_id: Optional[int] = Query(None),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    limit: int = Query(1000, ge=1, le=5000),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista visitas confirmadas para exibir no mapa."""
    visitas = crud_visitas.get_visitas_confirmadas(
        db=db,
        empresa_id=current_user.empresa_id,
        vendedor_id=vendedor_id,
        cliente_id=cliente_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        limit=limit
    )
    
    # Enriquecer com nomes
    result = []
    for visita in visitas:
        response = schemas.VisitaVendedorResponse.model_validate(visita)
        if visita.vendedor:
            response.vendedor_nome = visita.vendedor.nome
        if visita.cliente:
            response.cliente_nome = visita.cliente.razao_social
        if visita.empresa:
            response.empresa_nome = visita.empresa.nome
        result.append(response)
    
    return result


@router.get(
    "/{visita_id}",
    response_model=schemas.VisitaVendedorResponse,
    summary="Busca visita por ID",
    description="Retorna detalhes de uma visita específica."
)
def buscar_visita(
    visita_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Busca visita por ID."""
    visita = crud_visitas.get_visita_by_id(
        db=db,
        visita_id=visita_id,
        empresa_id=current_user.empresa_id
    )
    
    if not visita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visita não encontrada"
        )
    
    # Verificar permissão (vendedor só vê suas próprias visitas)
    perfil_upper = current_user.perfil.upper() if current_user.perfil else ""
    if "VENDEDOR" in perfil_upper and perfil_upper not in ["ADMIN", "GESTOR"]:
        if visita.vendedor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
    
    response = schemas.VisitaVendedorResponse.model_validate(visita)
    if visita.vendedor:
        response.vendedor_nome = visita.vendedor.nome
    if visita.cliente:
        response.cliente_nome = visita.cliente.razao_social
    if visita.empresa:
        response.empresa_nome = visita.empresa.nome
    
    return response


@router.patch(
    "/{visita_id}",
    response_model=schemas.VisitaVendedorResponse,
    summary="Atualiza visita",
    description="Atualiza uma visita (apenas se não confirmada)."
)
def atualizar_visita(
    visita_id: int,
    visita_update: schemas.VisitaVendedorUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza uma visita."""
    visita = crud_visitas.get_visita_by_id(
        db=db,
        visita_id=visita_id,
        empresa_id=current_user.empresa_id
    )
    
    if not visita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visita não encontrada"
        )
    
    # Verificar permissão
    perfil_upper = current_user.perfil.upper() if current_user.perfil else ""
    if "VENDEDOR" in perfil_upper and perfil_upper not in ["ADMIN", "GESTOR"]:
        if visita.vendedor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
    
    try:
        visita_atualizada = crud_visitas.update_visita(
            db=db,
            visita_id=visita_id,
            empresa_id=current_user.empresa_id,
            visita_update=visita_update
        )
        
        if not visita_atualizada:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Visita não encontrada"
            )
        
        response = schemas.VisitaVendedorResponse.model_validate(visita_atualizada)
        if visita_atualizada.vendedor:
            response.vendedor_nome = visita_atualizada.vendedor.nome
        if visita_atualizada.cliente:
            response.cliente_nome = visita_atualizada.cliente.razao_social
        if visita_atualizada.empresa:
            response.empresa_nome = visita_atualizada.empresa.nome
        
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{visita_id}/confirmar",
    response_model=schemas.VisitaVendedorResponse,
    summary="Confirma visita",
    description="Confirma uma visita (não permite mais edição)."
)
def confirmar_visita(
    visita_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Confirma uma visita."""
    visita = crud_visitas.get_visita_by_id(
        db=db,
        visita_id=visita_id,
        empresa_id=current_user.empresa_id
    )
    
    if not visita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visita não encontrada"
        )
    
    # Verificar permissão
    perfil_upper = current_user.perfil.upper() if current_user.perfil else ""
    if "VENDEDOR" in perfil_upper and perfil_upper not in ["ADMIN", "GESTOR"]:
        if visita.vendedor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
    
    visita_confirmada = crud_visitas.confirmar_visita(
        db=db,
        visita_id=visita_id,
        empresa_id=current_user.empresa_id
    )
    
    if not visita_confirmada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visita não encontrada"
        )
    
    response = schemas.VisitaVendedorResponse.model_validate(visita_confirmada)
    if visita_confirmada.vendedor:
        response.vendedor_nome = visita_confirmada.vendedor.nome
    if visita_confirmada.cliente:
        response.cliente_nome = visita_confirmada.cliente.razao_social
    if visita_confirmada.empresa:
        response.empresa_nome = visita_confirmada.empresa.nome
    
    return response


@router.get(
    "/stats/estatisticas",
    response_model=schemas.VisitaVendedorStatsResponse,
    summary="Estatísticas de visitas",
    description="Retorna estatísticas de visitas do vendedor logado ou de todos (se admin)."
)
def estatisticas_visitas(
    vendedor_id: Optional[int] = Query(None, description="ID do vendedor (apenas admin)"),
    periodo_dias: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Retorna estatísticas de visitas."""
    perfil_upper = current_user.perfil.upper() if current_user.perfil else ""
    
    # Vendedores só veem suas próprias estatísticas
    if "VENDEDOR" in perfil_upper and perfil_upper not in ["ADMIN", "GESTOR"]:
        vendedor_id = current_user.id
    
    stats = crud_visitas.get_visitas_stats(
        db=db,
        vendedor_id=vendedor_id,
        empresa_id=current_user.empresa_id,
        periodo_dias=periodo_dias
    )
    
    return schemas.VisitaVendedorStatsResponse(**stats)


@router.delete(
    "/{visita_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove visita",
    description="Remove uma visita (apenas se não confirmada)."
)
def remover_visita(
    visita_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Remove uma visita."""
    visita = crud_visitas.get_visita_by_id(
        db=db,
        visita_id=visita_id,
        empresa_id=current_user.empresa_id
    )
    
    if not visita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Visita não encontrada"
        )
    
    # Verificar permissão
    perfil_upper = current_user.perfil.upper() if current_user.perfil else ""
    if "VENDEDOR" in perfil_upper and perfil_upper not in ["ADMIN", "GESTOR"]:
        if visita.vendedor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
    
    try:
        crud_visitas.delete_visita(
            db=db,
            visita_id=visita_id,
            empresa_id=current_user.empresa_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
