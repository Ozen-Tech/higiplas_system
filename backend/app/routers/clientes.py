# /backend/app/routers/clientes.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import json

from ..db.connection import get_db
from ..dependencies import get_current_user
from ..db import models
from ..schemas import cliente as schemas_cliente
from ..schemas import orcamento as schemas_orcamento
from ..crud import cliente as crud_cliente

router = APIRouter(prefix="/clientes", tags=["clientes"])

# Schema alternativo para aceitar o formato do frontend
class ClienteCreateLegacy(BaseModel):
    """Schema para aceitar o formato legado do frontend"""
    razao_social: str
    cpf_cnpj: Optional[str] = None
    cnpj: Optional[str] = None  # Aceita tanto cnpj quanto cpf_cnpj
    email: Optional[str] = None
    telefone: Optional[str] = None
    tipo_pessoa: Optional[str] = None
    endereco: Optional[Any] = None  # Aceita string ou dict
    empresa_vinculada: Optional[str] = None
    status_pagamento: Optional[str] = None
    observacoes: Optional[str] = None

@router.post("/", response_model=schemas_cliente.Cliente)
@router.post("", response_model=schemas_cliente.Cliente)  # Rota sem barra final
def create_cliente(
    cliente_req: Dict[str, Any],  # Aceita qualquer formato JSON
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria um novo cliente - aceita formato novo ou legado do frontend."""
    
    # Detectar formato baseado nos campos recebidos
    if "nome" in cliente_req:
        # Formato novo (ClienteCreateRequest)
        endereco_str = None
        if cliente_req.get('endereco'):
            endereco = cliente_req['endereco']
            if isinstance(endereco, dict):
                endereco_parts = [
                    endereco.get('logradouro', ''),
                    endereco.get('numero', ''),
                    endereco.get('complemento', ''),
                    endereco.get('bairro', ''),
                    endereco.get('cidade', ''),
                    endereco.get('estado', ''),
                    endereco.get('cep', '')
                ]
                endereco_str = ", ".join(filter(None, endereco_parts))
            else:
                endereco_str = str(endereco)
        
        cliente_data = schemas_cliente.ClienteCreate(
            razao_social=cliente_req['nome'],
            cnpj=cliente_req.get('cpf_cnpj'),
            email=cliente_req.get('email'),
            telefone=cliente_req.get('telefone'),
            endereco=endereco_str,
            empresa_vinculada=cliente_req.get('empresa_vinculada') or schemas_cliente.EmpresaVinculada.HIGIPLAS,
        )
    
    elif "razao_social" in cliente_req:
        # Formato legado
        endereco_str = None
        if cliente_req.get('endereco'):
            if isinstance(cliente_req['endereco'], str):
                try:
                    # Se é string JSON, fazer parse
                    endereco_dict = json.loads(cliente_req['endereco'])
                except json.JSONDecodeError:
                    # Se não é JSON válido, usar como string simples
                    endereco_str = cliente_req['endereco']
                else:
                    # Montar endereço a partir do dict
                    endereco_parts = [
                        endereco_dict.get('logradouro', ''),
                        endereco_dict.get('numero', ''),
                        endereco_dict.get('complemento', ''),
                        endereco_dict.get('bairro', ''),
                        endereco_dict.get('cidade', ''),
                        endereco_dict.get('estado', ''),
                        endereco_dict.get('cep', '')
                    ]
                    endereco_str = ", ".join(filter(None, endereco_parts))
            elif isinstance(cliente_req['endereco'], dict):
                # Se já é dict, processar diretamente
                endereco_parts = [
                    cliente_req['endereco'].get('logradouro', ''),
                    cliente_req['endereco'].get('numero', ''),
                    cliente_req['endereco'].get('complemento', ''),
                    cliente_req['endereco'].get('bairro', ''),
                    cliente_req['endereco'].get('cidade', ''),
                    cliente_req['endereco'].get('estado', ''),
                    cliente_req['endereco'].get('cep', '')
                ]
                endereco_str = ", ".join(filter(None, endereco_parts))
        
        # Usar cnpj ou cpf_cnpj (o que vier preenchido)
        cnpj_final = cliente_req.get('cnpj') or cliente_req.get('cpf_cnpj')
        
        cliente_data = schemas_cliente.ClienteCreate(
            razao_social=cliente_req['razao_social'],
            cnpj=cnpj_final,
            email=cliente_req.get('email'),
            telefone=cliente_req.get('telefone'),
            endereco=endereco_str,
            empresa_vinculada=cliente_req.get('empresa_vinculada') or schemas_cliente.EmpresaVinculada.HIGIPLAS,
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="Formato de requisição inválido. Campo 'nome' ou 'razao_social' é obrigatório."
        )
    
    return crud_cliente.create_cliente(db, cliente_data, current_user.empresa_id)

@router.post("/legacy", response_model=schemas_cliente.Cliente)
@router.post("/legacy/", response_model=schemas_cliente.Cliente)  # Rota com barra final
def create_cliente_legacy(
    cliente_req: ClienteCreateLegacy,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_user)
):
    """Cria um novo cliente aceitando formato legado do frontend."""
    
    # Processar endereço - pode vir como string JSON ou dict
    endereco_str = None
    if cliente_req.endereco:
        if isinstance(cliente_req.endereco, str):
            try:
                # Se é string JSON, fazer parse
                endereco_dict = json.loads(cliente_req.endereco)
            except json.JSONDecodeError:
                # Se não é JSON válido, usar como string simples
                endereco_str = cliente_req.endereco
            else:
                # Montar endereço a partir do dict
                endereco_parts = [
                    endereco_dict.get('logradouro', ''),
                    endereco_dict.get('numero', ''),
                    endereco_dict.get('complemento', ''),
                    endereco_dict.get('bairro', ''),
                    endereco_dict.get('cidade', ''),
                    endereco_dict.get('estado', ''),
                    endereco_dict.get('cep', '')
                ]
                endereco_str = ", ".join(filter(None, endereco_parts))
        elif isinstance(cliente_req.endereco, dict):
            # Se já é dict, processar diretamente
            endereco_parts = [
                cliente_req.endereco.get('logradouro', ''),
                cliente_req.endereco.get('numero', ''),
                cliente_req.endereco.get('complemento', ''),
                cliente_req.endereco.get('bairro', ''),
                cliente_req.endereco.get('cidade', ''),
                cliente_req.endereco.get('estado', ''),
                cliente_req.endereco.get('cep', '')
            ]
            endereco_str = ", ".join(filter(None, endereco_parts))

    # Usar cnpj ou cpf_cnpj (o que vier preenchido)
    cnpj_final = cliente_req.cnpj or cliente_req.cpf_cnpj
    
    # Criar o objeto ClienteCreate com os dados convertidos
    cliente_data = schemas_cliente.ClienteCreate(
        razao_social=cliente_req.razao_social,
        cnpj=cnpj_final,
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