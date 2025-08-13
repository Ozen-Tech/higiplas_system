# /backend/app/schemas/orcamento.py

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date, datetime

from .produto import Produto as SchemaProduto
from .usuario import Usuario as SchemaUsuario
from .cliente import Cliente as SchemaCliente

# Item do Orçamento
class OrcamentoItemBase(BaseModel):
    produto_id: int
    quantidade: int

class OrcamentoItemCreate(OrcamentoItemBase):
    pass

class OrcamentoItem(OrcamentoItemBase):
    id: int
    preco_unitario_congelado: float
    produto: SchemaProduto # Inclui os dados do produto no retorno

    model_config = ConfigDict(from_attributes=True)

# Orçamento Completo
class OrcamentoBase(BaseModel):
    data_validade: Optional[date] = None
    condicao_pagamento: str
    preco_minimo: Optional[float] = None
    preco_maximo: Optional[float] = None
    numero_nf: Optional[str] = None

class OrcamentoCreate(OrcamentoBase):
    cliente_id: Optional[int] = None
    nome_cliente: Optional[str] = None  # Para compatibilidade com código existente
    itens: List[OrcamentoItemCreate]

class OrcamentoUpdate(BaseModel):
    data_validade: Optional[date] = None
    condicao_pagamento: Optional[str] = None
    preco_minimo: Optional[float] = None
    preco_maximo: Optional[float] = None
    numero_nf: Optional[str] = None
    status: Optional[str] = None

class Orcamento(BaseModel):
    id: int
    status: str
    data_criacao: datetime
    data_validade: Optional[date] = None
    condicao_pagamento: Optional[str] = None  # Temporariamente opcional para corrigir erro 500
    preco_minimo: Optional[float] = None
    preco_maximo: Optional[float] = None
    numero_nf: Optional[str] = None
    usuario: SchemaUsuario
    cliente: Optional[SchemaCliente] = None  # Temporariamente opcional para corrigir erro 500
    itens: List[OrcamentoItem]

    model_config = ConfigDict(from_attributes=True)

# Schema para resumo de vendas do cliente
class ResumoVendasCliente(BaseModel):
    mes: str
    ano: int
    total_vendas: float
    quantidade_orcamentos: int
    
    model_config = ConfigDict(from_attributes=True)