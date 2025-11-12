# /backend/app/crud/orcamento.py - VERSÃO FINAL COM PROTEÇÃO

from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from fastapi import HTTPException, status

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

def get_all_orcamentos(db: Session, empresa_id: Optional[int] = None) -> List[models.Orcamento]:
    """
    Lista todos os orçamentos do sistema (apenas para admin).
    Se empresa_id for fornecido, filtra por empresa.
    """
    query = db.query(models.Orcamento).options(
        joinedload(models.Orcamento.cliente),
        joinedload(models.Orcamento.usuario),
        joinedload(models.Orcamento.itens).joinedload(models.OrcamentoItem.produto)
    ).filter(
        models.Orcamento.cliente_id.isnot(None)
    )
    
    if empresa_id:
        query = query.join(models.Usuario).filter(
            models.Usuario.empresa_id == empresa_id
        )
    
    return query.order_by(
        models.Orcamento.data_criacao.desc()
    ).all()

def get_orcamento_by_id(db: Session, orcamento_id: int) -> Optional[models.Orcamento]:
    """
    Busca um orçamento específico por ID com todos os dados relacionados.
    """
    return db.query(models.Orcamento).options(
        joinedload(models.Orcamento.cliente),
        joinedload(models.Orcamento.usuario),
        joinedload(models.Orcamento.itens).joinedload(models.OrcamentoItem.produto)
    ).filter(
        models.Orcamento.id == orcamento_id
    ).first()

def update_orcamento(
    db: Session,
    orcamento_id: int,
    orcamento_update: schemas_orcamento.OrcamentoUpdate
) -> models.Orcamento:
    """
    Atualiza um orçamento existente (apenas admin).
    Permite atualizar cliente, condição de pagamento, status e itens.
    """
    db_orcamento = db.query(models.Orcamento).filter(
        models.Orcamento.id == orcamento_id
    ).first()
    
    if not db_orcamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orçamento não encontrado"
        )
    
    # Atualizar campos básicos
    if orcamento_update.cliente_id is not None:
        db_orcamento.cliente_id = orcamento_update.cliente_id
    if orcamento_update.condicao_pagamento is not None:
        db_orcamento.condicao_pagamento = orcamento_update.condicao_pagamento
    if orcamento_update.status is not None:
        db_orcamento.status = orcamento_update.status
    
    # Atualizar itens se fornecidos
    if orcamento_update.itens is not None:
        # Remover itens antigos
        for item in db_orcamento.itens:
            db.delete(item)
        
        # Adicionar novos itens
        for item_update in orcamento_update.itens:
            db_item = models.OrcamentoItem(
                orcamento_id=db_orcamento.id,
                produto_id=item_update.produto_id,
                quantidade=item_update.quantidade,
                preco_unitario_congelado=item_update.preco_unitario
            )
            db.add(db_item)
    
    db.commit()
    db.refresh(db_orcamento)
    
    # Retornar com dados completos
    return get_orcamento_by_id(db, orcamento_id)

def update_orcamento_status(
    db: Session,
    orcamento_id: int,
    novo_status: str
) -> models.Orcamento:
    """
    Atualiza apenas o status de um orçamento.
    """
    db_orcamento = db.query(models.Orcamento).filter(
        models.Orcamento.id == orcamento_id
    ).first()
    
    if not db_orcamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orçamento não encontrado"
        )
    
    db_orcamento.status = novo_status
    db.commit()
    db.refresh(db_orcamento)
    
    return get_orcamento_by_id(db, orcamento_id)

def confirmar_orcamento(
    db: Session,
    orcamento_id: int,
    usuario_id: int,
    empresa_id: int
) -> models.Orcamento:
    """
    Confirma um orçamento e dá baixa no estoque dos produtos.
    Valida estoque disponível antes de processar.
    """
    from app.services.stock_service import StockService
    
    db_orcamento = get_orcamento_by_id(db, orcamento_id)
    
    if not db_orcamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orçamento não encontrado"
        )
    
    # Validar que o orçamento está em um status que pode ser confirmado
    if db_orcamento.status not in ['ENVIADO', 'APROVADO']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Orçamento com status '{db_orcamento.status}' não pode ser confirmado. Apenas orçamentos ENVIADO ou APROVADO podem ser confirmados."
        )
    
    # Validar estoque disponível antes de processar
    produtos_insuficientes = []
    for item in db_orcamento.itens:
        produto = item.produto
        if produto.quantidade_em_estoque < item.quantidade:
            produtos_insuficientes.append({
                'produto': produto.nome,
                'disponivel': produto.quantidade_em_estoque,
                'solicitado': item.quantidade
            })
    
    if produtos_insuficientes:
        detalhes = ", ".join([
            f"{p['produto']} (disponível: {p['disponivel']}, solicitado: {p['solicitado']})"
            for p in produtos_insuficientes
        ])
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estoque insuficiente para os seguintes produtos: {detalhes}"
        )
    
    # Processar baixa de estoque para cada item
    try:
        for item in db_orcamento.itens:
            StockService.update_stock_transactionally(
                db=db,
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                tipo_movimentacao='SAIDA',
                usuario_id=usuario_id,
                empresa_id=empresa_id,
                origem='VENDA',
                observacao=f"Orçamento #{orcamento_id} confirmado"
            )
        
        # Atualizar status do orçamento para FINALIZADO
        db_orcamento.status = 'FINALIZADO'
        db.commit()
        db.refresh(db_orcamento)
        
        return get_orcamento_by_id(db, orcamento_id)
        
    except HTTPException:
        # Re-raise HTTP exceptions (como estoque insuficiente)
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao confirmar orçamento: {str(e)}"
        )