# /backend/app/routers/orcamentos.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.connection import get_db
from app.db import models
from app.dependencies import get_current_user
from app.crud import orcamento as crud_orcamento
from app.schemas import orcamento as schemas_orcamento

router = APIRouter(
    prefix="/orcamentos",
    tags=["Orçamentos"],
)

@router.post("/", response_model=schemas_orcamento.Orcamento, status_code=201)
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
def read_user_orcamentos(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Retorna uma lista de todos os orçamentos criados pelo vendedor logado."""
    return crud_orcamento.get_orcamentos_by_user(db=db, usuario_id=current_user.id)

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