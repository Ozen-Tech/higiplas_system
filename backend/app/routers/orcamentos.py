# /backend/app/routers/orcamentos.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.connection import get_db
from app.db import models
from app.dependencies import get_current_user
from ..crud import orcamento as crud_orcamento
from ..schemas import orcamento as schemas_orcamento
from ..schemas import produtos_mais_vendidos as schemas_produtos_vendidos

router = APIRouter(
    prefix="/orcamentos",
    tags=["Orçamentos"],
)

@router.post("/", response_model=schemas_orcamento.Orcamento, status_code=201)
@router.post("", response_model=schemas_orcamento.Orcamento, status_code=201)  # Rota sem barra final
def create_new_orcamento(
    orcamento: schemas_orcamento.OrcamentoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    return crud_orcamento.create_orcamento(
        db=db, 
        orcamento=orcamento, 
        usuario_id=current_user.id,
        empresa_id=current_user.empresa_id
    )

@router.get("/", response_model=List[schemas_orcamento.Orcamento], summary="Lista os orçamentos do usuário logado")
@router.get("", response_model=List[schemas_orcamento.Orcamento], summary="Lista os orçamentos do usuário logado")
def read_user_orcamentos(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Retorna uma lista de todos os orçamentos criados pelo vendedor logado."""
    try:
        return crud_orcamento.get_orcamentos_by_user(db=db, usuario_id=current_user.id)
    except Exception as e:
        import traceback
        print(f"Erro ao buscar orçamentos: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno ao buscar orçamentos: {str(e)}"
        )

@router.get("/{orcamento_id}", response_model=schemas_orcamento.Orcamento, summary="Busca um orçamento específico")
def read_one_orcamento(
    orcamento_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Retorna os dados de um orçamento específico, se ele pertencer ao usuário logado."""
    orcamento = crud_orcamento.get_orcamento_by_id(db=db, orcamento_id=orcamento_id, usuario_id=current_user.id)
    if not orcamento:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado ou não pertence a este usuário.")
    return orcamento

@router.put("/{orcamento_id}", response_model=schemas_orcamento.Orcamento)
@router.put("/{orcamento_id}/", response_model=schemas_orcamento.Orcamento)  # Rota com barra final
def update_orcamento(
    orcamento_id: int,
    orcamento_update: schemas_orcamento.OrcamentoUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza um orçamento existente."""
    return crud_orcamento.update_orcamento(
        db=db,
        orcamento_id=orcamento_id,
        orcamento_update=orcamento_update,
        usuario_id=current_user.id,
        empresa_id=current_user.empresa_id
    )

@router.delete("/{orcamento_id}")
@router.delete("/{orcamento_id}/")  # Rota com barra final
def delete_orcamento(
    orcamento_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Exclui um orçamento (apenas se não estiver finalizado)."""
    return crud_orcamento.delete_orcamento(
        db=db,
        orcamento_id=orcamento_id,
        usuario_id=current_user.id,
        empresa_id=current_user.empresa_id
    )

# --- NOVA ROTA PARA FINALIZAR UM ORÇAMENTO ---
@router.post("/{orcamento_id}/finalizar", response_model=schemas_orcamento.Orcamento, summary="Finaliza um orçamento e dá baixa no estoque")
def finalizar_orcamento_endpoint(
    orcamento_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Muda o status de um orçamento para 'FINALIZADO' e realiza a baixa
    no estoque para cada item do orçamento.
    """
    try:
        orcamento_finalizado = crud_orcamento.finalizar_orcamento(
            db=db,
            orcamento_id=orcamento_id,
            usuario_id=current_user.id,
            empresa_id=current_user.empresa_id
        )
        return orcamento_finalizado
    except HTTPException as e:
        # Repassa exceções de negócio (ex: estoque insuficiente) para o cliente
        raise e
    except Exception as e:
        # Captura erros inesperados
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno no servidor: {e}")

@router.post("/{orcamento_id}/finalizar-com-nf", response_model=schemas_orcamento.Orcamento)
def finalizar_orcamento_com_nf(
    orcamento_id: int,
    numero_nf: str,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Finaliza um orçamento com número da NF."""
    try:
        return crud_orcamento.finalizar_orcamento_com_nf(
            db=db,
            orcamento_id=orcamento_id,
            numero_nf=numero_nf,
            usuario_id=current_user.id,
            empresa_id=current_user.empresa_id
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro interno no servidor: {e}")

# Rotas para dashboard de admins
@router.get("/empresa/todos", response_model=List[schemas_orcamento.Orcamento])
def get_orcamentos_empresa(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todos os orçamentos da empresa (para dashboard de admins)."""
    # Verificar se o usuário é admin poderia ser adicionado aqui
    return crud_orcamento.get_orcamentos_by_empresa(
        db=db,
        empresa_id=current_user.empresa_id,
        skip=skip,
        limit=limit
    )

@router.get("/empresa/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Retorna estatísticas para o dashboard de admins."""
    return crud_orcamento.get_dashboard_stats(db=db, empresa_id=current_user.empresa_id)

@router.get("/produtos-mais-vendidos", response_model=List[schemas_produtos_vendidos.ProdutoVendidoDetalhado])
def get_produtos_mais_vendidos(
    ano: int = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Retorna os produtos mais vendidos do ano."""
    return crud_orcamento.get_produtos_mais_vendidos(
        db=db,
        empresa_id=current_user.empresa_id,
        ano=ano,
        limit=limit
    )