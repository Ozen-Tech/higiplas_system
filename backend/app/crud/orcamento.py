from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, extract, and_
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime, date
from ..db import models
from ..schemas import orcamento as schemas_orcamento
from ..crud import movimentacao_estoque as crud_movimentacao
from ..schemas import movimentacao_estoque as schemas_movimentacao


def create_orcamento(db: Session, orcamento: schemas_orcamento.OrcamentoCreate, usuario_id: int, empresa_id: int):
    try:
        # Verifica se o cliente existe e pertence à empresa
        cliente = db.query(models.Cliente).filter(
            models.Cliente.id == orcamento.cliente_id,
            models.Cliente.empresa_id == empresa_id
        ).first()
        
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado ou não pertence a esta empresa."
            )
        
        # 1. Cria o registro principal do orçamento
        db_orcamento = models.Orcamento(
            cliente_id=orcamento.cliente_id,
            data_validade=orcamento.data_validade,
            condicao_pagamento=orcamento.condicao_pagamento,
            preco_minimo=orcamento.preco_minimo,
            preco_maximo=orcamento.preco_maximo,
            numero_nf=orcamento.numero_nf,
            usuario_id=usuario_id,
        )
        db.add(db_orcamento)
        db.flush()

        # 2. Itera sobre os itens, verifica o estoque e cria os registros de item
        for item_in in orcamento.itens:
            produto = db.query(models.Produto).filter(
                models.Produto.id == item_in.produto_id,
                models.Produto.empresa_id == empresa_id
            ).first()
            
            if not produto:
                raise HTTPException(status_code=404, detail=f"Produto com ID {item_in.produto_id} não encontrado.")
            if produto.quantidade_em_estoque < item_in.quantidade:
                raise HTTPException(status_code=400, detail=f"Estoque insuficiente para '{produto.nome}'. Disponível: {produto.quantidade_em_estoque}, Solicitado: {item_in.quantidade}")
            
            db_item = models.OrcamentoItem(
                orcamento_id=db_orcamento.id,
                produto_id=item_in.produto_id,
                quantidade=item_in.quantidade,
                preco_unitario_congelado=produto.preco_venda
            )
            db.add(db_item)

        db.commit()
        db.refresh(db_orcamento)
        
        usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
        if usuario:
            usuario.xp += 10
            if usuario.xp >= (usuario.level * 100):
                usuario.level += 1
                usuario.xp = 0
            db.commit()
        
        return db_orcamento

    except HTTPException as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno ao criar orçamento: {e}")

def get_orcamentos_by_user(db: Session, usuario_id: int):
    """Busca todos os orçamentos criados por um usuário específico."""
    return db.query(models.Orcamento).options(
        joinedload(models.Orcamento.cliente),
        joinedload(models.Orcamento.usuario),
        joinedload(models.Orcamento.itens)
    ).filter(
        models.Orcamento.usuario_id == usuario_id
    ).order_by(
        models.Orcamento.data_criacao.desc()
    ).all()

def get_orcamentos_by_empresa(db: Session, empresa_id: int, skip: int = 0, limit: int = 100):
    """Busca todos os orçamentos de uma empresa (para dashboard de admins)."""
    return db.query(models.Orcamento).join(
        models.Usuario
    ).options(
        joinedload(models.Orcamento.cliente),
        joinedload(models.Orcamento.usuario),
        joinedload(models.Orcamento.itens)
    ).filter(
        models.Usuario.empresa_id == empresa_id
    ).order_by(
        models.Orcamento.data_criacao.desc()
    ).offset(skip).limit(limit).all()

def get_orcamento_by_id(db: Session, orcamento_id: int, usuario_id: int = None, empresa_id: int = None):
    """Busca um único orçamento pelo ID."""
    query = db.query(models.Orcamento).options(
        joinedload(models.Orcamento.cliente),
        joinedload(models.Orcamento.usuario),
        joinedload(models.Orcamento.itens).joinedload(models.OrcamentoItem.produto)
    ).filter(models.Orcamento.id == orcamento_id)
    
    if usuario_id:
        query = query.filter(models.Orcamento.usuario_id == usuario_id)
    elif empresa_id:
        query = query.join(models.Usuario).filter(models.Usuario.empresa_id == empresa_id)
    
    return query.first()

# --- NOVA FUNÇÃO PARA FINALIZAR O ORÇAMENTO ---
def finalizar_orcamento(db: Session, orcamento_id: int, usuario_id: int, empresa_id: int):
    """
    Finaliza um orçamento, atualizando seu status e dando baixa no estoque dos produtos.
    """
    # 1. Busca o orçamento, garantindo que ele pertence à empresa do usuário.
    #    O `joinedload` já carrega os itens para evitar novas queries.
    db_orcamento = db.query(models.Orcamento).filter(
        models.Orcamento.id == orcamento_id,
        # Verifica se o orçamento pertence a um usuário da empresa correta
        models.Orcamento.usuario.has(empresa_id=empresa_id) 
    ).first()

    if not db_orcamento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Orçamento não encontrado ou não pertence a esta empresa.")

    # 2. Verifica se o orçamento já não foi finalizado.
    if db_orcamento.status == "FINALIZADO":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este orçamento já foi finalizado.")

    # 3. Itera sobre os itens e dá baixa no estoque.
    #    A função `create_movimentacao_estoque` já é transacional e segura.
    for item in db_orcamento.itens:
        # Verifica se há estoque suficiente ANTES de tentar a baixa.
        if item.produto.quantidade_em_estoque < item.quantidade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente para o produto '{item.produto.nome}'. Restam apenas {item.produto.quantidade_em_estoque}."
            )
            
        movimentacao_data = schemas_movimentacao.MovimentacaoEstoqueCreate(
            produto_id=item.produto_id,
            tipo_movimentacao="SAIDA",
            quantidade=item.quantidade,
            observacao=f"Saída referente ao Orçamento ID: {db_orcamento.id} para o cliente: {db_orcamento.cliente.razao_social}"
        )
        # Reutilizamos a função de movimentação que já existe e é segura!
        crud_movimentacao.create_movimentacao_estoque(
            db=db,
            movimentacao=movimentacao_data,
            usuario_id=usuario_id,
            empresa_id=empresa_id
        )

    # 4. Atualiza o status do orçamento e do usuário.
    db_orcamento.status = "FINALIZADO"
    
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if usuario:
        usuario.xp += 25 # 25 XP por finalizar um orçamento/venda
        if usuario.xp >= (usuario.level * 100):
            usuario.level += 1
            usuario.xp = 0

    # 5. Salva todas as alterações no banco de dados.
    db.commit()
    db.refresh(db_orcamento)
    
    return db_orcamento