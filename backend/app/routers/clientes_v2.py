# /backend/app/routers/clientes_v2.py
"""
Rotas simplificadas para clientes v2
Otimizado para vendedores de rua
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ..db.connection import get_db
from ..dependencies import get_current_user
from ..db import models
from ..schemas import cliente_v2 as schemas
from ..crud import cliente_v2 as crud

router = APIRouter(
    prefix="/clientes",  # Agora é o endpoint principal
    tags=["Clientes"]
)

# ============= CRIAÇÃO RÁPIDA =============

@router.post("/quick", response_model=schemas.ClienteResponse)
def create_cliente_quick(
    cliente: schemas.ClienteQuickCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Criação ultra-rápida de cliente - apenas nome e telefone
    Ideal para vendedor em campo
    """
    db_cliente = crud.create_cliente_quick(
        db=db,
        nome=cliente.nome,
        telefone=cliente.telefone,
        vendedor_id=current_user.id,
        empresa_id=current_user.empresa_id
    )
    
    # Adicionar campos extras para resposta
    response = schemas.ClienteResponse(
        id=db_cliente.id,
        nome=db_cliente.razao_social,
        telefone=db_cliente.telefone,
        tipo_pessoa="FISICA",
        vendedor_id=current_user.id,
        vendedor_nome=current_user.nome,
        empresa_id=current_user.empresa_id,
        status="ATIVO",
        criado_em=db_cliente.data_criacao or datetime.now()
    )
    
    return response

# ============= CRUD COMPLETO =============

