# /backend/app/crud/orcamento.py

from sqlalchemy.orm import Session, joinedload
from typing import List

from app.db import models
from app.schemas import orcamento as schemas_orcamento

def create_orcamento(db: Session, orcamento_in: schemas_orcamento.OrcamentoCreate, vendedor_id: int) -> models.Orcamento:
    """Cria um novo orçamento com seus itens."""
    
    # 1. Cria o objeto principal do Orçamento
    db_orcamento = models.Orcamento(
        cliente_id=orcamento_in.cliente_id,
        usuario_id=vendedor_id,
        status=orcamento_in.status,
        condicao_pagamento=orcamento_in.condicao_pagamento
    )
    db.add(db_orcamento)
    db.flush()  # Isso é importante para obter o 'id' do orçamento antes do commit

    # 2. Itera sobre os itens recebidos e os adiciona ao banco, ligados ao orçamento
    for item_in in orcamento_in.itens:
        db_item = models.OrcamentoItem(
            orcamento_id=db_orcamento.id,
            produto_id=item_in.produto_id,
            quantidade=item_in.quantidade,
            # Este é o campo-chave: salva o preço que o vendedor definiu
            preco_unitario_congelado=item_in.preco_unitario
        )
        db.add(db_item)
    
    # 3. Salva todas as alterações no banco de dados
    db.commit()
    db.refresh(db_orcamento)
    return db_orcamento

def get_orcamentos_by_vendedor(db: Session, vendedor_id: int) -> List[models.Orcamento]:
    """
    Lista todos os orçamentos criados por um vendedor específico,
    trazendo junto os dados do cliente para exibição no histórico.
    """
    return db.query(models.Orcamento).options(
        joinedload(models.Orcamento.cliente),
        joinedload(models.Orcamento.itens).joinedload(models.OrcamentoItem.produto) # Carrega itens e produtos
    ).filter(models.Orcamento.usuario_id == vendedor_id).order_by(models.Orcamento.data_criacao.desc()).all()