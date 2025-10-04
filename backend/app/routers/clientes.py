# /backend/app/routers/clientes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..db.connection import get_db
from ..dependencies import get_current_user
from ..db import models
from ..schemas import cliente as schemas_cliente
from ..schemas import orcamento as schemas_orcamento
from ..crud import cliente as crud_cliente

router = APIRouter(prefix="/clientes", tags=["clientes"])

@router.post("/", response_model=schemas_cliente.Cliente)
@router.post("", response_model=schemas_cliente.Cliente)  # Rota sem barra final
def create_cliente(
    cliente_req: schemas_cliente.ClienteCreateRequest,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria um novo cliente a partir de uma requisição do frontend."""
    
    endereco_str = None
    if cliente_req.endereco:
        endereco = cliente_req.endereco
        endereco_parts = [
            endereco.logradouro,
            endereco.numero,
            endereco.complemento,
            endereco.bairro,
            endereco.cidade,
            endereco.estado,
            endereco.cep
        ]
        endereco_str = ", ".join(filter(None, endereco_parts))

    cliente_data = schemas_cliente.ClienteCreate(
        razao_social=cliente_req.nome,
        cnpj=cliente_req.cpf_cnpj,
        email=cliente_req.email,
        telefone=cliente_req.telefone,
        endereco=endereco_str,
        empresa_vinculada=cliente_req.empresa_vinculada or schemas_cliente.EmpresaVinculada.HIGIPLAS,
    )
    
    return crud_cliente.create_cliente(db, cliente_data, current_user.empresa_id)

@router.get("/", response_model=List[schemas_cliente.Cliente])
@router.get("", response_model=List[schemas_cliente.Cliente])  # Rota sem barra final
def list_clientes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista todos os clientes da empresa."""
    return crud_cliente.get_clientes(db, current_user.empresa_id, skip, limit)

@router.get("/search")
def search_clientes(
    q: str,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Busca clientes por nome ou CNPJ."""
    return crud_cliente.search_clientes(db, current_user.empresa_id, q)

@router.get("/{cliente_id}", response_model=schemas_cliente.Cliente)
def get_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Busca um cliente específico (dados básicos apenas)."""
    cliente = crud_cliente.get_cliente_by_id(db, cliente_id, current_user.empresa_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )
    return cliente

@router.put("/{cliente_id}", response_model=schemas_cliente.Cliente)
@router.put("/{cliente_id}/", response_model=schemas_cliente.Cliente)  # Rota com barra final
def update_cliente(
    cliente_id: int,
    cliente_update: schemas_cliente.ClienteUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza um cliente."""
    return crud_cliente.update_cliente(db, cliente_id, cliente_update, current_user.empresa_id)

@router.delete("/{cliente_id}")
@router.delete("/{cliente_id}/")  # Rota com barra final
def delete_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Exclui um cliente."""
    return crud_cliente.delete_cliente(db, cliente_id, current_user.empresa_id)

@router.get("/{cliente_id}/resumo-vendas", response_model=List[schemas_orcamento.ResumoVendasCliente])
def get_resumo_vendas_cliente(
    cliente_id: int,
    meses: int = 3,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Retorna resumo das vendas dos últimos N meses do cliente."""
    return crud_cliente.get_resumo_vendas_cliente(db, cliente_id, current_user.empresa_id, meses)

@router.get("/{cliente_id}/ultima-venda")
def get_ultima_venda_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Retorna a última venda do cliente."""
    return crud_cliente.get_ultima_venda_cliente(db, cliente_id, current_user.empresa_id)

@router.get("/{cliente_id}/historico-pagamentos", response_model=List[schemas_cliente.HistoricoPagamento])
def get_historico_pagamentos(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Lista o histórico de pagamentos de um cliente."""
    return crud_cliente.get_historico_pagamentos_cliente(db, cliente_id, current_user.empresa_id)

@router.post("/historico-pagamentos", response_model=schemas_cliente.HistoricoPagamento)
def create_historico_pagamento(
    historico: schemas_cliente.HistoricoPagamentoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria um novo registro de histórico de pagamento."""
    # Verifica se o cliente pertence à empresa do usuário
    cliente = crud_cliente.get_cliente_by_id(db, historico.cliente_id, current_user.empresa_id)
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado."
        )
    
    return crud_cliente.create_historico_pagamento(db, historico)

@router.put("/historico-pagamentos/{historico_id}", response_model=schemas_cliente.HistoricoPagamento)
def update_historico_pagamento(
    historico_id: int,
    historico_update: schemas_cliente.HistoricoPagamentoUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Atualiza um registro de histórico de pagamento."""
    return crud_cliente.update_historico_pagamento(db, historico_id, historico_update, current_user.empresa_id)