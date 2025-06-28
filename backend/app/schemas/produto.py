from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ProdutoBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=255)
    codigo: Optional[str] = Field(None, max_length=50)
    empresa_id: int
    categoria_id: Optional[int] = None
    estoque_minimo: Optional[int] = 0
    unidade: Optional[str] = Field(None, max_length=20)

class ProdutoCreate(ProdutoBase):
    pass

class Produto(ProdutoBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True