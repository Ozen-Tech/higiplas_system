# backend/app/schemas/produto.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date

# Schema base com os campos comuns a todos os outros
class ProdutoBase(BaseModel):
    nome: str
    codigo: str
    categoria: str
    descricao: Optional[str] = None
    preco_custo: Optional[float] = None
    preco_venda: float
    unidade_medida: str
    estoque_minimo: Optional[int] = 0

# Schema para criação de um produto (herda do base)
class ProdutoCreate(ProdutoBase):
    data_validade: Optional[date] = None
    quantidade_em_estoque: Optional[int] = 0
    
# Schema para atualização (TODOS os campos são opcionais)
class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    codigo: Optional[str] = None
    categoria: Optional[str] = None
    descricao: Optional[str] = None
    preco_custo: Optional[float] = None
    preco_venda: Optional[float] = None
    unidade_medida: Optional[str] = None
    estoque_minimo: Optional[int] = None
    data_validade: Optional[date] = None

# Schema para leitura/retorno (inclui campos gerados pelo banco)
class Produto(ProdutoBase):
    id: int
    empresa_id: int
    quantidade_em_estoque: int
    data_validade: Optional[date] = None

    # Configuração para permitir que o Pydantic leia dados de um objeto SQLAlchemy
    model_config = ConfigDict(from_attributes=True)