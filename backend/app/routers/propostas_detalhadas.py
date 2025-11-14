# backend/app/routers/propostas_detalhadas.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.connection import get_db
from app.dependencies import get_current_user, get_admin_user
from app.db import models
from app.schemas import proposta_detalhada as schemas
from app.crud import proposta_detalhada as crud_proposta

router = APIRouter(
    prefix="/propostas-detalhadas",
    tags=["Propostas Detalhadas"]
)


def _proposta_to_response(proposta: models.PropostaDetalhada, comparacoes: Optional[List[schemas.ComparacaoConcorrente]] = None) -> schemas.PropostaDetalhadaResponse:
    """Converte um modelo PropostaDetalhada para PropostaDetalhadaResponse"""
    return schemas.PropostaDetalhadaResponse(
        id=proposta.id,
        orcamento_id=proposta.orcamento_id,
        cliente_id=proposta.cliente_id,
        produto_id=proposta.produto_id,
        quantidade_produto=proposta.quantidade_produto,
        dilucao_aplicada=proposta.dilucao_aplicada,
        dilucao_numerador=proposta.dilucao_numerador,
        dilucao_denominador=proposta.dilucao_denominador,
        concorrente_id=proposta.concorrente_id,
        observacoes=proposta.observacoes,
        compartilhavel=proposta.compartilhavel,
        vendedor_id=proposta.vendedor_id,
        ficha_tecnica_id=proposta.ficha_tecnica_id,
        rendimento_total_litros=proposta.rendimento_total_litros,
        preco_produto=proposta.preco_produto,
        custo_por_litro_final=proposta.custo_por_litro_final,
        economia_vs_concorrente=proposta.economia_vs_concorrente,
        economia_percentual=proposta.economia_percentual,
        economia_valor=proposta.economia_valor,
        token_compartilhamento=proposta.token_compartilhamento,
        data_criacao=proposta.data_criacao,
        data_atualizacao=proposta.data_atualizacao,
        produto_nome=proposta.produto.nome if proposta.produto else None,
        cliente_nome=proposta.cliente.razao_social if proposta.cliente else None,
        vendedor_nome=proposta.vendedor.nome if proposta.vendedor else None,
        ficha_tecnica=schemas.FichaTecnica.model_validate(proposta.ficha_tecnica) if proposta.ficha_tecnica else None,
        concorrente=schemas.ProdutoConcorrente.model_validate(proposta.concorrente) if proposta.concorrente else None,
        comparacoes=comparacoes or []
    )


