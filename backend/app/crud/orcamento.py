# /backend/app/crud/orcamento.py - VERSÃO FINAL COM PROTEÇÃO

from sqlalchemy.orm import Session, joinedload
from typing import List

from app.db import models
from app.schemas import orcamento as schemas_orcamento

def create_orcamento(db: Session, orcamento_in: schemas_orcamento.OrcamentoCreate, vendedor_id: int) -> models.Orcamento:
    """Cria um novo orçamento com seus itens."""
    
    db_orcamento = models.Orcamento(
        cliente_id=orcamento_in.cliente_id,
        usuario_id=vendedor_id,
        status=orcamento_in.status,
        condicao_pagamento=orcamento_in.condicao_pagamento
    )
    db.add(db_orcamento)
    db.flush()

    for item_in in orcamento_in.itens:
        db_item = models.OrcamentoItem(
            orcamento_id=db_orcamento.id,
            produto_id=item_in.produto_id,
            quantidade=item_in.quantidade,
            preco_unitario_congelado=item_in.preco_unitario
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_orcamento)
    return db_orcamento

def get_orcamentos_by_vendedor(db: Session, vendedor_id: int) -> List[models.Orcamento]:
    """
    Lista todos os orçamentos criados por um vendedor específico,
    carregando os dados relacionados e IGNORANDO registros órfãos.
    """
    return db.query(models.Orcamento).options(
        joinedload(models.Orcamento.cliente),
        joinedload(models.Orcamento.usuario),
        joinedload(models.Orcamento.itens).joinedload(models.OrcamentoItem.produto)
    ).filter(
        models.Orcamento.usuario_id == vendedor_id,
        # ===== CORREÇÃO FINAL =====
        # Adiciona um filtro para garantir que o orçamento tenha um cliente.
        # Isso previne o erro 500 se houver dados inválidos no banco.
        models.Orcamento.cliente_id.isnot(None)
    ).order_by(
        models.Orcamento.data_criacao.desc()
    ).all()