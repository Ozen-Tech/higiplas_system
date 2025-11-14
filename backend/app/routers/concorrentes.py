# backend/app/routers/concorrentes.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.connection import get_db
from app.dependencies import get_current_user, get_admin_user
from app.db import models
from app.schemas import proposta_detalhada as schemas
from app.crud import concorrentes as crud_concorrentes

router = APIRouter(
    prefix="/concorrentes",
    tags=["Concorrentes"]
)


@router.get("/", response_model=List[schemas.ProdutoConcorrente], summary="Lista concorrentes")
def get_concorrentes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    categoria: Optional[str] = Query(None),
    ativo: Optional[bool] = Query(True),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista produtos concorrentes com filtros opcionais"""
    return crud_concorrentes.get_concorrentes(
        db, skip=skip, limit=limit, categoria=categoria, ativo=ativo
    )


@router.get("/{concorrente_id}", response_model=schemas.ProdutoConcorrente, summary="Busca concorrente por ID")
def get_concorrente_by_id(
    concorrente_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Busca um concorrente específico por ID"""
    concorrente = crud_concorrentes.get_concorrente_by_id(db, concorrente_id)
    if not concorrente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concorrente {concorrente_id} não encontrado"
        )
    return concorrente


@router.get("/categoria/{categoria}", response_model=List[schemas.ProdutoConcorrente], summary="Lista concorrentes por categoria")
def get_concorrentes_por_categoria(
    categoria: str,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista concorrentes de uma categoria específica"""
    return crud_concorrentes.get_concorrentes_por_categoria(db, categoria)


@router.post("/", response_model=schemas.ProdutoConcorrente, status_code=status.HTTP_201_CREATED, summary="Cria concorrente (Admin)")
def create_concorrente(
    concorrente_in: schemas.ProdutoConcorrenteCreate,
    db: Session = Depends(get_db),
    admin_user: models.Usuario = Depends(get_admin_user)
):
    """Cria um novo produto concorrente. Apenas para administradores."""
    return crud_concorrentes.create_concorrente(db, concorrente_in)


@router.put("/{concorrente_id}", response_model=schemas.ProdutoConcorrente, summary="Atualiza concorrente (Admin)")
def update_concorrente(
    concorrente_id: int,
    concorrente_update: schemas.ProdutoConcorrenteUpdate,
    db: Session = Depends(get_db),
    admin_user: models.Usuario = Depends(get_admin_user)
):
    """Atualiza um concorrente. Apenas para administradores."""
    concorrente = crud_concorrentes.update_concorrente(db, concorrente_id, concorrente_update)
    if not concorrente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concorrente {concorrente_id} não encontrado"
        )
    return concorrente


@router.delete("/{concorrente_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deleta concorrente (Admin)")
def delete_concorrente(
    concorrente_id: int,
    db: Session = Depends(get_db),
    admin_user: models.Usuario = Depends(get_admin_user)
):
    """Deleta (desativa) um concorrente. Apenas para administradores."""
    sucesso = crud_concorrentes.delete_concorrente(db, concorrente_id)
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Concorrente {concorrente_id} não encontrado"
        )

