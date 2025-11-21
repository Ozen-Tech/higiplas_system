from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from ..schemas import movimentacao_estoque as schemas_movimentacao
from ..db import models
from datetime import datetime, timedelta
from typing import List, Optional
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

def create_pending_movimentacao(
    db: Session, 
    movimentacao: schemas_movimentacao.MovimentacaoEstoquePendenteCreate, 
    usuario_id: int, 
    empresa_id: int
) -> models.MovimentacaoEstoque:
    """Cria uma movimentação pendente sem alterar o estoque."""
    return StockService.create_pending_movimentacao(
        db=db,
        produto_id=movimentacao.produto_id,
        quantidade=movimentacao.quantidade,
        tipo_movimentacao=movimentacao.tipo_movimentacao,
        usuario_id=usuario_id,
        empresa_id=empresa_id,
        motivo_movimentacao=movimentacao.motivo_movimentacao,
        observacao=movimentacao.observacao,
        observacao_motivo=movimentacao.observacao_motivo
    )

def get_pending_movimentacoes(
    db: Session, 
    empresa_id: int,
    status_filter: Optional[str] = None
) -> List[models.MovimentacaoEstoque]:
    """Lista todas as movimentações pendentes da empresa."""
    query = db.query(models.MovimentacaoEstoque).join(
        models.Produto
    ).filter(
        models.Produto.empresa_id == empresa_id
    ).options(
        joinedload(models.MovimentacaoEstoque.produto),
        joinedload(models.MovimentacaoEstoque.usuario),
        joinedload(models.MovimentacaoEstoque.aprovado_por)
    )
    
    if status_filter:
        query = query.filter(models.MovimentacaoEstoque.status == status_filter)
    else:
        query = query.filter(models.MovimentacaoEstoque.status == 'PENDENTE')
    
    return query.order_by(
        models.MovimentacaoEstoque.data_movimentacao.desc()
    ).all()

def get_pending_movimentacoes_by_user(
    db: Session, 
    usuario_id: int,
    empresa_id: int,
    status_filter: Optional[str] = None
) -> List[models.MovimentacaoEstoque]:
    """Lista movimentações pendentes do usuário."""
    query = db.query(models.MovimentacaoEstoque).join(
        models.Produto
    ).filter(
        models.MovimentacaoEstoque.usuario_id == usuario_id,
        models.Produto.empresa_id == empresa_id
    ).options(
        joinedload(models.MovimentacaoEstoque.produto),
        joinedload(models.MovimentacaoEstoque.usuario),
        joinedload(models.MovimentacaoEstoque.aprovado_por)
    )
    
    if status_filter:
        query = query.filter(models.MovimentacaoEstoque.status == status_filter)
    else:
        # Por padrão, mostra todas (pendentes, confirmadas e rejeitadas)
        pass
    
    return query.order_by(
        models.MovimentacaoEstoque.data_movimentacao.desc()
    ).all()

def confirm_movimentacao(
    db: Session,
    movimentacao_id: int,
    aprovado_por_id: int,
    empresa_id: int
) -> models.Produto:
    """Confirma uma movimentação pendente e aplica ao estoque."""
    return StockService.confirm_movimentacao(
        db=db,
        movimentacao_id=movimentacao_id,
        aprovado_por_id=aprovado_por_id,
        empresa_id=empresa_id
    )

def edit_movimentacao(
    db: Session,
    movimentacao_id: int,
    aprovado_por_id: int,
    empresa_id: int,
    edicao: schemas_movimentacao.MovimentacaoEstoqueEdicao
) -> models.Produto:
    """Edita uma movimentação pendente e confirma aplicando ao estoque."""
    from ..schemas.movimentacao_estoque import MotivoMovimentacao
    
    return StockService.edit_and_confirm_movimentacao(
        db=db,
        movimentacao_id=movimentacao_id,
        aprovado_por_id=aprovado_por_id,
        empresa_id=empresa_id,
        produto_id=edicao.produto_id,
        quantidade=edicao.quantidade,
        tipo_movimentacao=edicao.tipo_movimentacao,
        motivo_movimentacao=edicao.motivo_movimentacao,
        observacao=edicao.observacao,
        observacao_motivo=edicao.observacao_motivo
    )

def reject_movimentacao(
    db: Session,
    movimentacao_id: int,
    aprovado_por_id: int,
    motivo_rejeicao: str,
    empresa_id: int
) -> models.MovimentacaoEstoque:
    """Rejeita uma movimentação pendente sem alterar o estoque."""
    return StockService.reject_movimentacao(
        db=db,
        movimentacao_id=movimentacao_id,
        aprovado_por_id=aprovado_por_id,
        motivo_rejeicao=motivo_rejeicao,
        empresa_id=empresa_id
    )
