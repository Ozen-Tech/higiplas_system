# /backend/app/routers/invoice_processing.py
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.db import models
from app.dependencies import get_current_user

router = APIRouter(prefix="/invoices", tags=["Processamento de Notas Fiscais"])


@router.post("/parse-and-match", summary="Extrai produtos de uma NF-e (imagem) - recurso desativado")
async def parse_invoice_and_match_products(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Extração por imagem foi desativada. Use PDF ou XML de NF-e nas rotas de movimentações."""
    raise HTTPException(
        status_code=410,
        detail="Extração por imagem desativada. Use o processamento de PDF ou XML de NF-e nas movimentações."
    )