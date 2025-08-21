from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..db.connection import get_db
from ..dependencies import get_current_user
from ..db import models
from ..crud import fornecedor as crud_fornecedor
from ..schemas import fornecedor as schemas_fornecedor

router = APIRouter(prefix="/fornecedores", tags=["Fornecedores"])

@router.get("/", response_model=List[schemas_fornecedor.Fornecedor])
def read_fornecedores(db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    try:
        return crud_fornecedor.get_fornecedores(db=db, empresa_id=current_user.empresa_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao buscar fornecedores: {str(e)}")

@router.post("/", response_model=schemas_fornecedor.Fornecedor, status_code=201)
def create_new_fornecedor(fornecedor: schemas_fornecedor.FornecedorCreate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    try:
        return crud_fornecedor.create_fornecedor(db=db, fornecedor=fornecedor, empresa_id=current_user.empresa_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao criar fornecedor: {str(e)}")