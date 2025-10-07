# /backend/app/schemas/orcamento.py

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

# Importa os outros schemas que serão usados aqui
from .produto import Produto
from .usuario import Usuario
from .cliente_v2 import ClienteResponse

# --- Itens do Orçamento ---

class OrcamentoItemBase(BaseModel):
    produto_id: int
    quantidade: int
    
class OrcamentoItemCreate(OrcamentoItemBase):
    # O preço que o vendedor define na hora
    preco_unitario: float

class OrcamentoItem(OrcamentoItemBase):
    id: int
    # O preço que foi salvo no banco no momento da criação
    preco_unitario_congelado: float
    produto: Produto # Mostra os dados completos do produto

    model_config = ConfigDict(from_attributes=True)


# --- Orçamento Principal ---

class OrcamentoBase(BaseModel):
    cliente_id: int
    condicao_pagamento: str
    status: str = "RASCUNHO"

class OrcamentoCreate(OrcamentoBase):
    itens: List[OrcamentoItemCreate]

class Orcamento(OrcamentoBase):
    id: int
    data_criacao: datetime
    
    # Relações com outros objetos
    usuario: Usuario
    cliente: ClienteResponse
    itens: List[OrcamentoItem]

    model_config = ConfigDict(from_attributes=True)