@router.post("/", response_model=schemas.PropostaDetalhadaResponse, status_code=status.HTTP_201_CREATED, summary="Cria proposta detalhada")
def create_proposta_detalhada(
    proposta_in: schemas.PropostaDetalhadaCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Cria uma proposta detalhada com cálculos automáticos de rendimento e comparação com concorrentes.
    Disponível para vendedores.
    """
    from app.core.logger import app_logger
    app_logger.info(f"Criando proposta detalhada para produto {proposta_in.produto_id}, cliente {proposta_in.cliente_id}, vendedor {current_user.id}")
    app_logger.info(f"Dados da proposta: quantidade={proposta_in.quantidade_produto}, dilucao={proposta_in.dilucao_aplicada}, num={proposta_in.dilucao_numerador}, den={proposta_in.dilucao_denominador}")
    try:
        proposta = crud_proposta.create_proposta_detalhada(
            db, proposta_in, current_user.id
        )
        app_logger.info(f"Proposta criada com sucesso: ID {proposta.id}")
        
        # Buscar proposta completa com relacionamentos
        proposta_completa = crud_proposta.get_proposta_by_id(db, proposta.id, incluir_relacionamentos=True)
        
        if not proposta_completa:
            app_logger.error(f"Erro: Proposta {proposta.id} não encontrada após criação")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao recuperar proposta criada"
            )
        
        # Buscar comparações
        if proposta_completa.rendimento_total_litros and proposta_completa.custo_por_litro_final:
            comparacoes = crud_proposta.comparar_com_concorrentes(
                db,
                proposta_in.produto_id,
                proposta_completa.rendimento_total_litros,
                proposta_completa.custo_por_litro_final,
                proposta_completa.produto.categoria if proposta_completa.produto else None
            )
        else:
            comparacoes = []
        
        # Montar resposta usando função auxiliar
        response = _proposta_to_response(proposta_completa, comparacoes)
        app_logger.info(f"Resposta montada com sucesso para proposta {proposta.id}")
        return response
        
    except ValueError as e:
        app_logger.error(f"Erro de validação ao criar proposta: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Erro inesperado ao criar proposta: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar proposta: {str(e)}"
        )


@router.get("/me", response_model=List[schemas.PropostaDetalhadaResponse], summary="Lista minhas propostas")
def get_my_propostas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todas as propostas criadas pelo vendedor logado"""
    propostas = crud_proposta.get_propostas_by_vendedor(
        db, current_user.id, skip=skip, limit=limit
    )
    
    # Converter para response
    response_list = []
    for proposta in propostas:
        # Carregar relacionamentos se necessário
        if not proposta.produto:
            proposta_completa = crud_proposta.get_proposta_by_id(db, proposta.id, incluir_relacionamentos=True)
            if proposta_completa:
                proposta = proposta_completa
        response_list.append(_proposta_to_response(proposta))
    
    return response_list


@router.get("/{proposta_id}", response_model=schemas.PropostaDetalhadaCompleta, summary="Visualiza proposta completa")
def get_proposta_by_id(
    proposta_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Visualiza uma proposta detalhada completa"""
    proposta = crud_proposta.get_proposta_by_id(db, proposta_id, incluir_relacionamentos=True)
    
    if not proposta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposta {proposta_id} não encontrada"
        )
    
    # Verificar permissão: vendedor só vê suas próprias propostas, admin vê todas
    is_admin = current_user.perfil.upper() in ["ADMIN", "GESTOR"]
    if not is_admin and proposta.vendedor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para visualizar esta proposta"
        )
    
    # Buscar comparações
    comparacoes = []
    if proposta.rendimento_total_litros and proposta.custo_por_litro_final:
        comparacoes = crud_proposta.comparar_com_concorrentes(
            db,
            proposta.produto_id,
            proposta.rendimento_total_litros,
            proposta.custo_por_litro_final,
            proposta.produto.categoria if proposta.produto else None
        )
    
    # Montar resposta usando função auxiliar e converter para Completa
    response = _proposta_to_response(proposta, comparacoes)
    return schemas.PropostaDetalhadaCompleta(**response.model_dump())


@router.get("/cliente/{cliente_id}", response_model=List[schemas.PropostaDetalhadaResponse], summary="Lista propostas de um cliente")
def get_propostas_by_cliente(
    cliente_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todas as propostas de um cliente específico"""
    propostas = crud_proposta.get_propostas_by_cliente(
        db, cliente_id, skip=skip, limit=limit
    )
    
    # Verificar permissão: vendedor só vê propostas de clientes que ele atende
    is_admin = current_user.perfil.upper() in ["ADMIN", "GESTOR"]
    if not is_admin:
        # Filtrar apenas propostas do vendedor
        propostas = [p for p in propostas if p.vendedor_id == current_user.id]
    
    response_list = []
    for proposta in propostas:
        # Carregar relacionamentos se necessário
        if not proposta.produto:
            proposta_completa = crud_proposta.get_proposta_by_id(db, proposta.id, incluir_relacionamentos=True)
            if proposta_completa:
                proposta = proposta_completa
        response_list.append(_proposta_to_response(proposta))
    
    return response_list


@router.get("/admin/todas", response_model=List[schemas.PropostaDetalhadaResponse], summary="Lista todas as propostas (Admin)")
def get_all_propostas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    admin_user: models.Usuario = Depends(get_admin_user)
):
    """Lista todas as propostas do sistema. Apenas para administradores."""
    propostas = crud_proposta.get_all_propostas(db, skip=skip, limit=limit)
    
    response_list = []
    for proposta in propostas:
        # Carregar relacionamentos se necessário
        if not proposta.produto:
            proposta_completa = crud_proposta.get_proposta_by_id(db, proposta.id, incluir_relacionamentos=True)
            if proposta_completa:
                proposta = proposta_completa
        response_list.append(_proposta_to_response(proposta))
    
    return response_list


@router.post("/{proposta_id}/compartilhar", response_model=schemas.PropostaDetalhadaResponse, summary="Gera link compartilhável")
def compartilhar_proposta(
    proposta_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Gera token de compartilhamento para uma proposta"""
    proposta = crud_proposta.get_proposta_by_id(db, proposta_id)
    
    if not proposta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposta {proposta_id} não encontrada"
        )
    
    # Verificar permissão
    is_admin = current_user.perfil.upper() in ["ADMIN", "GESTOR"]
    if not is_admin and proposta.vendedor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para compartilhar esta proposta"
        )
    
    # Atualizar proposta para ser compartilhável
    import secrets
    proposta.compartilhavel = True
    proposta.token_compartilhamento = secrets.token_urlsafe(32)
    db.commit()
    db.refresh(proposta)
    
    # Carregar relacionamentos
    proposta_completa = crud_proposta.get_proposta_by_id(db, proposta.id, incluir_relacionamentos=True)
    if proposta_completa:
        proposta = proposta_completa
    
    return _proposta_to_response(proposta)


@router.get("/compartilhar/{token}", response_model=schemas.PropostaDetalhadaCompleta, summary="Visualiza proposta compartilhada")
def get_proposta_compartilhada(
    token: str,
    db: Session = Depends(get_db)
):
    """Visualiza uma proposta através do token de compartilhamento (público)"""
    proposta = crud_proposta.get_proposta_by_token(db, token)
    
    if not proposta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Proposta não encontrada ou link inválido"
        )
    
    # Buscar comparações
    comparacoes = []
    if proposta.rendimento_total_litros and proposta.custo_por_litro_final:
        comparacoes = crud_proposta.comparar_com_concorrentes(
            db,
            proposta.produto_id,
            proposta.rendimento_total_litros,
            proposta.custo_por_litro_final,
            proposta.produto.categoria if proposta.produto else None
        )
    
    # Montar resposta usando função auxiliar e converter para Completa
    response = _proposta_to_response(proposta, comparacoes)
    return schemas.PropostaDetalhadaCompleta(**response.model_dump())


@router.put("/{proposta_id}", response_model=schemas.PropostaDetalhadaResponse, summary="Atualiza proposta")
def update_proposta(
    proposta_id: int,
    proposta_update: schemas.PropostaDetalhadaUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza uma proposta detalhada"""
    proposta = crud_proposta.get_proposta_by_id(db, proposta_id)
    
    if not proposta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposta {proposta_id} não encontrada"
        )
    
    # Verificar permissão
    is_admin = current_user.perfil.upper() in ["ADMIN", "GESTOR"]
    if not is_admin and proposta.vendedor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para atualizar esta proposta"
        )
    
    proposta_atualizada = crud_proposta.update_proposta_detalhada(
        db, proposta_id, proposta_update
    )
    
    if not proposta_atualizada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Erro ao atualizar proposta {proposta_id}"
        )
    
    proposta_completa = crud_proposta.get_proposta_by_id(db, proposta_id, incluir_relacionamentos=True)
    
    if not proposta_completa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Erro ao atualizar proposta {proposta_id}"
        )
    
    return _proposta_to_response(proposta_completa)


@router.delete("/{proposta_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deleta proposta")
def delete_proposta(
    proposta_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Deleta uma proposta detalhada"""
    proposta = crud_proposta.get_proposta_by_id(db, proposta_id)
    
    if not proposta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposta {proposta_id} não encontrada"
        )
    
    # Verificar permissão
    is_admin = current_user.perfil.upper() in ["ADMIN", "GESTOR"]
    if not is_admin and proposta.vendedor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para deletar esta proposta"
        )
    
    sucesso = crud_proposta.delete_proposta_detalhada(db, proposta_id)
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Erro ao deletar proposta {proposta_id}"
        )

