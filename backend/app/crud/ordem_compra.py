from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from ..db import models
from ..schemas import ordem_compra as schemas_oc, movimentacao_estoque as schemas_mov
from . import movimentacao_estoque as crud_movimentacao
from datetime import datetime

def create_ordem_compra(db: Session, ordem_in: schemas_oc.OrdemDeCompraCreate, usuario_id: int):
    try:
        db_ordem = models.OrdemDeCompra(
            fornecedor_id=ordem_in.fornecedor_id if ordem_in.fornecedor_id else None,
            usuario_id=usuario_id,
            status="RASCUNHO"
        )
        db.add(db_ordem)
        db.flush()  # Para obter o ID da ordem antes do commit

        for item_in in ordem_in.itens:
            db_item = models.OrdemDeCompraItem(
                ordem_id=db_ordem.id,
                produto_id=item_in.produto_id,
                quantidade_solicitada=item_in.quantidade_solicitada,
                custo_unitario_registrado=item_in.custo_unitario_registrado
            )
            db.add(db_item)
        
        db.commit()
        db.refresh(db_ordem)
        return db_ordem
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno ao criar ordem de compra: {e}")

def get_ordens_compra(db: Session, empresa_id: int):
    return db.query(models.OrdemDeCompra).join(models.OrdemDeCompra.usuario).filter(
        models.Usuario.empresa_id == empresa_id
    ).options(
        joinedload(models.OrdemDeCompra.fornecedor),
        joinedload(models.OrdemDeCompra.itens).joinedload(models.OrdemDeCompraItem.produto)
    ).order_by(models.OrdemDeCompra.data_criacao.desc()).all()

def get_ordem_compra_by_id(db: Session, ordem_id: int, empresa_id: int):
    """Busca uma ordem de compra por ID, garantindo que pertence à empresa"""
    ordem = db.query(models.OrdemDeCompra).join(models.OrdemDeCompra.usuario).filter(
        models.OrdemDeCompra.id == ordem_id,
        models.Usuario.empresa_id == empresa_id
    ).options(
        joinedload(models.OrdemDeCompra.fornecedor),
        joinedload(models.OrdemDeCompra.itens).joinedload(models.OrdemDeCompraItem.produto),
        joinedload(models.OrdemDeCompra.usuario)
    ).first()
    
    if not ordem:
        raise HTTPException(status_code=404, detail="Ordem de Compra não encontrada.")
    return ordem

def update_ordem_compra(db: Session, ordem_id: int, ordem_update: schemas_oc.OrdemDeCompraUpdate, empresa_id: int):
    """Atualiza uma ordem de compra"""
    db_ordem = get_ordem_compra_by_id(db, ordem_id, empresa_id)
    
    # Não permite editar OC já recebida
    if db_ordem.status == "RECEBIDA":
        raise HTTPException(status_code=400, detail="Não é possível editar uma Ordem de Compra já recebida.")
    
    try:
        # Atualizar fornecedor se fornecido
        if ordem_update.fornecedor_id is not None:
            db_ordem.fornecedor_id = ordem_update.fornecedor_id
        
        # Atualizar itens se fornecido
        if ordem_update.itens is not None:
            # Deletar itens antigos
            for item in db_ordem.itens:
                db.delete(item)
            
            # Adicionar novos itens
            for item_in in ordem_update.itens:
                db_item = models.OrdemDeCompraItem(
                    ordem_id=db_ordem.id,
                    produto_id=item_in.produto_id,
                    quantidade_solicitada=item_in.quantidade_solicitada,
                    custo_unitario_registrado=item_in.custo_unitario_registrado
                )
                db.add(db_item)
        
        db.commit()
        db.refresh(db_ordem)
        return db_ordem
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar ordem de compra: {e}")

def delete_ordem_compra(db: Session, ordem_id: int, empresa_id: int):
    """Deleta uma ordem de compra"""
    db_ordem = get_ordem_compra_by_id(db, ordem_id, empresa_id)
    
    # Não permite deletar OC já recebida
    if db_ordem.status == "RECEBIDA":
        raise HTTPException(status_code=400, detail="Não é possível deletar uma Ordem de Compra já recebida.")
    
    try:
        db.delete(db_ordem)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar ordem de compra: {e}")

def receber_ordem_compra(db: Session, ordem_id: int, usuario_id: int, empresa_id: int):
    # Busca a OC garantindo que ela pertence à empresa do usuário
    db_ordem = db.query(models.OrdemDeCompra).join(models.OrdemDeCompra.usuario).filter(
        models.OrdemDeCompra.id == ordem_id,
        models.Usuario.empresa_id == empresa_id
    ).first()

    if not db_ordem:
        raise HTTPException(status_code=404, detail="Ordem de Compra não encontrada.")
    if db_ordem.status == "RECEBIDA":
        raise HTTPException(status_code=400, detail="Esta Ordem de Compra já foi recebida.")

    try:
        # Itera sobre os itens da OC para dar entrada no estoque
        for item in db_ordem.itens:
            # 1. Cria a movimentação de ENTRADA
            movimentacao_data = schemas_mov.MovimentacaoEstoqueCreate(
                produto_id=item.produto_id,
                tipo_movimentacao="ENTRADA",
                quantidade=item.quantidade_solicitada,
                observacao=f"Entrada referente à Ordem de Compra ID: {ordem_id}"
            )
            # A função create_movimentacao_estoque já é transacional e segura
            crud_movimentacao.create_movimentacao_estoque(
                db=db,
                movimentacao=movimentacao_data,
                usuario_id=usuario_id,
                empresa_id=empresa_id
            )
            
            # 2. Atualiza o preço de custo do produto
            produto_a_atualizar = db.query(models.Produto).filter(models.Produto.id == item.produto_id).first()
            if produto_a_atualizar:
                produto_a_atualizar.preco_custo = item.custo_unitario_registrado
        
        # 3. Atualiza o status e a data da OC
        db_ordem.status = "RECEBIDA"
        db_ordem.data_recebimento = datetime.now()
        
        db.commit()
        db.refresh(db_ordem)
        return db_ordem
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao processar recebimento: {e}")