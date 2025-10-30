from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from ..schemas import movimentacao_estoque as schemas_movimentacao
from ..db import models
from datetime import datetime, timedelta
from ..services.stock_service import StockService
from ..core.logger import stock_operations_logger


def create_movimentacao_estoque(db: Session, movimentacao: schemas_movimentacao.MovimentacaoEstoqueCreate, usuario_id: int, empresa_id: int):
    origem = getattr(movimentacao, 'origem', None)
    
    produto_atualizado = StockService.update_stock_transactionally(
        db=db,
        produto_id=movimentacao.produto_id,
        quantidade=movimentacao.quantidade,
        tipo_movimentacao=movimentacao.tipo_movimentacao,
        usuario_id=usuario_id,
        empresa_id=empresa_id,
        origem=origem,
        observacao=movimentacao.observacao
    )
    
    return produto_atualizado

def get_movimentacoes_by_produto_id(db: Session, produto_id: int, empresa_id: int):
    produto = db.query(models.Produto).filter(models.Produto.id == produto_id, models.Produto.empresa_id == empresa_id).first()
    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado ou não pertence à sua empresa.")

    return db.query(models.MovimentacaoEstoque).options(
            joinedload(models.MovimentacaoEstoque.usuario)
        ).filter(
            models.MovimentacaoEstoque.produto_id == produto_id
        ).order_by(
            models.MovimentacaoEstoque.data_movimentacao.desc()
        ).all()

def get_recent_movimentacoes(db: Session, empresa_id: int, days: int = 30):
    data_limite = datetime.now() - timedelta(days=days)

    return db.query(models.MovimentacaoEstoque).join(
        models.Produto, models.MovimentacaoEstoque.produto_id == models.Produto.id
    ).join(
        models.Usuario, models.MovimentacaoEstoque.usuario_id == models.Usuario.id
    ).filter(
        models.Produto.empresa_id == empresa_id,
        models.MovimentacaoEstoque.data_movimentacao >= data_limite
    ).options(
        joinedload(models.MovimentacaoEstoque.produto),
        joinedload(models.MovimentacaoEstoque.usuario)
    ).order_by(
        models.MovimentacaoEstoque.data_movimentacao.desc()
    ).all()
