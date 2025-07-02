# backend/app/crud/movimentacao_estoque.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..schemas import movimentacao_estoque as schemas_movimentacao
from ..db import models

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

    return db.query(models.MovimentacaoEstoque).filter(models.MovimentacaoEstoque.produto_id == produto_id).order_by(models.MovimentacaoEstoque.data_movimentacao.desc()).all()