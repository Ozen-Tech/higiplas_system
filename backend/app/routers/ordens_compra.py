from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..db.connection import get_db
from ..dependencies import get_current_user
from ..db import models
from ..crud import ordem_compra as crud_oc
from ..schemas import ordem_compra as schemas_oc

router = APIRouter(prefix="/ordens-compra", tags=["Ordens de Compra"])

@router.post("/", response_model=schemas_oc.OrdemDeCompra, status_code=201)
def create_new_ordem_compra(ordem: schemas_oc.OrdemDeCompraCreate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    return crud_oc.create_ordem_compra(db=db, ordem_in=ordem, usuario_id=current_user.id)

@router.get("/", response_model=List[schemas_oc.OrdemDeCompra])
def read_ordens_compra(db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    return crud_oc.get_ordens_compra(db=db, empresa_id=current_user.empresa_id)

@router.put("/{ordem_id}/receber", response_model=schemas_oc.OrdemDeCompra)
def receive_ordem_compra(ordem_id: int, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    return crud_oc.receber_ordem_compra(db=db, ordem_id=ordem_id, usuario_id=current_user.id, empresa_id=current_user.empresa_id)