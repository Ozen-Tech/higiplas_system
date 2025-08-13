# /backend/app/crud/cliente.py

from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime, date

from app.db import models
from app.schemas import cliente as schemas_cliente

def create_cliente(db: Session, cliente: schemas_cliente.ClienteCreate, empresa_id: int):
    """Cria um novo cliente."""
    # Verifica se já existe um cliente com o mesmo CNPJ na empresa
    if cliente.cnpj:
        existing_cliente = db.query(models.Cliente).filter(
            models.Cliente.cnpj == cliente.cnpj,
            models.Cliente.empresa_id == empresa_id
        ).first()
        if existing_cliente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um cliente com este CNPJ."
            )
    
    db_cliente = models.Cliente(
        **cliente.model_dump(),
        empresa_id=empresa_id
    )
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

def get_clientes(db: Session, empresa_id: int, skip: int = 0, limit: int = 100):
    """Lista todos os clientes da empresa."""
    return db.query(models.Cliente).filter(
        models.Cliente.empresa_id == empresa_id
    ).offset(skip).limit(limit).all()

def get_cliente_by_id(db: Session, cliente_id: int, empresa_id: int):
    """Busca um cliente específico por ID."""
    try:
        # Busca apenas os dados básicos do cliente, sem relacionamentos
        cliente = db.query(models.Cliente).filter(
            models.Cliente.id == cliente_id,
            models.Cliente.empresa_id == empresa_id
        ).first()
        
        return cliente
        
    except Exception as e:
        print(f"Erro em get_cliente_by_id: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar cliente: {str(e)}"
        )

def get_cliente_by_cnpj(db: Session, cnpj: str, empresa_id: int):
    """Busca um cliente por CNPJ."""
    return db.query(models.Cliente).filter(
        models.Cliente.cnpj == cnpj,
        models.Cliente.empresa_id == empresa_id
    ).first()

def search_clientes(db: Session, empresa_id: int, search_term: str):
    """Busca clientes por nome ou CNPJ."""
    return db.query(models.Cliente).filter(
        models.Cliente.empresa_id == empresa_id,
        models.Cliente.razao_social.ilike(f"%{search_term}%") |
        models.Cliente.cnpj.ilike(f"%{search_term}%")
    ).all()

def update_cliente(db: Session, cliente_id: int, cliente_update: schemas_cliente.ClienteUpdate, empresa_id: int):
    """Atualiza um cliente."""
    db_cliente = get_cliente_by_id(db, cliente_id, empresa_id)
    if not db_cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )
    
    # Verifica CNPJ duplicado se estiver sendo alterado
    if cliente_update.cnpj and cliente_update.cnpj != db_cliente.cnpj:
        existing_cliente = get_cliente_by_cnpj(db, cliente_update.cnpj, empresa_id)
        if existing_cliente and existing_cliente.id != cliente_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um cliente com este CNPJ."
            )
    
    update_data = cliente_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_cliente, field, value)
    
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

def delete_cliente(db: Session, cliente_id: int, empresa_id: int):
    """Exclui um cliente."""
    try:
        # Busca o cliente diretamente sem usar get_cliente_by_id para evitar problemas de relacionamento
        db_cliente = db.query(models.Cliente).filter(
            models.Cliente.id == cliente_id,
            models.Cliente.empresa_id == empresa_id
        ).first()
        
        if not db_cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente não encontrado."
            )
        
        # Exclui manualmente os registros relacionados para evitar problemas de cascade
        # Exclui histórico de pagamentos
        db.query(models.HistoricoPagamento).filter(
            models.HistoricoPagamento.cliente_id == cliente_id
        ).delete(synchronize_session=False)
        
        # Exclui orçamentos e seus itens (se houver)
        orcamentos = db.query(models.Orcamento).filter(
            models.Orcamento.cliente_id == cliente_id
        ).all()
        
        for orcamento in orcamentos:
            # Exclui itens do orçamento
            db.query(models.OrcamentoItem).filter(
                models.OrcamentoItem.orcamento_id == orcamento.id
            ).delete(synchronize_session=False)
            
            # Exclui o orçamento
            db.delete(orcamento)
        
        # Agora exclui o cliente
        db.delete(db_cliente)
        db.commit()
        return {"message": "Cliente excluído com sucesso"}
        
    except HTTPException:
        # Re-raise HTTPExceptions (como 404)
        raise
    except Exception as e:
        db.rollback()
        print(f"Erro ao excluir cliente: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao excluir cliente: {str(e)}"
        )