@router.post("/", response_model=schemas.ClienteResponse)
def create_cliente(
    cliente: schemas.ClienteCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Criar cliente com todos os dados"""
    db_cliente = crud.create_cliente(
        db=db,
        cliente=cliente,
        vendedor_id=current_user.id,
        empresa_id=current_user.empresa_id
    )
    
    # Mapear para resposta
    response = schemas.ClienteResponse(
        id=db_cliente.id,
        nome=db_cliente.razao_social,
        telefone=db_cliente.telefone,
        tipo_pessoa=cliente.tipo_pessoa,
        cpf_cnpj=db_cliente.cnpj,
        bairro=cliente.bairro,
        cidade=cliente.cidade,
        observacoes=db_cliente.observacoes,
        referencia_localizacao=db_cliente.referencia_localizacao,
        vendedor_id=current_user.id,
        vendedor_nome=current_user.nome,
        empresa_id=current_user.empresa_id,
        status="ATIVO",
        criado_em=db_cliente.data_criacao or datetime.now()
    )
    
    return response

@router.get("/", response_model=List[schemas.ClienteList])
def list_clientes(
    search: Optional[str] = Query(None, description="Buscar por nome, telefone ou documento"),
    bairro: Optional[str] = Query(None, description="Filtrar por bairro"),
    cidade: Optional[str] = Query(None, description="Filtrar por cidade"),
    meus_clientes: bool = Query(False, description="Ver apenas meus clientes"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """
    Listar clientes com filtros
    - search: busca por nome, telefone ou documento
    - bairro/cidade: filtros de localização
    - meus_clientes: ver apenas clientes do vendedor logado
    """
    vendedor_id = current_user.id if meus_clientes else None
    
    clientes = crud.get_clientes(
        db=db,
        empresa_id=current_user.empresa_id,
        vendedor_id=vendedor_id,
        skip=skip,
        limit=limit,
        search=search,
        bairro=bairro,
        cidade=cidade
    )
    
    # Mapear para lista simplificada
    return [
        schemas.ClienteList(
            id=c.id,
            nome=c.razao_social,
            telefone=c.telefone or "",
            bairro=extract_bairro(c.endereco),
            cidade=extract_cidade(c.endereco),
            status="ATIVO" if c.status_pagamento == "BOM_PAGADOR" else "INATIVO",
            ultima_venda=None  # TODO: implementar
        ) for c in clientes
    ]

@router.get("/{cliente_id}", response_model=schemas.ClienteResponse)
def get_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Buscar cliente por ID"""
    db_cliente = crud.get_cliente_by_id(
        db=db,
        cliente_id=cliente_id,
        empresa_id=current_user.empresa_id
    )
    
    if not db_cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Mapear para resposta
    return schemas.ClienteResponse(
        id=db_cliente.id,
        nome=db_cliente.razao_social,
        telefone=db_cliente.telefone or "",
        tipo_pessoa="JURIDICA" if db_cliente.cnpj and len(db_cliente.cnpj) > 11 else "FISICA",
        cpf_cnpj=db_cliente.cnpj,
        bairro=extract_bairro(db_cliente.endereco),
        cidade=extract_cidade(db_cliente.endereco),
        observacoes=db_cliente.observacoes,
        referencia_localizacao=db_cliente.referencia_localizacao,
        vendedor_id=db_cliente.vendedor_id or current_user.id,
        vendedor_nome=None,  # TODO: buscar nome do vendedor
        empresa_id=db_cliente.empresa_id,
        status="ATIVO" if db_cliente.status_pagamento == "BOM_PAGADOR" else "INATIVO",
        criado_em=db_cliente.data_criacao or datetime.now()
    )

@router.put("/{cliente_id}", response_model=schemas.ClienteResponse)
def update_cliente(
    cliente_id: int,
    cliente_update: schemas.ClienteUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualizar cliente"""
    db_cliente = crud.update_cliente(
        db=db,
        cliente_id=cliente_id,
        cliente_update=cliente_update,
        empresa_id=current_user.empresa_id
    )
    
    if not db_cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Mapear para resposta
    return schemas.ClienteResponse(
        id=db_cliente.id,
        nome=db_cliente.razao_social,
        telefone=db_cliente.telefone or "",
        tipo_pessoa="JURIDICA" if db_cliente.cnpj and len(db_cliente.cnpj) > 11 else "FISICA",
        cpf_cnpj=db_cliente.cnpj,
        bairro=extract_bairro(db_cliente.endereco),
        cidade=extract_cidade(db_cliente.endereco),
        observacoes=db_cliente.observacoes,
        referencia_localizacao=db_cliente.referencia_localizacao,
        vendedor_id=db_cliente.vendedor_id or current_user.id,
        empresa_id=db_cliente.empresa_id,
        status="ATIVO",
        criado_em=db_cliente.data_criacao or datetime.now(),
        atualizado_em=db_cliente.atualizado_em
    )

@router.delete("/{cliente_id}")
def delete_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Deletar cliente (soft delete)"""
    success = crud.delete_cliente(
        db=db,
        cliente_id=cliente_id,
        empresa_id=current_user.empresa_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    return {"message": "Cliente removido com sucesso"}

# ============= FUNCIONALIDADES EXTRAS =============

@router.get("/{cliente_id}/stats", response_model=schemas.ClienteStats)
def get_cliente_stats(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Obter estatísticas de vendas do cliente"""
    stats = crud.get_cliente_stats(
        db=db,
        cliente_id=cliente_id,
        empresa_id=current_user.empresa_id
    )
    
    return schemas.ClienteStats(**stats)

@router.post("/bulk", response_model=dict)
def bulk_create_clientes(
    bulk_data: schemas.ClienteBulkCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Criar múltiplos clientes de uma vez"""
    result = crud.bulk_create_clientes(
        db=db,
        clientes=bulk_data.clientes,
        vendedor_id=current_user.id,
        empresa_id=current_user.empresa_id
    )
    
    if isinstance(result, dict):
        return result
    
    return {
        "criados": len(result),
        "clientes": [c.id for c in result]
    }

@router.get("/search/nearby")
def search_nearby_clientes(
    bairro: str = Query(..., description="Bairro para buscar"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Buscar clientes próximos (mesmo bairro)"""
    clientes = crud.get_clientes(
        db=db,
        empresa_id=current_user.empresa_id,
        bairro=bairro,
        limit=limit
    )
    
    return [
        {
            "id": c.id,
            "nome": c.razao_social,
            "telefone": c.telefone,
            "endereco": c.endereco,
            "referencia": c.referencia_localizacao
        } for c in clientes
    ]

# ============= HELPERS =============

def extract_bairro(endereco: Optional[str]) -> Optional[str]:
    """Extrair bairro do endereço"""
    if not endereco:
        return None
    parts = endereco.split(",")
    return parts[0].strip() if parts else None

def extract_cidade(endereco: Optional[str]) -> Optional[str]:
    """Extrair cidade do endereço"""
    if not endereco:
        return None
    parts = endereco.split(",")
    return parts[1].strip() if len(parts) > 1 else None

# Importar datetime que faltou
from datetime import datetime
