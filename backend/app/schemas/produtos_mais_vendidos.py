# /backend/app/schemas/produtos_mais_vendidos.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ProdutoMaisVendidoBase(BaseModel):
    produto_id: int
    ano: int
    total_vendido: float
    valor_total_vendas: float
    numero_orcamentos: int

class ProdutoMaisVendidoCreate(ProdutoMaisVendidoBase):
    pass

class ProdutoMaisVendidoUpdate(BaseModel):
    total_vendido: Optional[float] = None
    valor_total_vendas: Optional[float] = None
    numero_orcamentos: Optional[int] = None

class ProdutoMaisVendido(ProdutoMaisVendidoBase):
    id: int
    data_criacao: datetime
    empresa_id: int
    
    model_config = ConfigDict(from_attributes=True)

# Schema para resposta da API de produtos mais vendidos
class ProdutoVendidoDetalhado(BaseModel):
    id: int
    nome: str
    codigo: str
    preco_venda: float
    total_vendido: float
    valor_total_vendas: float
    numero_orcamentos: int
    
    model_config = ConfigDict(from_attributes=True)