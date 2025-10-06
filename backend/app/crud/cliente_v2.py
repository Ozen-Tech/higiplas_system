# /backend/app/crud/cliente_v2.py
"""
CRUD simplificado para clientes v2
Focado em performance e praticidade
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.db import models
from app.schemas import cliente_v2 as schemas

def create_cliente_quick(
    db: Session, 
    nome: str, 
    telefone: str, 
    vendedor_id: int,
    empresa_id: int
) -> models.Cliente:
    """Criação ultra-rápida de cliente - apenas nome e telefone"""
    
    # Verificar se já existe cliente com mesmo telefone
    existing = db.query(models.Cliente).filter(
        models.Cliente.telefone == telefone,
        models.Cliente.empresa_id == empresa_id
    ).first()
    
    if existing:
        # Retorna o existente ao invés de erro
        return existing
    
    db_cliente = models.Cliente(
        razao_social=nome,  # Mapeando para o campo existente
        telefone=telefone,
        vendedor_id=vendedor_id,
        empresa_id=empresa_id,
        status_pagamento="BOM_PAGADOR",  # Default
        empresa_vinculada="HIGIPLAS",  # Default
        criado_em=datetime.now()
    )
    
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

def create_cliente(
    db: Session,
    cliente: schemas.ClienteCreate,
    vendedor_id: int,
    empresa_id: int
) -> models.Cliente:
    """Criar cliente completo"""
    
    # Verificar duplicados por telefone (se fornecido)
    if cliente.telefone:
        existing = db.query(models.Cliente).filter(
            models.Cliente.telefone == cliente.telefone,
            models.Cliente.empresa_id == empresa_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cliente já existe com este telefone: {cliente.nome}"
            )
    
    # Verificar duplicados por CPF/CNPJ apenas se fornecido
    if cliente.cpf_cnpj and cliente.cpf_cnpj.strip():
        existing = db.query(models.Cliente).filter(
            models.Cliente.cnpj == cliente.cpf_cnpj.strip(),
            models.Cliente.empresa_id == empresa_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cliente já existe com este documento"
            )
    
    # Criar endereço simplificado
    endereco = None
    if cliente.bairro or cliente.cidade:
        endereco = f"{cliente.bairro or ''}, {cliente.cidade or ''}".strip(", ")
    
    db_cliente = models.Cliente(
        razao_social=cliente.nome,
        telefone=cliente.telefone,
        cnpj=cliente.cpf_cnpj,
        endereco=endereco,
        observacoes=cliente.observacoes,
        referencia_localizacao=cliente.referencia_localizacao,
        vendedor_id=vendedor_id,
        empresa_id=empresa_id,
        status_pagamento="BOM_PAGADOR",
        empresa_vinculada="HIGIPLAS",
        criado_em=datetime.now()
    )
    
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

def get_clientes(
    db: Session,
    empresa_id: int,
    vendedor_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    bairro: Optional[str] = None,
    cidade: Optional[str] = None
) -> List[models.Cliente]:
    """Listar clientes com filtros opcionais"""
    
    query = db.query(models.Cliente).filter(
        models.Cliente.empresa_id == empresa_id
    )
    
    # Filtro por vendedor
    if vendedor_id:
        query = query.filter(models.Cliente.vendedor_id == vendedor_id)
    
    # Busca por termo
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.Cliente.razao_social.ilike(search_term),
                models.Cliente.telefone.like(search_term),
                models.Cliente.cnpj.like(search_term)
            )
        )
    
    # Filtro por localização
    if bairro:
        query = query.filter(models.Cliente.endereco.ilike(f"%{bairro}%"))
    
    if cidade:
        query = query.filter(models.Cliente.endereco.ilike(f"%{cidade}%"))
    
    return query.order_by(models.Cliente.razao_social).offset(skip).limit(limit).all()

def get_cliente_by_id(
    db: Session,
    cliente_id: int,
    empresa_id: int
) -> Optional[models.Cliente]:
    """Buscar cliente por ID"""
    return db.query(models.Cliente).filter(
        models.Cliente.id == cliente_id,
        models.Cliente.empresa_id == empresa_id
    ).first()

def update_cliente(
    db: Session,
    cliente_id: int,
    cliente_update: schemas.ClienteUpdate,
    empresa_id: int
) -> Optional[models.Cliente]:
    """Atualizar cliente"""
    
    db_cliente = get_cliente_by_id(db, cliente_id, empresa_id)
    if not db_cliente:
        return None
    
    # Mapear campos
    update_data = cliente_update.dict(exclude_unset=True)
    
    if 'nome' in update_data:
        db_cliente.razao_social = update_data['nome']
    
    if 'telefone' in update_data:
        db_cliente.telefone = update_data['telefone']
    
    if 'cpf_cnpj' in update_data:
        db_cliente.cnpj = update_data['cpf_cnpj']
    
    if 'observacoes' in update_data:
        db_cliente.observacoes = update_data['observacoes']
    
    if 'referencia_localizacao' in update_data:
        db_cliente.referencia_localizacao = update_data['referencia_localizacao']
    
    # Atualizar endereço
    if 'bairro' in update_data or 'cidade' in update_data:
        bairro = update_data.get('bairro', '')
        cidade = update_data.get('cidade', '')
        db_cliente.endereco = f"{bairro}, {cidade}".strip(", ") if (bairro or cidade) else None
    
    db_cliente.atualizado_em = datetime.now()
    
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

def delete_cliente(
    db: Session,
    cliente_id: int,
    empresa_id: int
) -> bool:
    """Deletar cliente (soft delete - apenas marca como inativo)"""
    
    db_cliente = get_cliente_by_id(db, cliente_id, empresa_id)
    if not db_cliente:
        return False
    
    # Soft delete - apenas marca como inativo
    db_cliente.status_pagamento = "MAU_PAGADOR"  # Temporário - mapear para status
    db_cliente.atualizado_em = datetime.now()
    
    db.commit()
    return True

def get_cliente_stats(
    db: Session,
    cliente_id: int,
    empresa_id: int
) -> dict:
    """Obter estatísticas do cliente"""
    
    # Buscar orçamentos do cliente
    orcamentos = db.query(models.Orcamento).filter(
        models.Orcamento.cliente_id == cliente_id,
        models.Orcamento.status == "FINALIZADO"
    ).all()
    
    total_vendido = 0
    produtos_contador = {}
    historico = []
    
    for orcamento in orcamentos:
        # Calcular total do orçamento
        total_orc = sum(
            item.quantidade * item.preco_unitario_congelado 
            for item in orcamento.itens
        )
        total_vendido += total_orc
        
        # Contar produtos
        for item in orcamento.itens:
            if item.produto_id not in produtos_contador:
                produtos_contador[item.produto_id] = {
                    'produto': item.produto.nome if item.produto else 'Produto',
                    'quantidade': 0,
                    'valor_total': 0
                }
            produtos_contador[item.produto_id]['quantidade'] += item.quantidade
            produtos_contador[item.produto_id]['valor_total'] += item.quantidade * item.preco_unitario_congelado
        
        # Adicionar ao histórico
        historico.append({
            'data': orcamento.data_criacao,
            'valor': total_orc,
            'id': orcamento.id
        })
    
    # Top produtos
    produtos_mais_comprados = sorted(
        produtos_contador.values(), 
        key=lambda x: x['valor_total'], 
        reverse=True
    )[:5]
    
    return {
        'total_orcamentos': len(orcamentos),
        'total_vendido': total_vendido,
        'ticket_medio': total_vendido / len(orcamentos) if orcamentos else 0,
        'produtos_mais_comprados': produtos_mais_comprados,
        'historico_vendas': sorted(historico, key=lambda x: x['data'], reverse=True)[:10]
    }

def bulk_create_clientes(
    db: Session,
    clientes: List[schemas.ClienteCreate],
    vendedor_id: int,
    empresa_id: int
) -> List[models.Cliente]:
    """Criar múltiplos clientes de uma vez"""
    
    created_clientes = []
    errors = []
    
    for cliente_data in clientes:
        try:
            db_cliente = create_cliente(db, cliente_data, vendedor_id, empresa_id)
            created_clientes.append(db_cliente)
        except HTTPException as e:
            errors.append({
                'cliente': cliente_data.nome,
                'erro': e.detail
            })
    
    if errors:
        return {
            'criados': len(created_clientes),
            'erros': errors,
            'clientes': created_clientes
        }
    
    return created_clientes