def get_resumo_vendas_cliente(db: Session, cliente_id: int, empresa_id: int, meses: int = 3):
    """Retorna resumo das vendas dos últimos N meses do cliente."""
    # Verifica se o cliente existe e pertence à empresa
    cliente = get_cliente_by_id(db, cliente_id, empresa_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )
    
    # Calcula a data de início (N meses atrás)
    data_inicio = datetime.now().replace(day=1)
    for _ in range(meses - 1):
        if data_inicio.month == 1:
            data_inicio = data_inicio.replace(year=data_inicio.year - 1, month=12)
        else:
            data_inicio = data_inicio.replace(month=data_inicio.month - 1)
    
    # Busca orçamentos finalizados do cliente nos últimos meses
    resumo = db.query(
        extract('month', models.Orcamento.data_criacao).label('mes'),
        extract('year', models.Orcamento.data_criacao).label('ano'),
        func.sum(
            models.OrcamentoItem.quantidade * models.OrcamentoItem.preco_unitario_congelado
        ).label('total_vendas'),
        func.count(models.Orcamento.id).label('quantidade_orcamentos')
    ).join(
        models.OrcamentoItem
    ).filter(
        models.Orcamento.cliente_id == cliente_id,
        models.Orcamento.status == 'FINALIZADO',
        models.Orcamento.data_criacao >= data_inicio
    ).group_by(
        extract('year', models.Orcamento.data_criacao),
        extract('month', models.Orcamento.data_criacao)
    ).order_by(
        extract('year', models.Orcamento.data_criacao).desc(),
        extract('month', models.Orcamento.data_criacao).desc()
    ).all()
    
    return resumo

def get_ultima_venda_cliente(db: Session, cliente_id: int, empresa_id: int):
    """Retorna a última venda (orçamento finalizado) do cliente."""
    return db.query(models.Orcamento).filter(
        models.Orcamento.cliente_id == cliente_id,
        models.Orcamento.status == 'FINALIZADO'
    ).order_by(models.Orcamento.data_criacao.desc()).first()

# CRUD para Histórico de Pagamentos
def create_historico_pagamento(db: Session, historico: schemas_cliente.HistoricoPagamentoCreate):
    """Cria um novo registro de histórico de pagamento."""
    db_historico = models.HistoricoPagamento(**historico.model_dump())
    db.add(db_historico)
    db.commit()
    db.refresh(db_historico)
    return db_historico

def get_historico_pagamentos_cliente(db: Session, cliente_id: int, empresa_id: int):
    """Lista o histórico de pagamentos de um cliente."""
    # Verifica se o cliente pertence à empresa - busca direta para evitar problemas de relacionamento
    db_cliente = db.query(models.Cliente).filter(
        models.Cliente.id == cliente_id,
        models.Cliente.empresa_id == empresa_id
    ).first()
    
    if not db_cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )
    
    # Busca histórico sem ordenação para evitar problemas com colunas inexistentes
    try:
        return db.query(models.HistoricoPagamento).filter(
            models.HistoricoPagamento.cliente_id == cliente_id
        ).order_by(models.HistoricoPagamento.id.desc()).all()
    except Exception as e:
        # Fallback: retorna sem ordenação se houver erro
        return db.query(models.HistoricoPagamento).filter(
            models.HistoricoPagamento.cliente_id == cliente_id
        ).all()

def update_historico_pagamento(db: Session, historico_id: int, historico_update: schemas_cliente.HistoricoPagamentoUpdate, empresa_id: int):
    """Atualiza um registro de histórico de pagamento."""
    db_historico = db.query(models.HistoricoPagamento).join(
        models.Cliente
    ).filter(
        models.HistoricoPagamento.id == historico_id,
        models.Cliente.empresa_id == empresa_id
    ).first()
    
    if not db_historico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Histórico de pagamento não encontrado."
        )
    
    update_data = historico_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_historico, field, value)
    
    db.commit()
    db.refresh(db_historico)
    return db_historico