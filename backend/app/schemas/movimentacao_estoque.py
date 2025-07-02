# backend/app/schemas/movimentacao_estoque.py

from pydantic import BaseModel, Field, validator, ConfigDict
from datetime import datetime
from typing import Optional

class MovimentacaoEstoqueBase(BaseModel):
    produto_id: int
    quantidade: int = Field(..., gt=0, description="A quantidade deve ser maior que zero.")
    observacao: Optional[str] = None

class MovimentacaoEstoqueCreate(MovimentacaoEstoqueBase):
    tipo_movimentacao: str

    @validator('tipo_movimentacao')
    def tipo_deve_ser_valido(cls, v):
        tipo_normalizado = v.upper()
        if tipo_normalizado not in ['ENTRADA', 'SAIDA']:
            raise ValueError("O tipo de movimentação deve ser 'ENTRADA' ou 'SAIDA'")
        return tipo_normalizado

class MovimentacaoEstoque(MovimentacaoEstoqueBase):
    id: int
    tipo_movimentacao: str
    usuario_id: int
    data_movimentacao: datetime
    
    model_config = ConfigDict(from_attributes=True)