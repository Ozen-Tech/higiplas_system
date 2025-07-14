from sqlalchemy.orm import Session
from sqlalchemy import desc # Para ordenar de forma decrescente

from ..db import models

# Função 1: Pegar os 10 produtos com maior quantidade vendida
def get_top_10_vendas(db: Session):
    """
    Busca os 10 registros de vendas históricas com a maior quantidade vendida.
    """
    return db.query(models.VendaHistorica).order_by(
        desc(models.VendaHistorica.quantidade_vendida_total)
    ).limit(10).all()

# Função 2: Pegar o histórico de um produto específico (você pode usar no futuro)
def get_historico_venda_por_descricao(db: Session, descricao: str) -> models.VendaHistorica | None:
    """
    Busca o registro de venda histórica de um produto específico pela sua descrição.
    """
    return db.query(models.VendaHistorica).filter(
        models.VendaHistorica.descricao.ilike(f"%{descricao}%")
    ).first()

# Função 3 (Opcional, mas útil): Pegar os 10 produtos mais lucrativos
def get_top_10_lucro(db: Session):
    """
    Busca os 10 registros de vendas históricas com o maior lucro bruto.
    """
    return db.query(models.VendaHistorica).order_by(
        desc(models.VendaHistorica.lucro_bruto_total)
    ).limit(10).all()