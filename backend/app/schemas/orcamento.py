# /backend/app/schemas/orcamento.py

from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date, datetime

from .produto import Produto as SchemaProduto
from .usuario import Usuario as SchemaUsuario

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
    nome_cliente: str
    data_validade: Optional[date] = None

class OrcamentoCreate(OrcamentoBase):
    itens: List[OrcamentoItemCreate]

class Orcamento(OrcamentoBase):
    id: int
    status: str
    data_criacao: datetime
    usuario: SchemaUsuario
    itens: List[OrcamentoItem]

    model_config = ConfigDict(from_attributes=True)