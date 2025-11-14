
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from .produto import Produto
from .fornecedor import Fornecedor

# --- Itens da Ordem de Compra ---
class OrdemDeCompraItemBase(BaseModel):
    produto_id: int
    quantidade_solicitada: int
    custo_unitario_registrado: float

class OrdemDeCompraItemCreate(OrdemDeCompraItemBase):
    pass

class OrdemDeCompraItem(OrdemDeCompraItemBase):
    id: int
    produto: Produto

    model_config = ConfigDict(from_attributes=True)

# --- Ordem de Compra Principal ---
class OrdemDeCompraBase(BaseModel):
    fornecedor_id: Optional[int] = None

class OrdemDeCompraCreate(OrdemDeCompraBase):
    itens: List[OrdemDeCompraItemCreate]

class OrdemDeCompra(OrdemDeCompraBase):
    id: int
    usuario_id: int
    status: str
    data_criacao: datetime
    data_recebimento: Optional[datetime] = None
    fornecedor: Optional[Fornecedor] = None
    itens: List[OrdemDeCompraItem]

    model_config = ConfigDict(from_attributes=True)