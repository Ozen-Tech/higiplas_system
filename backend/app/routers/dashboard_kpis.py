# /backend/app/routers/dashboard_kpis.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.connection import get_db
from app.db import models
from app.dependencies import get_current_user

router = APIRouter(prefix="/kpis", tags=["Dashboard KPIs"])

@router.get("/")
def get_dashboard_kpis(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    empresa_id = current_user.empresa_id

    total_produtos = db.query(func.count(models.Produto.id)).filter(models.Produto.empresa_id == empresa_id).scalar()
    
    produtos_baixo_estoque = db.query(func.count(models.Produto.id)).filter(
        models.Produto.empresa_id == empresa_id,
        models.Produto.quantidade_em_estoque <= models.Produto.estoque_minimo
    ).scalar()

    valor_total_estoque = db.query(func.sum(models.Produto.quantidade_em_estoque * models.Produto.preco_custo)).filter(
        models.Produto.empresa_id == empresa_id,
        models.Produto.preco_custo.isnot(None) # Garante que só somamos produtos com custo
    ).scalar() or 0

    return {
        "total_produtos": total_produtos,
        "produtos_baixo_estoque": produtos_baixo_estoque,
        "valor_total_estoque": round(valor_total_estoque, 2)
    }