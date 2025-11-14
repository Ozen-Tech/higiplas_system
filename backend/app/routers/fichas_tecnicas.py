# backend/app/routers/fichas_tecnicas.py

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import tempfile

from app.db.connection import get_db
from app.dependencies import get_current_user, get_admin_user
from app.db import models
from app.schemas import proposta_detalhada as schemas
from app.crud import ficha_tecnica as crud_ficha
from app.services.ficha_tecnica_service import ficha_tecnica_service
from app.core.logger import app_logger

logger = app_logger

router = APIRouter(
    prefix="/fichas-tecnicas",
    tags=["Fichas Técnicas"]
)


@router.post("/processar-pasta", response_model=List[schemas.FichaTecnica], summary="Processa pasta de PDFs (Admin)")
def processar_pasta_pdfs(
    pasta: str,
    db: Session = Depends(get_db),
    admin_user: models.Usuario = Depends(get_admin_user)
):
    """
    Processa todos os PDFs de uma pasta e cria fichas técnicas.
    Apenas para administradores.
    """
    try:
        if not os.path.isdir(pasta):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Pasta não encontrada: {pasta}"
            )
        
        # Processar PDFs
        dados_pdfs = ficha_tecnica_service.processar_pasta_pdfs(pasta)
        
        # Criar fichas técnicas no banco
        fichas_criadas = []
        for dados in dados_pdfs:
            try:
                ficha_create = schemas.FichaTecnicaCreate(**dados)
                ficha = crud_ficha.create_ficha_tecnica(db, ficha_create)
                fichas_criadas.append(ficha)
            except Exception as e:
                logger.error(f"Erro ao criar ficha técnica para {dados.get('nome_produto')}: {e}")
                continue
        
        return fichas_criadas
        
    except Exception as e:
        logger.error(f"Erro ao processar pasta: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar pasta: {str(e)}"
        )


@router.post("/processar-pdf", response_model=schemas.FichaTecnica, summary="Processa um PDF (Admin)")
def processar_pdf(
    pdf_path: str,
    produto_id: int = None,
    db: Session = Depends(get_db),
    admin_user: models.Usuario = Depends(get_admin_user)
):
    """
    Processa um PDF de ficha técnica e cria/atualiza registro.
    Apenas para administradores.
    """
    try:
        ficha = crud_ficha.processar_pdf_ficha_tecnica(db, pdf_path, produto_id)
        return ficha
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Erro ao processar PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar PDF: {str(e)}"
        )


@router.get("/produto/{produto_id}", response_model=schemas.FichaTecnica, summary="Busca ficha técnica do produto")
def get_ficha_by_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Busca ficha técnica de um produto específico"""
    ficha = crud_ficha.get_ficha_by_produto(db, produto_id)
    if not ficha:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ficha técnica não encontrada para o produto {produto_id}"
        )
    return ficha


@router.get("/", response_model=List[schemas.FichaTecnica], summary="Lista todas as fichas técnicas")
def get_all_fichas(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todas as fichas técnicas cadastradas"""
    return crud_ficha.get_all_fichas(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.FichaTecnica, status_code=status.HTTP_201_CREATED, summary="Cria ficha técnica (Admin)")
def create_ficha_tecnica(
    ficha_in: schemas.FichaTecnicaCreate,
    db: Session = Depends(get_db),
    admin_user: models.Usuario = Depends(get_admin_user)
):
    """Cria uma nova ficha técnica manualmente. Apenas para administradores."""
    return crud_ficha.create_ficha_tecnica(db, ficha_in)


@router.put("/{ficha_id}", response_model=schemas.FichaTecnica, summary="Atualiza ficha técnica (Admin)")
def update_ficha_tecnica(
    ficha_id: int,
    ficha_update: schemas.FichaTecnicaUpdate,
    db: Session = Depends(get_db),
    admin_user: models.Usuario = Depends(get_admin_user)
):
    """Atualiza uma ficha técnica. Apenas para administradores."""
    ficha = crud_ficha.update_ficha_tecnica(db, ficha_id, ficha_update)
    if not ficha:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ficha técnica {ficha_id} não encontrada"
        )
    return ficha


@router.delete("/{ficha_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Deleta ficha técnica (Admin)")
def delete_ficha_tecnica(
    ficha_id: int,
    db: Session = Depends(get_db),
    admin_user: models.Usuario = Depends(get_admin_user)
):
    """Deleta uma ficha técnica. Apenas para administradores."""
    sucesso = crud_ficha.delete_ficha_tecnica(db, ficha_id)
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ficha técnica {ficha_id} não encontrada"
        )

