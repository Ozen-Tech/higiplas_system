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