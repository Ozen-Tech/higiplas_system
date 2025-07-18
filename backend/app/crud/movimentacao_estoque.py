from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from ..schemas import movimentacao_estoque as schemas_movimentacao
from ..db import models
from datetime import datetime, timedelta


def create_movimentacao_estoque(db: Session, movimentacao: schemas_movimentacao.MovimentacaoEstoqueCreate, usuario_id: int, empresa_id: int):
    """
    Cria uma movimentação de estoque e atualiza a quantidade do produto de forma atômica.
    """
    # 1. Buscar o produto com um bloqueio de linha para evitar race conditions
    # O .with_for_update() garante que nenhuma outra transação possa modificar esta linha até o commit.
    db_produto = db.query(models.Produto).with_for_update().filter(
        models.Produto.id == movimentacao.produto_id,
        models.Produto.empresa_id == empresa_id
    ).first()

    if not db_produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado ou não pertence à sua empresa.")

    # 2. Validar a operação e calcular o novo estoque
    if movimentacao.tipo_movimentacao == 'SAIDA':
        if db_produto.quantidade_em_estoque < movimentacao.quantidade:
            # Não precisamos de rollback manual, o SQLAlchemy cuida disso se uma exceção for levantada
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estoque insuficiente para a saída.")
        db_produto.quantidade_em_estoque -= movimentacao.quantidade
    else:  # 'ENTRADA'
        db_produto.quantidade_em_estoque += movimentacao.quantidade

    # 3. Criar o registro da movimentação
    db_movimentacao = models.MovimentacaoEstoque(
        produto_id=movimentacao.produto_id,
        tipo_movimentacao=movimentacao.tipo_movimentacao,
        quantidade=movimentacao.quantidade,
        observacao=movimentacao.observacao,
        usuario_id=usuario_id
    )

    # Adiciona ambos os objetos (o produto atualizado e a nova movimentação) à sessão
    db.add(db_movimentacao)
    
    # Comita a transação. Se qualquer passo falhar, nada é salvo.
    db.commit()
    
    # Atualiza o objeto produto com os dados do banco (garante que temos o valor mais recente)
    db.refresh(db_produto)
    
    return db_produto

def get_movimentacoes_by_produto_id(db: Session, produto_id: int, empresa_id: int):
    """
    Busca o histórico de movimentações de um produto específico.
    """
    # Verifica se o produto pertence à empresa do usuário antes de retornar as movimentações
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
    """
    Busca todas as movimentações de uma empresa nos últimos X dias.
    Faz join com Produto e Usuário para obter seus nomes.
    """
    # Calcula a data de início do período
    data_limite = datetime.now() - timedelta(days=days)

    # A query faz join em 'Produto' e 'Usuario' para enriquecer os dados
    return db.query(models.MovimentacaoEstoque).join(
        models.Produto, models.MovimentacaoEstoque.produto_id == models.Produto.id
    ).join(
        models.Usuario, models.MovimentacaoEstoque.usuario_id == models.Usuario.id
    ).filter(
        models.Produto.empresa_id == empresa_id,
        models.MovimentacaoEstoque.data_movimentacao >= data_limite
    ).options(
        # Eager load para evitar múltiplas queries
        joinedload(models.MovimentacaoEstoque.produto),
        joinedload(models.MovimentacaoEstoque.usuario)
    ).order_by(
        models.MovimentacaoEstoque.data_movimentacao.desc()
    ).all()