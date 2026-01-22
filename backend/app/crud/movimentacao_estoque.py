from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text, inspect
from fastapi import HTTPException, status
from ..schemas import movimentacao_estoque as schemas_movimentacao
from ..db import models
from ..db.connection import engine
from datetime import datetime, timedelta
from typing import List, Optional
from ..services.stock_service import StockService
from ..core.logger import stock_operations_logger
import logging

logger = logging.getLogger(__name__)


def create_movimentacao_estoque(db: Session, movimentacao: schemas_movimentacao.MovimentacaoEstoqueCreate, usuario_id: int, empresa_id: int):
    origem = getattr(movimentacao, 'origem', None)
    motivo_movimentacao = getattr(movimentacao, 'motivo_movimentacao', None)
    observacao_motivo = getattr(movimentacao, 'observacao_motivo', None)
    
    produto_atualizado = StockService.update_stock_transactionally(
        db=db,
        produto_id=movimentacao.produto_id,
        quantidade=movimentacao.quantidade,
        tipo_movimentacao=movimentacao.tipo_movimentacao,
        usuario_id=usuario_id,
        empresa_id=empresa_id,
        origem=origem,
        observacao=movimentacao.observacao,
        motivo_movimentacao=motivo_movimentacao,
        observacao_motivo=observacao_motivo
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
    
    # Verificar se as colunas de reversão existem
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('movimentacoes_estoque')]
        colunas_reversao_existem = 'reversao_de_id' in columns
    except Exception as e:
        logger.warning(f"⚠️ Erro ao verificar colunas: {e}. Assumindo que não existem.")
        colunas_reversao_existem = False
    
    # Se as colunas não existem, usar query SQL direta
    if not colunas_reversao_existem:
        sql_query = text("""
            SELECT 
                me.id, me.tipo_movimentacao, me.quantidade, me.observacao,
                me.data_movimentacao, me.origem, me.quantidade_antes, me.quantidade_depois,
                me.status, me.aprovado_por_id, me.data_aprovacao, me.motivo_rejeicao,
                me.motivo_movimentacao, me.observacao_motivo, me.dados_antes_edicao,
                me.dados_depois_edicao, me.produto_id, me.usuario_id
            FROM movimentacoes_estoque me
            JOIN produtos p ON p.id = me.produto_id
            WHERE p.empresa_id = :empresa_id AND me.data_movimentacao >= :data_limite
            ORDER BY me.data_movimentacao DESC
        """)
        
        result = db.execute(sql_query, {'empresa_id': empresa_id, 'data_limite': data_limite})
        rows = result.fetchall()
        
        # Converter para objetos MovimentacaoEstoque
        movimentacoes = []
        for row in rows:
            mov = models.MovimentacaoEstoque()
            mov.id = row[0]
            mov.tipo_movimentacao = row[1]
            mov.quantidade = row[2]
            mov.observacao = row[3]
            mov.data_movimentacao = row[4]
            mov.origem = row[5]
            mov.quantidade_antes = row[6]
            mov.quantidade_depois = row[7]
            mov.status = row[8]
            mov.aprovado_por_id = row[9]
            mov.data_aprovacao = row[10]
            mov.motivo_rejeicao = row[11]
            mov.motivo_movimentacao = row[12]
            mov.observacao_motivo = row[13]
            mov.dados_antes_edicao = row[14]
            mov.dados_depois_edicao = row[15]
            mov.produto_id = row[16]
            mov.usuario_id = row[17]
            mov.revertida = False
            mov.reversao_de_id = None
            mov.data_reversao = None
            mov.revertida_por_id = None
            
            # Carregar produto e usuário
            mov.produto = db.query(models.Produto).filter(models.Produto.id == mov.produto_id).first()
            mov.usuario = db.query(models.Usuario).filter(models.Usuario.id == mov.usuario_id).first()
            
            movimentacoes.append(mov)
        
        return movimentacoes
    
    # Query normal usando ORM quando as colunas existem
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

def edit_pending_movimentacao(
    db: Session,
    movimentacao_id: int,
    empresa_id: int,
    edicao: schemas_movimentacao.MovimentacaoEstoqueEdicao
) -> models.MovimentacaoEstoque:
    """Edita uma movimentação pendente SEM confirmar (não altera o estoque)."""
    from ..schemas.movimentacao_estoque import MotivoMovimentacao
    
    return StockService.edit_pending_movimentacao(
        db=db,
        movimentacao_id=movimentacao_id,
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
